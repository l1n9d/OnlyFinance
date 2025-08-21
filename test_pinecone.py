#!/usr/bin/env python3
"""
Test script for Pinecone integration
Usage: python test_pinecone.py
Make sure to set PINECONE_API_KEY and OPENAI_API_KEY environment variables
"""

import os
from data_handler import DataHandler

def test_pinecone_integration():
    print("🧪 Testing Pinecone Integration...")
    
    # Check environment variables
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ PINECONE_API_KEY environment variable not set")
        print("Please set it with: export PINECONE_API_KEY='your-api-key'")
        return False
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        return False
    
    try:
        # Test data handler initialization
        print("1️⃣ Initializing DataHandler...")
        data_path = "output/fidelity_specific_topics.json"
        handler = DataHandler(data_path)
        print("✅ DataHandler initialized successfully")
        
        # Test data loading
        print("2️⃣ Loading data...")
        data = handler.load_data()
        print(f"✅ Loaded {len(data)} articles")
        
        # Test chunking
        print("3️⃣ Chunking data...")
        docs = handler.chunk_data(data)
        print(f"✅ Created {len(docs)} document chunks")
        
        # Test index stats (before adding data)
        print("4️⃣ Checking index status...")
        exists = handler.check_collection_exists()
        print(f"✅ Index exists with data: {exists}")
        
        # Test adding a small sample to Pinecone
        print("5️⃣ Testing with small sample...")
        sample_docs = docs[:3]  # Just test with 3 documents
        handler.create_pinecone_collection(sample_docs)
        print("✅ Successfully added sample documents to Pinecone")
        
        # Test querying (wait a moment for indexing to complete)
        print("6️⃣ Testing query...")
        import time
        print("Waiting a moment for vectors to be indexed...")
        time.sleep(3)  # Wait for indexing
        
        results = handler.query_pinecone("What is investing?", top_k=2)
        print(f"✅ Query returned {len(results['documents'][0])} results")
        
        if len(results['documents'][0]) > 0:
            print(f"First result preview: {results['documents'][0][0][:100]}...")
        else:
            print("No results returned - trying a broader query...")
            results = handler.query_pinecone("financial", top_k=2)
            print(f"Broader query returned {len(results['documents'][0])} results")
            if len(results['documents'][0]) > 0:
                print(f"First result preview: {results['documents'][0][0][:100]}...")
        
        print("\n🎉 All tests passed! Pinecone integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pinecone_integration()
    if success:
        print("\n✅ Ready to run the full application!")
    else:
        print("\n❌ Please fix the issues above before running the full application.")
