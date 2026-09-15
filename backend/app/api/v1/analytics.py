"""
Read-only business analytics endpoints backing the SLA & Delivery Promise
Monitoring and Business Impact Estimation dashboards.

These are operational-intelligence views over the same dataset the domain
agents use — not agent runs — so they sit on the generic authenticated gate
(soft in dev, enforced in prod) rather than a per-domain RBAC role.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services import impact_service, sla_service

router = APIRouter(prefix="/api/v1/analytics", tags=["Business Analytics"])


@router.get("/sla")
def sla_overview(
    start: Optional[str] = Query(None, description="Purchase date from, YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="Purchase date to, YYYY-MM-DD"),
    state: Optional[str] = Query(None, description="Customer state, e.g. SP"),
    seller: Optional[str] = Query(None, description="Seller id"),
    category: Optional[str] = Query(None, description="Product category (English)"),
    db: Session = Depends(get_db),
):
    return sla_service.get_sla_overview(db, start=start, end=end, state=state, seller=seller, category=category)


@router.get("/impact")
def business_impact(
    start: Optional[str] = Query(None, description="Purchase date from, YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="Purchase date to, YYYY-MM-DD"),
    state: Optional[str] = Query(None, description="Customer state, e.g. SP"),
    seller: Optional[str] = Query(None, description="Seller id"),
    category: Optional[str] = Query(None, description="Product category (English)"),
    db: Session = Depends(get_db),
):
    return impact_service.get_business_impact(db, start=start, end=end, state=state, seller=seller, category=category)
