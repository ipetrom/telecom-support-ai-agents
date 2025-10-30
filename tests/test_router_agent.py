#!/usr/bin/env python3
"""
Interactive test script for RouterAgent.
Allows user to input queries and see intelligent intent classification and routing.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from agents.router_agent import RouterAgent, ConversationState


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 75)
    print("🚀 RouterAgent Interactive Test")
    print("=" * 75)
    print("\nTest the RouterAgent by entering your queries.")
    print("The agent will:")
    print("  • Classify intent (TECHNICAL / BILLING / UNKNOWN)")
    print("  • Provide confidence score (0.0-1.0)")
    print("  • Show reasoning")
    print("\nType 'quit' or 'exit' to stop.\n")


def print_result(user_input, result):
    """Pretty print the routing result"""
    print(f"\n{'─' * 75}")
    print(f"📝 Your input: '{user_input}'")
    print(f"{'─' * 75}")
    
    route = result.get('route')
    confidence = result.get('confidence', 0.0)
    classification = result.get('classification', {})
    reasoning = classification.get('reasoning', 'N/A')
    
    # Format route with emoji
    route_map = {
        'technical': '🔧 TECHNICAL',
        'billing': '💳 BILLING',
        'unknown': '❓ UNKNOWN',
        'fallback': '❓ FALLBACK'
    }
    route_display = route_map.get(route, f'❓ {route.upper()}')
    
    # Format confidence as a progress bar
    confidence_pct = confidence * 100
    bar_length = 20
    filled = int(bar_length * confidence)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    print(f"Route: {route_display}")
    print(f"Confidence: {bar} {confidence_pct:.1f}%")
    print(f"Reasoning: {reasoning}")
    print(f"{'─' * 75}")


def main():
    """Main interactive loop"""
    print_header()
    
    # Initialize LLM and RouterAgent
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        router = RouterAgent(llm=llm)
    except Exception as e:
        print(f"❌ Error initializing RouterAgent: {e}")
        print("Make sure OPENAI_API_KEY is set in .env file")
        return
    
    conversation_history = []
    message_count = 0
    
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
            
            # Run router
            print("\n⏳ Routing message...")
            result = router.route(state, user_input)
            
            # Print result
            print_result(user_input, result)
            
            # Add assistant response to history
            route = result.get('route', 'unknown')
            conversation_history.append({
                "role": "assistant",
                "content": f"[Routed to {route}]"
            })
            
            message_count += 1
            
            # Show conversation stats
            print(f"\n📊 Messages: {message_count} | History length: {len(conversation_history)}")
            
        except KeyboardInterrupt:
            print("\n\n❌ Test interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue


if __name__ == "__main__":
    main()