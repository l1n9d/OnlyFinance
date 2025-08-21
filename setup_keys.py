#!/usr/bin/env python3
"""
Create a .env file with your API keys for easy setup
"""

import os
import getpass

def create_env_file():
    print("🔧 Creating .env file for your API keys")
    print("=" * 50)
    
    env_content = []
    
    # OpenAI API Key
    if not os.path.exists(".env") or "OPENAI_API_KEY" not in open(".env").read():
        print("\n🔑 OpenAI API Key Setup")
        print("Get your API key from: https://platform.openai.com/api-keys")
        openai_key = getpass.getpass("Enter your OpenAI API key: ")
        env_content.append(f"OPENAI_API_KEY={openai_key}")
    
    # Pinecone API Key
    if not os.path.exists(".env") or "PINECONE_API_KEY" not in open(".env").read():
        print("\n🌲 Pinecone API Key Setup")
        print("1. Sign up for free at: https://www.pinecone.io/")
        print("2. Create a new project")
        print("3. Get your API key from the console")
        pinecone_key = getpass.getpass("Enter your Pinecone API key: ")
        env_content.append(f"PINECONE_API_KEY={pinecone_key}")
    
    # Write to .env file
    if env_content:
        with open(".env", "w") as f:
            f.write("\n".join(env_content))
        print("\n✅ .env file created successfully!")
        print("\nTo use these keys, run:")
        print("  source load_env.sh")
        print("  python test_pinecone.py")
        
        # Create load_env.sh script
        with open("load_env.sh", "w") as f:
            f.write("""#!/bin/bash
# Load environment variables from .env file
export $(cat .env | xargs)
echo "✅ Environment variables loaded from .env file"
""")
        os.chmod("load_env.sh", 0o755)
        print("✅ load_env.sh script created!")
    else:
        print("✅ .env file already exists with all required keys")

if __name__ == "__main__":
    create_env_file()
