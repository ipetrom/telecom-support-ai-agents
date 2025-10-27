"""
Billing Agent Tools.
Mock implementations of billing operations for the prototype.

Migration note: Replace with actual API calls to billing system in production.
Maintain the same function signatures for LangChain tool binding.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Mock database for development
MOCK_SUBSCRIPTIONS = {
    "user_12345": {
        "plan": "Premium 5G",
        "monthly_cost": 89.99,
        "start_date": "2024-01-15",
        "auto_renew": True,
        "data_limit_gb": 100
    },
    "user_67890": {
        "plan": "Basic 4G",
        "monthly_cost": 39.99,
        "start_date": "2024-06-01",
        "auto_renew": True,
        "data_limit_gb": 20
    }
}

MOCK_REFUND_CASES = {}
_case_counter = 1000


def get_subscription(user_id: str) -> Dict[str, any]:
    """
    Retrieve current subscription details for a user.
    
    Args:
        user_id: Unique user identifier
    
    Returns:
        Dictionary with subscription details or error message
        
    Example:
        >>> get_subscription("user_12345")
        {'plan': 'Premium 5G', 'monthly_cost': 89.99, ...}
    """
    logger.info(f"Fetching subscription for user: {user_id}")
    
    subscription = MOCK_SUBSCRIPTIONS.get(user_id)
    
    if subscription:
        logger.info(f"Found subscription: {subscription['plan']}")
        return {
            "success": True,
            "data": subscription
        }
    else:
        logger.warning(f"No subscription found for user: {user_id}")
        return {
            "success": False,
            "error": "No active subscription found for this user"
        }


def open_refund_case(
    user_id: str,
    reason: str,
    amount: Optional[float] = None
) -> Dict[str, any]:
    """
    Create a new refund case in the billing system.
    
    Args:
        user_id: Unique user identifier
        reason: Reason for refund request
        amount: Specific refund amount (optional, defaults to last month's charge)
    
    Returns:
        Dictionary with case ID and status
        
    Example:
        >>> open_refund_case("user_12345", "Service outage for 3 days")
        {'success': True, 'case_id': 'REF-1001', 'status': 'pending', ...}
    """
    global _case_counter
    
    logger.info(f"Opening refund case for user: {user_id}, reason: {reason}")
    
    # Validate user has subscription
    subscription = MOCK_SUBSCRIPTIONS.get(user_id)
    if not subscription:
        logger.error(f"Cannot open refund case: no subscription for {user_id}")
        return {
            "success": False,
            "error": "No active subscription found. Refund cases require an active subscription."
        }
    
    # Generate case
    _case_counter += 1
    case_id = f"REF-{_case_counter}"
    
    refund_amount = amount or subscription["monthly_cost"]
    
    case_data = {
        "case_id": case_id,
        "user_id": user_id,
        "reason": reason,
        "amount": refund_amount,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "estimated_resolution": (datetime.now() + timedelta(days=5)).date().isoformat()
    }
    
    MOCK_REFUND_CASES[case_id] = case_data
    
    logger.info(f"Refund case created: {case_id}")
    
    return {
        "success": True,
        "case_id": case_id,
        "status": "pending",
        "amount": refund_amount,
        "message": f"Refund case {case_id} has been created. You will receive an update within 3-5 business days.",
        "estimated_resolution": case_data["estimated_resolution"]
    }


def get_refund_policy() -> str:
    """
    Retrieve the company's refund policy text.
    
    Returns:
        Full refund policy as string
        
    Example:
        >>> policy = get_refund_policy()
        >>> print(policy[:100])
        'Our refund policy allows for full refunds within 30 days...'
    """
    logger.info("Fetching refund policy")
    
    policy = """
    📋 REFUND POLICY - Telecom Support
    
    1. ELIGIBILITY
       - Refunds are available within 30 days of billing date
       - Service outages exceeding 24 hours qualify for prorated refunds
       - Early termination fees may apply for contract plans
    
    2. PROCESSING TIME
       - Standard refunds: 5-7 business days
       - Disputed charges: 10-14 business days
       - Refunds are issued to the original payment method
    
    3. PARTIAL REFUNDS
       - Prorated based on unused service days
       - Calculated automatically by our billing system
    
    4. NON-REFUNDABLE ITEMS
       - Activation fees
       - Hardware purchases (separate 14-day return policy applies)
       - International roaming charges
    
    5. HOW TO REQUEST
       - Contact support via chat, phone, or email
       - Provide reason and relevant details
       - Case will be opened and tracked
    
    For specific questions about your refund eligibility, please ask our billing specialist.
    """
    
    return policy.strip()


# Tool metadata for LangChain
BILLING_TOOLS_METADATA = [
    {
        "name": "get_subscription",
        "description": "Retrieve current subscription plan and billing details for a user. Use this when the user asks about their plan, pricing, or billing cycle.",
        "function": get_subscription
    },
    {
        "name": "open_refund_case",
        "description": "Create a refund case in the billing system. Use this when the user explicitly requests a refund or compensation. Requires a clear reason.",
        "function": open_refund_case
    },
    {
        "name": "get_refund_policy",
        "description": "Get the complete refund policy document. Use this when the user asks about refund eligibility, timeframes, or general refund questions.",
        "function": get_refund_policy
    }
]
