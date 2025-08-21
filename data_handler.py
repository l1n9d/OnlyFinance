from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import json
import os
import uuid
import time

class DataHandler:
    def __init__(
        self,
        data_path,
        index_name="fidelity-financial-articles",
        pinecone_api_key=None
    ):
        self.data_path = data_path
        self.index_name = index_name
        
        # Initialize Pinecone
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        if not self.pinecone_api_key:
            raise ValueError("Pinecone API key is required. Set PINECONE_API_KEY environment variable or pass it directly.")
        
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # OpenAI embeddings
        self.embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Check if index exists, create if not
        self.setup_index()

    def setup_index(self):
        """Create Pinecone index if it doesn't exist"""
        try:
            # Check if index exists
            index_info = self.pc.describe_index(self.index_name)
            print(f"Index '{self.index_name}' exists with {index_info.status.ready} status")
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            print(f"Index '{self.index_name}' does not exist. Creating it...")
            # Create index with OpenAI embedding dimensions (1536 for text-embedding-3-small)
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI text-embedding-3-small dimension
                metric="cosine",
                spec={
                    "serverless": {
                        "cloud": "aws",
                        "region": "us-east-1"
                    }
                }
            )
            
            # Wait for index to be ready
            print("Waiting for index to be ready...")
            while not self.pc.describe_index(self.index_name).status.ready:
                time.sleep(1)
            
            print(f"Index '{self.index_name}' created successfully!")
            self.index = self.pc.Index(self.index_name)

    def load_data(self):
        """Load JSON file with {title, content} or {question, answer} format"""
        with open(self.data_path, "r") as f:
            data = json.load(f)
        
        # Convert Fidelity format to expected format if needed
        if data and isinstance(data[0], dict):
            if 'title' in data[0] and 'content' in data[0]:
                # Convert from Fidelity format to expected format
                converted_data = []
                for item in data:
                    converted_data.append({
                        "question": item["title"],
                        "answer": item["content"],
                        "url": item.get("url", "")
                    })
                return converted_data
        
        return data

    def chunk_data(self, data):
        """Split answers into smaller chunks for embedding"""
        docs = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", ".", " "]
        )
        for item in data:
            question = item["question"]
            answer = item["answer"]
            url = item.get("url", "")

            # Split into chunks
            chunks = text_splitter.split_text(answer)
            for i, chunk in enumerate(chunks):
                docs.append({
                    "id": str(uuid.uuid4()),
                    "text": chunk,
                    "metadata": {
                        "source": question,
                        "url": url,
                        "chunk_index": i
                    }
                })
        return docs

    def create_pinecone_collection(self, docs):
        """Add documents to Pinecone index"""
        print(f"Adding {len(docs)} document chunks to Pinecone...")
        
        # Batch process documents
        batch_size = 100
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            
            # Generate embeddings for the batch
            texts = [doc["text"] for doc in batch]
            embeddings = self.embedding_function.embed_documents(texts)
            
            # Prepare vectors for Pinecone
            vectors = []
            for j, doc in enumerate(batch):
                vectors.append({
                    "id": doc["id"],
                    "values": embeddings[j],
                    "metadata": {
                        "text": doc["text"],
                        "source": doc["metadata"]["source"],
                        "url": doc["metadata"]["url"],
                        "chunk_index": doc["metadata"]["chunk_index"]
                    }
                })
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors)
            print(f"Processed batch {i//batch_size + 1}/{(len(docs) + batch_size - 1)//batch_size}")
        
        print("All documents added to Pinecone successfully!")

    def query_pinecone(self, query, top_k=2):
        """Query Pinecone index"""
        # Generate embedding for query
        query_embedding = self.embedding_function.embed_query(query)
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results to match what app.py expects
        documents = []
        metadatas = []
        
        for match in results["matches"]:
            documents.append(match["metadata"]["text"])
            metadatas.append({
                "source": match["metadata"]["source"],
                "url": match["metadata"]["url"],
                "score": match["score"]
            })
        
        formatted_results = {
            "documents": [documents],
            "metadatas": [metadatas]
        }
        return formatted_results

    def process_data_and_create_collection(self):
        """Full pipeline: load, chunk, embed, and save to Pinecone"""
        data = self.load_data()
        docs = self.chunk_data(data)
        self.create_pinecone_collection(docs)
        return self.index

    def delete_pinecone_collection(self):
        """Delete all vectors from Pinecone index"""
        try:
            # Get all vector IDs (this might be slow for large indexes)
            stats = self.index.describe_index_stats()
            if stats["total_vector_count"] > 0:
                self.index.delete(delete_all=True)
                print(f"Deleted all vectors from Pinecone index '{self.index_name}'")
            else:
                print("No vectors to delete from Pinecone index")
        except Exception as e:
            print(f"Error deleting vectors: {e}")

    def check_collection_exists(self):
        """Check if collection has data"""
        try:
            stats = self.index.describe_index_stats()
            return stats["total_vector_count"] > 0
        except Exception as e:
            print(f"Error checking collection: {e}")
            return False

    # For compatibility with app.py
    def query_chroma(self, query, n_results=2):
        """Compatibility method - redirects to query_pinecone"""
        return self.query_pinecone(query, top_k=n_results)