"""
Example usage and testing script.
Demonstrates various conversation scenarios.
"""
import asyncio
import json
from typing import List, Dict

# Simulated API client for demonstration
class SupportClient:
    """Mock client for testing (replace with actual HTTP client in production)."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.thread_id = None
    
    async def send_message(self, message: str, user_id: str = "test_user") -> Dict:
        """Send a message to the support system."""
        # In production, use httpx or requests
        # For now, just demonstrate the expected flow
        return {
            "response": f"[Demo response to: {message}]",
            "thread_id": "demo-thread-123",
            "agent": "demo",
            "category": "technical"
        }


async def demo_technical_conversation():
    """Demonstrate a technical support conversation."""
    print("=" * 60)
    print("🔧 DEMO 1: Technical Support Conversation")
    print("=" * 60)
    print()
    
    client = SupportClient()
    
    scenarios = [
        "How do I authenticate with your API?",
        "I'm getting 401 errors when calling the endpoint",
        "What are the rate limits for API calls?",
    ]
    
    for message in scenarios:
        print(f"👤 User: {message}")
        response = await client.send_message(message)
        print(f"🤖 {response['agent'].title()}: {response['response']}")
        print(f"   [Category: {response['category']}]\n")


async def demo_billing_conversation():
    """Demonstrate a billing support conversation."""
    print("=" * 60)
    print("💳 DEMO 2: Billing Support Conversation")
    print("=" * 60)
    print()
    
    client = SupportClient()
    
    scenarios = [
        "What's my current subscription plan?",
        "I want a refund for last month due to service outage",
        "What's your refund policy?",
    ]
    
    for message in scenarios:
        print(f"👤 User: {message}")
        response = await client.send_message(message, user_id="user_12345")
        print(f"🤖 {response['agent'].title()}: {response['response']}")
        print(f"   [Category: {response['category']}]\n")


async def demo_fallback_conversation():
    """Demonstrate fallback handling."""
    print("=" * 60)
    print("❓ DEMO 3: Fallback & Clarification")
    print("=" * 60)
    print()
    
    client = SupportClient()
    
    scenarios = [
        "Hello",
        "I need help with my account",  # Ambiguous - triggers fallback
        "I can't connect to the service",  # After clarification
    ]
    
    for message in scenarios:
        print(f"👤 User: {message}")
        response = await client.send_message(message)
        print(f"🤖 {response['agent'].title()}: {response['response']}")
        print(f"   [Category: {response['category']}]\n")


async def demo_multi_turn_conversation():
    """Demonstrate multi-turn conversation with context."""
    print("=" * 60)
    print("🔄 DEMO 4: Multi-Turn Conversation")
    print("=" * 60)
    print()
    
    client = SupportClient()
    
    scenarios = [
        "I'm having trouble with OAuth authentication",
        "I followed the guide but still getting errors",
        "Actually, can I also check my billing details?",
        "And I'd like to request a refund",
    ]
    
    for message in scenarios:
        print(f"👤 User: {message}")
        response = await client.send_message(message)
        print(f"🤖 {response['agent'].title()}: {response['response']}")
        print(f"   [Category: {response['category']}, Thread: {response['thread_id']}]\n")


async def demo_agent_switching():
    """Demonstrate dynamic agent switching."""
    print("=" * 60)
    print("🔀 DEMO 5: Agent Switching")
    print("=" * 60)
    print()
    
    client = SupportClient()
    
    scenarios = [
        ("Technical question", "How do I configure rate limiting?"),
        ("Switch to billing", "Wait, how much does this plan cost?"),
        ("Back to technical", "Okay, back to rate limits - what's the default?"),
    ]
    
    for label, message in scenarios:
        print(f"[{label}]")
        print(f"👤 User: {message}")
        response = await client.send_message(message)
        print(f"🤖 {response['agent'].title()}: {response['response']}")
        print(f"   [Category: {response['category']}]\n")


async def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  Telecom Support AI - Usage Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    print("NOTE: These are simulated examples showing expected behavior.")
    print("To run against live system, start the server first:")
    print("  python main.py")
    print("\n")
    input("Press Enter to continue...\n")
    
    await demo_technical_conversation()
    input("Press Enter for next demo...\n")
    
    await demo_billing_conversation()
    input("Press Enter for next demo...\n")
    
    await demo_fallback_conversation()
    input("Press Enter for next demo...\n")
    
    await demo_multi_turn_conversation()
    input("Press Enter for next demo...\n")
    
    await demo_agent_switching()
    
    print("=" * 60)
    print("✅ All demos complete!")
    print("=" * 60)
    print()
    print("To test with real system:")
    print("1. Start server: python main.py")
    print("2. Test via CLI: python main.py --cli")
    print("3. Test via API: curl http://localhost:8000/chat")
    print()


if __name__ == "__main__":
    asyncio.run(main())
