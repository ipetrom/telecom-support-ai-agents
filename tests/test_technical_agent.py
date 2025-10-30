"""
Simple test script for TechnicalAgent.
Tests the agent with sample technical questions.
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from retriever.retriever import KBRetriever, RetrieverConfig
from agents.technical_agent import TechnicalAgent, ConversationState


def main():
    print("\n" + "="*70)
    print("🔧 Testing TechnicalAgent (with retriever diagnostics)")
    print("="*70 + "\n")
    
    # Setup
    print("📦 Loading retriever from artifacts...")
    retriever_config = RetrieverConfig(artifacts_dir=Path("artifacts"))
    retriever = KBRetriever(retriever_config)
    
    print(f"Retriever config:")
    print(f"  - threshold: {retriever_config.threshold}")
    print(f"  - min_hits: {retriever_config.min_hits}")
    print(f"  - top_k: {retriever_config.top_k}\n")
    
    print("🤖 Initializing LLM...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    print("⚙️  Creating TechnicalAgent...\n")
    agent = TechnicalAgent(llm=llm, retriever=retriever)
    
    # Test cases
    test_questions = [
        "My fiber internet keeps dropping. The PON LED is blinking red. What should I do?",
        "How do I enable bridge mode on my router?",
        "My WiFi is slow on 5 GHz band. Can you help?",
        "My DSL connection keeps dropping, what should I do?",  # Simplified query
    ]
    
    for i, question in enumerate(test_questions, 1):
        print("="*70)
        print(f"❓ Test {i}: {question}")
        print("="*70)
        
        # Show what retriever finds
        print("\n🔍 Retriever output:")
        ret_result = retriever.retrieve(question)
        print(f"  - no_context flag: {ret_result['no_context']}")
        print(f"  - docs retrieved: {len(ret_result['docs'])}")
        print(f"  - scores: {[f'{s:.3f}' for s in ret_result['scores'][:5]]}")
        print(f"  - threshold: {ret_result['applied_threshold']}")
        
        if ret_result['no_context']:
            print(f"  ⚠️  Retriever says NO_CONTEXT!\n")
        
        # Now test agent
        print("🤖 Agent processing:")
        state = ConversationState()
        result = agent.run(state, question)
        
        print(f"\n✅ Reply:\n{result['reply']}\n")
        
        if result.get('no_context'):
            print("⚠️  Agent says NO_CONTEXT - insufficient information in KB\n")
        else:
            print(f"📚 Sources used ({len(result['sources'])} docs):")
            for src in result['sources'][:3]:  # Show top 3
                print(f"   - {src['title']} ({src['file']}) - Score: {src['score']:.3f}")
            print()


if __name__ == "__main__":
    main()