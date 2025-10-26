# YouTube Data Crawling, NLP & EDA Pipeline for LLMOps

This project automates data collection, preprocessing, and analysis from YouTube using the official Data API.  
It builds an end-to-end pipeline for **text mining, NLP preprocessing, and exploratory data analysis (EDA)**, designed for integration with LLMOps and RAG-based systems.

---

## 🚀 Features

- **Automated YouTube Data Crawling**  
  Collects metadata such as titles, descriptions, tags, and engagement metrics via YouTube Data API v3.

- **Keyword & Channel Filtering**  
  Enables topic-based crawling (e.g., "AI", "music production") and selective playlist ingestion.

- **Data Cleaning & NLP Preprocessing**  
  - Text normalization (removes emojis, URLs, HTML tags)  
  - Tokenization and stopword removal  
  - Lemmatization / stemming for English and multilingual data  
  - Ready for sentiment analysis or keyword extraction tasks  

- **Exploratory Data Analysis (EDA)**  
  - Frequency and co-occurrence analysis of keywords  
  - Engagement metrics visualization (views, likes, comments)  
  - Word cloud generation for content trends  
  - Optional correlation heatmap between metadata and performance metrics  

- **Pipeline Integration (LLMOps Ready)**  
  Data prepared for **RAG**, **semantic search**, or **fine-tuning pipelines** (LangChain / OpenAI compatible).

---

## 🧠 Tech Stack

- **Language:** Python  
- **Libraries:** `pandas`, `requests`, `tqdm`, `matplotlib`, `seaborn`, `nltk`, `spacy`, `wordcloud`, `dotenv`  
- **API:** YouTube Data API v3  
- **Optional:** `LangChain`, `OpenAI`, `SentenceTransformers` for vector-based retrieval

---

## ⚙️ Example Usage

```bash
python youtube_crawler.py --keyword "music production" --max_results 100
