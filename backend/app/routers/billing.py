"""Billing endpoints (PRD §16, §24).

GET  /api/subscription        — current subscription state for the user
POST /api/stripe/checkout     — start checkout (mock completes instantly)
POST /api/stripe/portal       — customer portal (mock returns guidance)
POST /api/billing/cancel      — mock-only: ends access immediately
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.deps import UserAuth
from app.integrations.payments import get_payment_provider
from app.repositories.subscriptions import SubscriptionsRepo
from app.services.entitlement import check_entitlement

router = APIRouter(prefix="/api", tags=["billing"])

MOCK_PRICE_LABEL = "£9.95/month"


@router.get("/subscription")
async def get_subscription(user: UserAuth) -> dict[str, Any]:
    row = SubscriptionsRepo().get(user.id)
    return {
        "status": (row or {}).get("status", "none"),
        "can_generate": check_entitlement(user.id),
        "price_label": MOCK_PRICE_LABEL,
        "cancel_at_period_end": bool((row or {}).get("cancel_at_period_end", False)),
        "current_period_end": (row or {}).get("current_period_end"),
        "provider": get_payment_provider().name,
    }


@router.post("/stripe/checkout")
async def create_checkout(user: UserAuth) -> dict[str, Any]:
    repo = SubscriptionsRepo()
    existing = repo.get(user.id)

    # Already active — nothing to buy (idempotent behaviour)
    if existing and (existing.get("status") or "").lower() in ("active", "trialing"):
        return {"status": "already_active", "url": None, "message": None}

    provider = get_payment_provider()
    result = provider.create_checkout(user.id, user.email)

    if result.status == "active":
        # Mock flow: activate for 30 days from now
        now = datetime.now(UTC)
        repo.upsert(
            user.id,
            {
                "status": "active",
                "stripe_subscription_id": f"mock_sub_{user.id[:8]}",
                "stripe_price_id": "mock_price_995",
                "current_period_start": now.isoformat(),
                "current_period_end": (now + timedelta(days=30)).isoformat(),
                "cancel_at_period_end": False,
            },
        )
        return {
            "status": "active",
            "url": None,
            "message": result.message,
        }

    return {"status": result.status, "url": result.url, "message": None}


@router.post("/stripe/portal")
async def create_portal(user: UserAuth) -> dict[str, Any]:
    provider = get_payment_provider()
    result = provider.create_portal(user.id)
    return {"status": result.status, "url": result.url, "message": result.message}


@router.post("/billing/cancel")
async def cancel_subscription(user: UserAuth) -> dict[str, Any]:
    """Mock-only immediate cancellation. With real Stripe, cancellation
    happens in the Customer Portal and arrives via webhook."""
    provider = get_payment_provider()
    if provider.name != "mock":
        raise HTTPException(
            status_code=400,
            detail="Use the Stripe Customer Portal to cancel your subscription.",
        )

    repo = SubscriptionsRepo()
    row = repo.get(user.id)
    if not row:
        raise HTTPException(status_code=404, detail="No subscription found")

    repo.upsert(
        user.id,
        {
            "status": "canceled",
            "cancel_at_period_end": False,
            "canceled_at": datetime.now(UTC).isoformat(),
        },
    )
    return {"status": "canceled", "message": "Subscription canceled — access removed."}
