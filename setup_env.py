#!/usr/bin/env python3
"""
Environment setup script for Pinecone + OpenAI integration
This script helps you set up your API keys interactively
"""

import os
import getpass

def setup_environment():
    print("🔧 Setting up environment for Fidelity Financial Learning Assistant")
    print("=" * 60)
    
    # OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n🔑 OpenAI API Key Setup")
        print("Get your API key from: https://platform.openai.com/api-keys")
        openai_key = getpass.getpass("Enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = openai_key
        print("✅ OpenAI API key set for this session")
    else:
        print("✅ OpenAI API key already set")
    
    # Pinecone API Key
    if not os.getenv("PINECONE_API_KEY"):
        print("\n🌲 Pinecone API Key Setup")
        print("1. Sign up for free at: https://www.pinecone.io/")
        print("2. Create a new project")
        print("3. Get your API key from the console")
        pinecone_key = getpass.getpass("Enter your Pinecone API key: ")
        os.environ["PINECONE_API_KEY"] = pinecone_key
        print("✅ Pinecone API key set for this session")
    else:
        print("✅ Pinecone API key already set")
    
    print("\n🎯 Environment setup complete!")
    print("You can now run the test script: python test_pinecone.py")
    print("Or start the app directly: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    setup_environment()
