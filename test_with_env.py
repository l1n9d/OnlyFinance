#!/usr/bin/env python3
"""
Test script that loads environment variables from .env file
"""

import os
import sys

def load_env_file():
    """Load environment variables from .env file"""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
        print("✅ Loaded environment variables from .env file")
    else:
        print("❌ No .env file found. Run 'python setup_keys.py' first")
        return False
    return True

def main():
    print("🧪 Testing Pinecone Integration with Environment File...")
    
    # Load environment variables
    if not load_env_file():
        return
    
    # Import and run the test
    try:
        from test_pinecone import test_pinecone_integration
        success = test_pinecone_integration()
        if success:
            print("\n🎉 All tests passed! You can now run: streamlit run app.py")
        else:
            print("\n❌ Tests failed. Please check your API keys and try again.")
    except ImportError:
        print("❌ Could not import test_pinecone module")

if __name__ == "__main__":
    main()
