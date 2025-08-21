# Fidelity Financial Learning Assistant - Project Structure

## 📁 **ESSENTIAL FILES** (Required for deployment)

### **Core Application Files**
- ✅ **`app.py`** - Main Streamlit application interface
- ✅ **`data_handler.py`** - Pinecone vector database management
- ✅ **`utils.py`** - Helper functions for prompts and responses
- ✅ **`requirements.txt`** - Python dependencies
- ✅ **`README.md`** - Setup and deployment instructions

### **Data Files**
- ✅ **`output/fidelity_full_learning_center.json`** - Comprehensive scraped articles (55 articles)

### **Setup Files**
- ✅ **`setup_keys.py`** - Create .env file with API keys
- ✅ **`load_env.sh`** - Load environment variables
- ⚠️ **`.env`** - API keys (create but DON'T commit to git)

---

## 📁 **OPTIONAL FILES** (For development/testing)

### **Alternative Scrapers** (Choose one)
- 🔧 **`scraper_full_learning_center.py`** - **RECOMMENDED** (comprehensive scraper)
- 🔧 `scraper_learning_center.py` - Basic Learning Center scraper
- 🔧 `scraper_comprehensive.py` - Viewpoints-focused scraper
- 🔧 `scraper.py` - Original scraper

### **Testing & Setup**
- 🧪 **`test_pinecone.py`** - Test Pinecone integration
- 🔧 `setup_env.py` - Interactive environment setup

### **Legacy Data Files** (Can be removed)
- 🗂️ `output/fidelity_articles.json` - Old data
- 🗂️ `output/fidelity_specific_topics.json` - Old data
- 🗂️ `output/fidelity_improved_articles.json` - Old data
- 🗂️ `output/fidelity_comprehensive_articles.json` - Old data
- 🗂️ `output/fidelity_learning_center_articles.json` - Old data

---

## 🚀 **MINIMAL DEPLOYMENT PACKAGE**

For a clean deployment, you only need:

```
project/
├── app.py                                    # Main app
├── data_handler.py                           # Database handler
├── utils.py                                  # Helper functions
├── requirements.txt                          # Dependencies
├── README.md                                 # Instructions
├── setup_keys.py                            # API key setup
├── load_env.sh                              # Environment loader
├── scraper_full_learning_center.py          # Data collection
└── output/
    └── fidelity_full_learning_center.json   # Article data
```

**Total: 8 essential files + 1 data file**

---

## 🧹 **CLEANUP RECOMMENDATIONS**

### **Safe to Delete:**
```bash
# Remove old scrapers (keep only the comprehensive one)
rm scraper.py scraper_improved.py scraper_comprehensive.py
rm scraper_explorer.py scraper_learning_center.py

# Remove old data files
rm output/fidelity_articles.json
rm output/fidelity_specific_topics.json  
rm output/fidelity_improved_articles.json
rm output/fidelity_comprehensive_articles.json
rm output/fidelity_learning_center_articles.json

# Remove test files (optional)
rm test_pinecone.py test_with_env.py setup_env.py
```

### **Keep for Production:**
- All files in the "ESSENTIAL FILES" section
- `scraper_full_learning_center.py` (for data updates)
- `output/fidelity_full_learning_center.json` (current dataset)

---

## 📋 **DEPENDENCY VERSIONS**

Current `requirements.txt` should include:
```
streamlit
pinecone
langchain-openai
langchain-community
langchain-pinecone
beautifulsoup4
requests
tiktoken
python-dotenv
```

---

## 🔐 **SECURITY NOTES**

- ⚠️ **NEVER commit `.env` file** to version control
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables for API keys
- ✅ Include `.env.example` with placeholder values

---

## 📊 **CURRENT DATA STATS**

- **Articles**: 55 comprehensive Learning Center articles
- **Categories**: 5 main categories (Financial Essentials, Life Events, Investing & Trading, Investment Products, Other)
- **Vector Chunks**: 196 document chunks in Pinecone
- **Coverage**: Complete Fidelity Learning Center content
