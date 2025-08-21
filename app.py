import streamlit as st
import os
from data_handler import DataHandler
from utils import build_prompt, get_openai_response
import time

# Page configuration
st.set_page_config(
    page_title="OnlyFinance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Main header with emoji and description
st.title("💰 OnlyFinance")
# Welcome section with better formatting
#st.markdown("""
#<div style="
#    background-color: #f0f8ff; 
#    color: #000000; 
#    padding: 20px; 
#    border-radius: 10px; 
#    margin-bottom: 20px;">
    
#    <h4 style="color: #003366; margin-top: 0;">🎓 Your Personal Financial Learning Companion</h4>
#    <p>Ask me anything about investing, retirement planning, debt management, home buying, college savings, and more! 
#    I'm powered by <strong>comprehensive articles and viewpoints</strong> from Fidelity's Learning Center.</p>
#</div>
#""", unsafe_allow_html=True)


# Expandable section for examples
with st.expander("💡 **Try asking me about these topics:**"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        🏠 *"How do I buy my first house?"*
        
        🎓 *"What's the best way to save for college?"*
        
        💳 *"How do I manage credit card debt?"*
        """)
    
    with col2:
        st.markdown("""
        📈 *"Should I invest in cryptocurrency?"*
        
        🏦 *"What are ETFs and how do they work?"*
        
        👴 *"How much should I save for retirement?"*
        """)

# Check if API keys are available (from .env file)
missing_keys = []
if not os.environ.get("OPENAI_API_KEY"):
    missing_keys.append("OPENAI_API_KEY")
if not os.environ.get("PINECONE_API_KEY"):
    missing_keys.append("PINECONE_API_KEY")

if missing_keys:
    st.error(f"""
    🔑 **Missing API Keys**: {', '.join(missing_keys)}
    
    **To fix this:**
    1. Run `python setup_keys.py` to create your .env file
    2. Then restart with: `source load_env.sh && streamlit run app.py`
    
    Or set environment variables manually:
    ```bash
    export OPENAI_API_KEY="your-key"
    export PINECONE_API_KEY="your-key"
    ```
    """)
    st.stop()

# Data loading and setup (only after API keys are provided)
data_path = "output/fidelity_full_learning_center.json"  # Using comprehensive Fidelity Learning Center articles

# Initialize DataHandler in session state if it doesn't exist
if "data_handler" not in st.session_state:
    with st.spinner("Initializing Pinecone connection..."):
        st.session_state["data_handler"] = DataHandler(data_path)

data_handler = st.session_state["data_handler"]

# Initialize collection in session state if it doesn't exist
if "collection" not in st.session_state:
    # Check if the Pinecone index has data
    with st.spinner("🔍 Checking for existing financial data..."):
        if data_handler.check_collection_exists():
            # Show collapsible admin section in sidebar only if needed
            with st.sidebar:
                st.markdown("### 🔧 Admin Controls")
                use_existing = st.radio(
                    "Data Management:",
                    ["Use existing data", "Recreate collection"],
                    index=0,
                    help="Recreate only if you want to refresh the financial articles database"
                )
            
            if use_existing == "Recreate collection":
                with st.spinner("🔄 Refreshing financial articles database..."):
                    data_handler.delete_pinecone_collection()
                    time.sleep(2)
                    collection = data_handler.process_data_and_create_collection()
                st.session_state["collection"] = collection
                st.success("✅ Financial articles database refreshed!")
            else:
                st.session_state["collection"] = data_handler.index
                st.success("✅ Connected to existing financial knowledge base!")
        else:
            with st.spinner("📚 Setting up your financial knowledge base for the first time..."):
                collection = data_handler.process_data_and_create_collection()
            st.session_state["collection"] = collection
            st.success("✅ Financial knowledge base ready! You can now ask me anything about finance.")

# Chat interface with welcome message
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show welcome message if no conversation yet
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("""
        👋 **Welcome! Only Finance here.**
        
        I have access to **comprehensive articles and viewpoints** covering:  

        • 🏦 Financial Essentials (debt, taxes, budgeting)  
        • 🏠 Life Events (home buying, college, marriage)  
        • 📈 Investing & Trading (stocks, crypto, strategies)  
        • 💼 Investment Products (ETFs, bonds, options)  
        • 🎯 Smart Money Tips & Advanced Topics  
        
        **What would you like to learn about today?** 💭
        """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input with better placeholder
if prompt := st.chat_input("💬 Ask me about investing, budgeting, retirement, home buying, college savings, or any financial topic..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # RAG flow with better status messages
    with st.spinner("🔍 Searching through Fidelity's financial articles..."):
        results = data_handler.query_pinecone(prompt)  # Fixed: was query_chroma
        if results["documents"] and results["metadatas"]:
            retrieved_chunks = results["documents"][0]
            retrieved_metadatas = results["metadatas"][0]
        else:
            retrieved_chunks = []
            retrieved_metadatas = []

    full_prompt = build_prompt(prompt, retrieved_chunks)
    with st.spinner("🤖 Crafting your personalized financial guidance..."):
        response = get_openai_response(full_prompt, retrieved_metadatas)

    # Display response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Sidebar stats and info (only show if there's data)
if "collection" in st.session_state:
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Knowledge Base Stats")
        
        # Load data to show stats
        try:
            import json
            with open(data_path, 'r') as f:
                articles = json.load(f)
            
            # Count articles by category
            categories = {}
            for article in articles:
                category = article.get('category', 'Other')
                categories[category] = categories.get(category, 0) + 1
            
            st.metric("Total Articles", len(articles))
            st.metric("Categories", len(categories))
            
            # Show category breakdown
            st.markdown("**Categories:**")
            for category, count in categories.items():
                st.text(f"• {category}: {count}")
                
        except:
            st.metric("Status", "✅ Ready")
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
            <p>💰 OnlyFinance</p>
            <p>Powered by RAG + Pinecone + OpenAI</p>
            <p><em>Educational content from Fidelity Learning Center</em></p>
        </div>
        """, unsafe_allow_html=True)