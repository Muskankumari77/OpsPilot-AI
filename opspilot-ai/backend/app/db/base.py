"""
Imports every model so that `Base.metadata.create_all()` (called from
main.py on startup) can see and create all their tables.

As each domain is built in later phases, its model import gets added here.
"""
from app.db.session import Base  # noqa: F401

from app.models.user import User  # noqa: F401
from app.models.organization import Organization, OrganizationMember  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.customer import Customer  # noqa: F401
from app.models.sale import Sale  # noqa: F401
from app.models.inventory import Inventory  # noqa: F401
from app.models.expense import Expense  # noqa: F401
from app.models.dataset import Dataset  # noqa: F401
from app.models.document import Document, DocumentChunk  # noqa: F401
from app.models.action import Action  # noqa: F401
from app.models.alert import Alert  # noqa: F401
