import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from tools.billing_tools import as_langchain_tools
from agents.billing_agent import BillingAgent, ConversationState


def debug_response(obj):
    """Debug helper to see what LLM returns"""
    print(f"  Response type: {type(obj)}")
    print(f"  Has content: {hasattr(obj, 'content')}")
    if hasattr(obj, 'content'):
        print(f"  Content: '{obj.content}'")
    print(f"  Has text: {hasattr(obj, 'text')}")
    if hasattr(obj, 'text'):
        print(f"  Text: '{obj.text}'")
    print(f"  Str repr: '{str(obj)}'")
    print(f"  Dir: {[x for x in dir(obj) if not x.startswith('_')][:10]}")


def main():
    print("\n🧪 Testing BillingAgent\n")
    
    # Setup
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = as_langchain_tools()
    agent = BillingAgent(llm=llm, tools=tools)
    
    # Test 1: Simple policy question
    print("=" * 60)
    print("Test 1: Ask about refund policy")
    print("=" * 60)
    state = ConversationState(user_id="u123")
    result = agent.run(state, "What is your refund policy?")
    print(f"Reply: {result['reply']}\n")
    
    # Test 2: Get subscription
    print("=" * 60)
    print("Test 2: Get subscription info")
    print("=" * 60)
    state = ConversationState(user_id="u123")
    result = agent.run(state, "What's my subscription plan?")
    print(f"Reply: {result['reply']}")
    print(f"Tools used: {[t['name'] for t in result['used_tools']]}\n")
    
    # Test 3: Multi-turn
    print("=" * 60)
    print("Test 3: Multi-turn conversation")
    print("=" * 60)
    state = ConversationState(user_id="u456")
    result1 = agent.run(state, "What's my current plan?")
    print(f"Q1: What's my current plan?")
    print(f"A1: {result1['reply']}\n")
    
    state.history.append({"role": "user", "content": "What's my current plan?"})
    state.history.append({"role": "assistant", "content": result1['reply']})
    
    result2 = agent.run(state, "How much does it cost?")
    print(f"Q2: How much does it cost?")
    print(f"A2: {result2['reply']}\n")
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)