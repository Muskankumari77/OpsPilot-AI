from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, get_current_user, get_db, require_role
from app.models.organization import OrganizationMember, Role
from app.models.user import User
from app.schemas.knowledge_base import DocumentOut
from app.services import rag_service

router = APIRouter()


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    membership: OrganizationMember = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return rag_service.list_documents(db, membership.organization_id)


@router.post("/upload", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_role(Role.ADMIN, Role.MANAGER)),
    db: Session = Depends(get_db),
):
    raw_bytes = file.file.read()
    document = rag_service.ingest_document(
        db, membership.organization_id, current_user.id, file.filename or "document.txt", raw_bytes
    )
    return DocumentOut(
        id=document.id, filename=document.filename, created_at=document.created_at, chunk_count=len(document.chunks)
    )


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    membership: OrganizationMember = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    rag_service.delete_document(db, membership.organization_id, document_id)
