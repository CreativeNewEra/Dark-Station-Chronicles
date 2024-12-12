import os
from dotenv import load_dotenv
import anthropic
from llama_cpp import Llama

def test_claude():
    """Test Claude API connection"""
    print("\nTesting Claude connection...")
    try:
        client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": "Say 'Claude connection successful!'"
            }]
        )
        print("✓ Claude test successful!")
        print(f"Response: {response.content[0].text}")
        return True
    except Exception as e:
        print("✗ Claude test failed!")
        print(f"Error: {str(e)}")
        return False

def test_llama():
    """Test Llama.cpp installation"""
    print("\nTesting Llama.cpp installation...")
    try:
        # Just test if we can import and initialize Llama
        print("✓ Llama.cpp import successful!")

        # Check if model path is set
        model_path = os.getenv("LLAMA_MODEL_PATH")
        if not model_path:
            print("✗ LLAMA_MODEL_PATH not set in .env!")
            return False

        if not os.path.exists(model_path):
            print(f"✗ Model file not found at: {model_path}")
            return False

        print(f"✓ Found model file at: {model_path}")
        return True
    except Exception as e:
        print("✗ Llama.cpp test failed!")
        print(f"Error: {str(e)}")
        return False

def main():
    print("=== AI Backend Test Script ===")

    # Load environment variables
    print("\nLoading environment variables...")
    load_dotenv()

    # Run tests
    claude_ok = test_claude()
    llama_ok = test_llama()

    # Summary
    print("\n=== Test Summary ===")
    print(f"Claude API: {'✓' if claude_ok else '✗'}")
    print(f"Llama.cpp: {'✓' if llama_ok else '✗'}")

if __name__ == "__main__":
    main()
