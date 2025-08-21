# Fidelity Financial Learning Assistant

A comprehensive RAG-powered chatbot that provides financial guidance using articles from Fidelity Learning Center across 5 main categories.

## 🚀 Features

- **Smart Q&A**: Ask financial questions and get answers based on Fidelity's educational content
- **Vector Search**: Uses Pinecone for fast and accurate content retrieval
- **Modern UI**: Clean Streamlit interface for easy interaction
- **Cloud Ready**: Designed for deployment on Streamlit Cloud or GCP

## 📋 Prerequisites

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Pinecone API Key**: Sign up at [Pinecone](https://www.pinecone.io/) (free tier available)

## 🛠️ Local Setup

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Keys

**Option A: Quick Setup (Recommended)**
```bash
python setup_keys.py
source load_env.sh
```

**Option B: Manual Setup**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export PINECONE_API_KEY="your-pinecone-api-key"
```

### 3. Test the Integration

```bash
# Test Pinecone integration (optional but recommended)
python test_pinecone.py

# Run the application
source load_env.sh && streamlit run app.py
```

## 🌐 Deployment Options

### Streamlit Cloud Deployment

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the main file path: `app.py`
3. **Configure Secrets**: In Streamlit Cloud dashboard, add secrets:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   PINECONE_API_KEY = "your-pinecone-api-key"
   ```

### GCP Deployment

1. **Prepare for GCP**:
   ```bash
   # Create app.yaml for Google App Engine
   # See deployment documentation for details
   ```

2. **Deploy**:
   ```bash
   gcloud app deploy
   ```

## 📁 Project Structure

```
project/
├── app.py                          # Main Streamlit application
├── data_handler.py                 # Pinecone + LangChain integration
├── scraper_full_learning_center.py # Comprehensive Learning Center scraper
├── utils.py                        # Utility functions
├── setup_keys.py                   # API key setup helper
├── load_env.sh                     # Environment loader
├── requirements.txt                # Python dependencies
├── output/
│   └── fidelity_full_learning_center.json  # 55 comprehensive articles
├── PROJECT_STRUCTURE.md           # Detailed project documentation
└── README.md                       # This file
```

## 🔧 Configuration

### Pinecone Settings
- **Index Name**: `fidelity-financial-articles`
- **Dimensions**: 1536 (OpenAI text-embedding-3-small)
- **Metric**: Cosine similarity
- **Environment**: AWS us-east-1 (free tier)

### Data Processing
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 100 characters
- **Embedding Model**: text-embedding-3-small

## 💬 Usage

1. **Start the app**: Access via web browser (usually `http://localhost:8501`)
2. **Enter API keys**: Use the sidebar to input your OpenAI and Pinecone API keys
3. **Ask questions**: Type financial questions like:
   - "How do I buy my first house?"
   - "What's the best way to save for college?"
   - "How do I manage credit card debt?"
   - "Should I invest in cryptocurrency?"
   - "What are the best retirement strategies?"
4. **Get answers**: The app will search Fidelity content and provide relevant responses

## 🔍 Data Sources

The application uses educational content scraped from:
- **Fidelity Learning Center**: https://www.fidelity.com/learning-center
- **55 Comprehensive Articles** across 5 main categories:
  - 🏦 **Financial Essentials** (9 articles): debt, taxes, estate planning
  - 🏠 **Life Events** (12 articles): college, home buying, marriage, parenting
  - 📈 **Investing & Trading** (15 articles): crypto, technical analysis, strategies
  - 💼 **Investment Products** (8 articles): stocks, bonds, ETFs, options
  - 🎯 **Other** (11 articles): smart money tips, NAV, robo advisors

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're using the virtual environment
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **API Key Errors**: Verify your API keys are correct and have sufficient credits

3. **Pinecone Connection Issues**: Check your Pinecone API key and ensure the index is created

4. **Empty Responses**: Ensure the data has been loaded into Pinecone successfully

### Test Scripts

Run the test script to verify everything is working:
```bash
python test_pinecone.py
```

## 📊 Performance

- **Vector Search**: Sub-second query responses via Pinecone
- **Content Processing**: 55 articles → 196 optimized chunks
- **Embedding Generation**: Batch processing for efficiency
- **Scalability**: Production-ready for thousands of documents

## 🔒 Security

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use secure environment variable management
- **Production**: Consider using secret management services for production deployments

## 📈 Future Enhancements

- [ ] Add more content sources beyond Fidelity
- [ ] Implement conversation memory
- [ ] Add document upload functionality
- [ ] Create admin interface for content management
- [ ] Add analytics and usage tracking

## 📄 License

This project is for educational purposes. Please respect Fidelity's terms of service when using scraped content.

---

**Note**: This application is not affiliated with Fidelity Investments. It's an educational project that demonstrates RAG implementation using publicly available content.
