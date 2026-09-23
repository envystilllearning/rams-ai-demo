"""Payment provider abstraction (PRD §16, §54).

`MockProvider`  — demo flow: instantly activates a subscription without Stripe.
`StripeProvider`— real integration; activated via PAYMENT_PROVIDER=stripe.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class CheckoutResult:
    """Outcome of a checkout request."""

    provider: str
    status: str  # "active" (mock) or "redirect" (stripe)
    url: str | None = None
    message: str | None = None


class PaymentProvider(ABC):
    name: str

    @abstractmethod
    def create_checkout(self, user_id: str, email: str | None) -> CheckoutResult: ...

    @abstractmethod
    def create_portal(self, user_id: str) -> CheckoutResult: ...


class MockProvider(PaymentProvider):
    """Demo provider: no external calls. Subscription activation is handled
    directly by the billing router against the local subscriptions table."""

    name = "mock"

    def create_checkout(self, user_id: str, email: str | None) -> CheckoutResult:
        return CheckoutResult(
            provider=self.name,
            status="active",
            message="Mock checkout completed — subscription activated.",
        )

    def create_portal(self, user_id: str) -> CheckoutResult:
        return CheckoutResult(
            provider=self.name,
            status="mock_portal",
            message="Mock portal: use Cancel subscription below to end access.",
        )


class StripeProvider(PaymentProvider):
    """Real Stripe implementation. Requires STRIPE_SECRET_KEY and
    STRIPE_PRICE_ID. Activated by PAYMENT_PROVIDER=stripe."""

    name = "stripe"

    def create_checkout(self, user_id: str, email: str | None) -> CheckoutResult:
        import stripe  # imported lazily so mock mode needs no stripe key

        s = get_settings()
        if not s.stripe_secret_key or not s.stripe_price_id:
            raise RuntimeError("Stripe is not configured (missing key or price id)")
        stripe.api_key = s.stripe_secret_key

        from app.repositories.subscriptions import SubscriptionsRepo

        repo = SubscriptionsRepo()
        row = repo.get(user_id)
        customer_id = row.get("stripe_customer_id") if row else None
        if not customer_id:
            customer = stripe.Customer.create(email=email, metadata={"user_id": user_id})
            customer_id = customer.id
            repo.upsert(user_id, {"stripe_customer_id": customer_id})

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": s.stripe_price_id, "quantity": 1}],
            success_url=f"{s.frontend_url}/dashboard/settings/billing?success=1",
            cancel_url=f"{s.frontend_url}/dashboard/settings/billing?canceled=1",
            metadata={"user_id": user_id},
        )
        return CheckoutResult(provider=self.name, status="redirect", url=session.url)

    def create_portal(self, user_id: str) -> CheckoutResult:
        import stripe

        s = get_settings()
        if not s.stripe_secret_key:
            raise RuntimeError("Stripe is not configured")
        stripe.api_key = s.stripe_secret_key

        from app.repositories.subscriptions import SubscriptionsRepo

        row = SubscriptionsRepo().get(user_id)
        customer_id = row.get("stripe_customer_id") if row else None
        if not customer_id:
            raise RuntimeError("No Stripe customer for this user yet")

        portal = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{s.frontend_url}/dashboard/settings/billing",
        )
        return CheckoutResult(provider=self.name, status="redirect", url=portal.url)


def get_payment_provider() -> PaymentProvider:
    s = get_settings()
    if s.payment_provider.lower() == "stripe":
        return StripeProvider()
    return MockProvider()
