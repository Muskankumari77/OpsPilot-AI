"""
Dataset routes: upload (kicks off background processing), list, retrieve,
and a summary of row counts per domain table.

Upload requires Admin or Manager (Viewers are read-only per the spec).
"""
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_current_user, get_db, require_role
from app.core.exceptions import NotFoundError, ValidationError
from app.models.customer import Customer
from app.models.dataset import Dataset, DatasetStatus, DatasetType
from app.models.expense import Expense
from app.models.inventory import Inventory
from app.models.organization import OrganizationMember, Role
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User
from app.schemas.dataset import DatasetOut, DatasetSummaryOut
from app.services.data_ingestion_service import process_dataset

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@router.post("/upload", response_model=DatasetOut)
def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    dataset_type: DatasetType = Form(...),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("Only .csv, .xlsx, and .xls files are supported.")

    stored_filename = f"{uuid.uuid4().hex}{extension}"
    stored_path = os.path.join(UPLOAD_DIR, stored_filename)
    with open(stored_path, "wb") as out_file:
        out_file.write(file.file.read())

    dataset = Dataset(
        organization_id=membership.organization_id,
        uploaded_by_user_id=current_user.id,
        filename=file.filename or stored_filename,
        dataset_type=dataset_type,
        status=DatasetStatus.PROCESSING,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Runs after this response is returned — the upload endpoint doesn't
    # block on parsing/importing a potentially large file.
    background_tasks.add_task(process_dataset, dataset.id, stored_path)

    return dataset


@router.get("", response_model=list[DatasetOut])
def list_datasets(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return (
        db.query(Dataset)
        .filter(Dataset.organization_id == membership.organization_id)
        .order_by(Dataset.created_at.desc())
        .all()
    )


@router.get("/summary", response_model=DatasetSummaryOut)
def dataset_summary(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    org_id = membership.organization_id
    return DatasetSummaryOut(
        products=db.query(Product).filter(Product.organization_id == org_id).count(),
        customers=db.query(Customer).filter(Customer.organization_id == org_id).count(),
        sales=db.query(Sale).filter(Sale.organization_id == org_id).count(),
        inventory=db.query(Inventory).filter(Inventory.organization_id == org_id).count(),
        expenses=db.query(Expense).filter(Expense.organization_id == org_id).count(),
    )


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(
    dataset_id: int,
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.organization_id == membership.organization_id)
        .first()
    )
    if not dataset:
        raise NotFoundError("Dataset not found.")
    return dataset
