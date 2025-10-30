"""
Interactive test script for FallbackAgent.
Allows user to input queries and see routing decisions and agent responses.
"""

import sys
import os

# Add parent directory to path so we can import agents module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fallback_agent import FallbackAgent, ConversationState


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 70)
    print("🤖 FallbackAgent Interactive Test")
    print("=" * 70)
    print("\nTest the FallbackAgent by entering your queries.")
    print("The agent will:")
    print("  • Detect the route hint (technical/billing/None)")
    print("  • Provide an appropriate response")
    print("\nType 'quit' or 'exit' to stop.\n")


def print_result(user_input, result):
    """Pretty print the result"""
    print(f"\n{'─' * 70}")
    print(f"📝 Your input: '{user_input}'")
    print(f"{'─' * 70}")
    
    route_hint = result.get('route_hint')
    reply = result.get('reply')
    
    # Format route hint with color/emoji
    if route_hint == 'technical':
        route_display = "🔧 TECHNICAL"
    elif route_hint == 'billing':
        route_display = "💳 BILLING"
    else:
        route_display = "❓ UNKNOWN"
    
    print(f"Route Hint: {route_display}")
    print(f"\n📢 Agent Response:")
    print(f"─" * 70)
    print(reply)
    print(f"─" * 70)


def main():
    """Main interactive loop"""
    print_header()
    
    agent = FallbackAgent()
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 Enter your query: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n✅ Thanks for testing! Goodbye!\n")
                break
            
            # Skip empty input
            if not user_input:
                print("⚠️  Please enter a query.")
                continue
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Create state with history
            state = ConversationState(
                history=conversation_history,
                last_agent=None
            )
            
            # Run agent
            result = agent.run(state, user_input)
            
            # Print result
            print_result(user_input, result)
            
            # Add assistant response to history
            conversation_history.append({
                "role": "assistant",
                "content": result.get('reply', '')
            })
            
            # Show conversation stats
            print(f"\n📊 Conversation: {len(conversation_history)} messages")
            
        except KeyboardInterrupt:
            print("\n\n❌ Test interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


def demo_mode():
    """Run demo with predefined queries"""
    print_header()
    print("🎬 Running DEMO mode with predefined queries...\n")
    
    agent = FallbackAgent()
    state = ConversationState(history=[], last_agent=None)
    
    demo_queries = [
        "My WiFi is not working",
        "How much is the subscription?",
        "APN bridge problem",
        "I want a refund",
        "Router keeps disconnecting",
        "Hello there",
    ]
    
    for query in demo_queries:
        result = agent.run(state, query)
        print_result(query, result)
        input("\nPress Enter to continue to next query...")
    
    print("\n✅ Demo completed!\n")


if __name__ == "__main__":
    # Check if user wants demo mode
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['demo', '--demo', '-d']:
        demo_mode()
    else:
        main()
