"""
Billing tools for the BillingAgent.

This module exposes three business capabilities as callable tools:
  1) get_subscription(user_id) -> SubscriptionOut
  2) open_refund_case(user_id, reason, amount, invoice_id) -> RefundCaseOut
  3) get_refund_policy() -> RefundPolicyOut

Design notes
- Pure-Python implementation with an in-memory store to keep the MVP deterministic.
- Pydantic models for strict I/O validation.
- Helper factory functions `as_langchain_tools()` to wrap functions as StructuredTool for LangChain.
- All monetary fields are in PLN. Timezone: Europe/Warsaw.

Example (manual):
  from tools.billing_tools import as_langchain_tools
  tools = as_langchain_tools()
  tools[0].invoke({"user_id":"u123"})

Security & Privacy
- Mask PII in logs. Do not log full invoices or card numbers.
- This MVP does not persist data to disk; integrate with real systems later.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
import itertools
import logging
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, PositiveFloat, validator

try:
    # Optional LangChain import for tool wrappers
    from langchain.tools import StructuredTool
except Exception:  # pragma: no cover
    StructuredTool = None  # type: ignore

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -----------------------------
# In-memory mock data
# -----------------------------

@dataclass
class _Plan:
    name: str
    monthly_price: float
    currency: str = "PLN"


_PLANS: Dict[str, _Plan] = {
    "S": _Plan(name="S 50 GB", monthly_price=35.0),
    "M": _Plan(name="M 100 GB", monthly_price=45.0),
    "L": _Plan(name="L Unlimited", monthly_price=65.0),
}


@dataclass
class _Sub:
    plan_code: str
    start_date: date
    status: str  # active, suspended, canceled


_USERS: Dict[str, _Sub] = {
    "u123": _Sub(plan_code="M", start_date=date(2025, 8, 15), status="active"),
    "u456": _Sub(plan_code="L", start_date=date(2025, 6, 1), status="active"),
}


# simple id generator for refund cases
_CASE_COUNTER = itertools.count(10001)


# -----------------------------
# Policy (deterministic for MVP)
# -----------------------------

class RefundReason(str, Enum):
    OVERCHARGE = "overcharge"
    SERVICE_OUTAGE = "service_outage"
    WITHIN_COOLING_OFF = "within_cooling_off" #odstąpienie od umowy
    OTHER = "other"


class RefundPolicyOut(BaseModel):
    cooling_off_days: int = 14
    processing_sla_business_days: int = 5
    refund_to_method_days: str = Field(
        "7-10", description="Expected days for funds to appear on original payment method",
    )
    non_refundable_items: List[str] = [
        "One-time activation fees after activation",
        "Usage outside plan (e.g., premium services)",
    ]
    notes: List[str] = [
        "Refunds are issued to the original payment method",
        "Business days exclude weekends and public holidays in Poland",
    ]


def get_refund_policy() -> RefundPolicyOut:
    """Return the simple refund policy used by the BillingAgent."""
    return RefundPolicyOut()


# -----------------------------
# Schemas
# -----------------------------

class SubscriptionIn(BaseModel):
    user_id: str = Field(..., min_length=2, max_length=64)


class SubscriptionOut(BaseModel):
    user_id: str
    plan_code: str
    plan_name: str
    price_monthly_pln: float
    status: str
    start_date: date


def get_subscription(user_id: str) -> SubscriptionOut:
    """Return subscription details for a given user_id (mock)."""
    sub = _USERS.get(user_id)
    if not sub:
        # Non-existing users are treated as not provisioned yet
        return SubscriptionOut(
            user_id=user_id,
            plan_code="N/A",
            plan_name="No active plan",
            price_monthly_pln=0.0,
            status="not_found",
            start_date=date(1970, 1, 1),
        )
    plan = _PLANS[sub.plan_code]
    return SubscriptionOut(
        user_id=user_id,
        plan_code=sub.plan_code,
        plan_name=plan.name,
        price_monthly_pln=plan.monthly_price,
        status=sub.status,
        start_date=sub.start_date,
    )


class RefundCaseIn(BaseModel):
    user_id: str = Field(..., min_length=2, max_length=64)
    reason: RefundReason
    amount_pln: PositiveFloat = Field(..., gt=0, le=1000.0, description="Refund amount in PLN (0 < x ≤ 1000)")
    invoice_id: str = Field(..., min_length=3, max_length=64)
    description: Optional[str] = Field(None, max_length=1000)

    @validator("amount_pln")
    def _cap_amount(cls, v):  # pragma: no cover
        # Business guard: cap to 2x monthly price if we know the plan
        return float(v)


class RefundCaseOut(BaseModel):
    case_id: str
    status: str  # opened, pending_review, rejected, approved
    next_steps: List[str]
    sla_business_days: int
    eta_date: date


def _business_eta(sla_bd: int) -> date:
    # Approximation: add SLA days ignoring weekends for MVP simplicity
    return date.today() + timedelta(days=sla_bd)


def open_refund_case(user_id: str, reason: RefundReason, amount_pln: float, invoice_id: str, description: Optional[str] = None) -> RefundCaseOut:
    """Open a refund case and return case metadata. This is a deterministic mock implementation."""
    case_id = f"R{next(_CASE_COUNTER)}"
    policy = get_refund_policy()

    # Minimal validations
    sub = _USERS.get(user_id)
    if not sub:
        base_steps = [
            "We could not find an active subscription for this user.",
            "Please verify the user_id or create a new subscription first.",
        ]
        return RefundCaseOut(
            case_id=case_id,
            status="pending_review",
            next_steps=base_steps,
            sla_business_days=policy.processing_sla_business_days,
            eta_date=_business_eta(policy.processing_sla_business_days),
        )

    # Domain rules (simple, for MVP)
    steps: List[str] = [
        f"Case created for invoice {invoice_id}.",
        f"Initial classification: {reason.value}.",
        "A billing specialist will validate the charge against the account records.",
        f"If approved, refund of {amount_pln:.2f} PLN will be issued to the original payment method.",
    ]

    status = "opened"
    if reason == RefundReason.WITHIN_COOLING_OFF:
        steps.append("Cooling-off period applies (14 days). Priority processing.")
        status = "pending_review"

    return RefundCaseOut(
        case_id=case_id,
        status=status,
        next_steps=steps,
        sla_business_days=policy.processing_sla_business_days,
        eta_date=_business_eta(policy.processing_sla_business_days),
    )


# -----------------------------
# LangChain wrappers (optional)
# -----------------------------

def as_langchain_tools() -> List:
    """Return tools wrapped as LangChain StructuredTool list (if LC is installed)."""
    if StructuredTool is None:  # pragma: no cover
        return []

    def _tool_get_subscription(inp: SubscriptionIn) -> SubscriptionOut:
        return get_subscription(inp.user_id)

    def _tool_open_refund_case(inp: RefundCaseIn) -> RefundCaseOut:
        return open_refund_case(
            user_id=inp.user_id,
            reason=inp.reason,
            amount_pln=float(inp.amount_pln),
            invoice_id=inp.invoice_id,
            description=inp.description,
        )

    def _tool_get_refund_policy(_: dict | None = None) -> RefundPolicyOut:
        return get_refund_policy()

    return [
        StructuredTool.from_function(
            name="get_subscription",
            description="Return subscription details for a given user_id (plan, price, status).",
            func=_tool_get_subscription,
            args_schema=SubscriptionIn,
            return_direct=False,
        ),
        StructuredTool.from_function(
            name="open_refund_case",
            description=(
                "Open a refund case with reason, amount (PLN), and invoice id. "
                "Returns case_id, SLA, and next steps."
            ),
            func=_tool_open_refund_case,
            args_schema=RefundCaseIn,
            return_direct=False,
        ),
        StructuredTool.from_function(
            name="get_refund_policy",
            description="Return the simplified refund policy (cooling-off period, SLA, notes).",
            func=_tool_get_refund_policy,
            return_direct=False,
        ),
    ]