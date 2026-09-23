"""Subscription entitlement logic — the backend is the authority (PRD §4/§17)."""

from app.core.config import get_settings
from app.repositories.subscriptions import SubscriptionsRepo

ALLOWED_STATUSES = ("active", "trialing")


def has_active_subscription(subscription: dict | None) -> bool:
    """Decide whether a subscription row grants generation access.

    - active / trialing  -> yes
    - past_due           -> only if SUBSCRIPTION_ALLOW_PAST_DUE=true
    - anything else / none -> no
    """
    if not subscription:
        return False
    status = (subscription.get("status") or "").lower()
    if status in ALLOWED_STATUSES:
        return True
    if status == "past_due":
        return get_settings().subscription_allow_past_due
    return False


def check_entitlement(user_id: str) -> bool:
    """Load the user's subscription and evaluate entitlement."""
    row = SubscriptionsRepo().get(user_id)
    return has_active_subscription(row)
