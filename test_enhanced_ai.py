import os
from dotenv import load_dotenv
from src.ai.ai_manager import EnhancedAIManager

def test_backend_switching():
    """Test switching between AI backends"""
    print("\nTesting backend switching...")
    try:
        ai_manager = EnhancedAIManager()

        # Test Claude backend
        print("\nTesting Claude backend:")
        if ai_manager.switch_backend("claude"):
            print("✓ Successfully switched to Claude")
            response = ai_manager.get_ai_response("What is your name?")
            print(f"Claude response: {response}")
        else:
            print("✗ Failed to switch to Claude backend")

        # Test Llama backend
        print("\nTesting Llama backend:")
        if ai_manager.switch_backend("llama"):
            print("✓ Successfully switched to Llama")
            response = ai_manager.get_ai_response("What is your name?")
            print(f"Llama response: {response}")
        else:
            print("✗ Failed to switch to Llama backend")

        return True
    except Exception as e:
        print(f"✗ Backend switching test failed: {str(e)}")
        return False

def test_game_responses():
    """Test game-specific responses"""
    print("\nTesting game-specific responses...")
    try:
        ai_manager = EnhancedAIManager()

        # Sample game state
        game_state = {
            "current_room": "cargo_hold",
            "player_stats": {
                "health": 100,
                "energy": 90,
                "level": 1
            },
            "inventory": ["medkit", "energy_cell"]
        }

        # Test with Claude
        print("\nTesting game response with Claude:")
        ai_manager.switch_backend("claude")
        response = ai_manager.get_ai_response("look around", game_state)
        print(f"Claude game response: {response}")

        # Test with Llama
        print("\nTesting game response with Llama:")
        ai_manager.switch_backend("llama")
        response = ai_manager.get_ai_response("look around", game_state)
        print(f"Llama game response: {response}")

        return True
    except Exception as e:
        print(f"✗ Game response test failed: {str(e)}")
        return False

def test_fallback():
    """Test fallback mechanism"""
    print("\nTesting fallback mechanism...")
    try:
        ai_manager = EnhancedAIManager()

        # Temporarily invalidate Claude backend to test fallback
        ai_manager.backends["claude"].api_key = "invalid_key"

        print("Testing with invalid Claude key (should fallback to Llama):")
        response = ai_manager.get_ai_response("Hello")
        print(f"Fallback response: {response}")

        return True
    except Exception as e:
        print(f"✗ Fallback test failed: {str(e)}")
        return False

def main():
    print("=== Enhanced AI Backend Test Script ===")

    # Load environment variables
    print("\nLoading environment variables...")
    load_dotenv()

    # Run tests
    backend_switch_ok = test_backend_switching()
    game_responses_ok = test_game_responses()
    fallback_ok = test_fallback()

    # Summary
    print("\n=== Test Summary ===")
    print(f"Backend Switching: {'✓' if backend_switch_ok else '✗'}")
    print(f"Game Responses: {'✓' if game_responses_ok else '✗'}")
    print(f"Fallback Mechanism: {'✓' if fallback_ok else '✗'}")

if __name__ == "__main__":
    main()
