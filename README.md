# YouTube Data Crawler & Analytics Pipeline for LLMOps

This project automates YouTube data collection and preprocessing for use in downstream analytics and LLM-based applications.  
It demonstrates end-to-end data engineering — from API integration to structured dataset generation and RAG-ready output.

---

## 🚀 Features

- **Automated YouTube Data Crawling**  
  Uses the official YouTube Data API to fetch video metadata (titles, tags, descriptions, and statistics).

- **Keyword-based Channel/Playlist Search**  
  Dynamically retrieves videos related to specified topics or playlists.

- **Data Cleaning & Preprocessing**  
  Removes noise (emojis, URLs, etc.), normalizes text, and converts JSON to tabular format for downstream ML use.

- **Pipeline Integration**  
  Prepared data can be connected to vector databases or LLM RAG pipelines for content retrieval or fine-tuning tasks.

- **Extensible Architecture**  
  Easily adaptable for additional APIs (e.g., Meta Ad Library, TikTok Data API).

---

## 🧠 Tech Stack

- **Language:** Python  
- **Libraries:** `requests`, `pandas`, `tqdm`, `json`, `dotenv`  
- **API:** YouTube Data API v3  
- **Optional:** OpenAI / LangChain for RAG integration

---

## 🧩 Example Usage

```bash
python youtube_crawler.py --keyword "music production" --max_results 100
