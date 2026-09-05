"""
Aggregates every v1 sub-router into one `api_router` that main.py mounts
under /api/v1. Each phase adds its own router include here as that
module's endpoints get built.
"""
from fastapi import APIRouter

from app.api.v1 import (
    actions,
    alerts,
    anomalies,
    auth,
    copilot,
    customers,
    dashboard,
    datasets,
    expenses,
    forecasts,
    health,
    insights,
    inventory,
    knowledge_base,
    organizations,
    products,
    reports,
    sales,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["forecasts"])
api_router.include_router(anomalies.router, prefix="/anomalies", tags=["anomalies"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
api_router.include_router(knowledge_base.router, prefix="/knowledge-base", tags=["knowledge-base"])
api_router.include_router(actions.router, prefix="/actions", tags=["actions"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
