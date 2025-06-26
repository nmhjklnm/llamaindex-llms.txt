# 🚀 LlamaIndex llms.txt Dataset Creator

## 🎯 Goal

Compress the entire LlamaIndex documentation into ~50k–100k tokens, so tools like Cursor, ChatGPT, or other LLM-based agents can efficiently load and use the docs without hitting context limits.

*Current status: 29MB dataset with automated crawling from LlamaIndex docs*

## 🗺️ Roadmap

### 1. Entropy-based Filtering
Using information complexity to remove over 80% of low-signal content (e.g. noisy webpage samples, raw base64 data, bloated HTML). Not fully stable yet but shows promising results.

### 2. Index-level Summarization  
Split docs into ~40 domain-based sections, then generate a high-density "index of indexes" that lets LLMs selectively focus on relevant sections.

### 3. Split File Strategy
- **llms.txt**: Minimal version with essential examples only
- **llm.full.txt**: Full reference content for when complete documentation is needed

## 🛠️ Installation & Setup

```bash
pip install crawl4ai pathlib
crawl4ai-setup
```

## 📁 Current Output Structure

```
llms.txt                    # Latest combined documentation dataset
versions/
  └── v0.10.0/
      ├── llms.txt         # Archived version dataset
```

## 🚀 Usage

### Local Development
```bash
python main.py
```

### Automated Workflow
- Daily monitoring of LlamaIndex versions via PyPI API
- Auto-crawl on version updates with smart change detection
- Archive historical versions and create tagged releases
- Manual trigger available via GitHub Actions UI

---

*Perfect for maintaining up-to-date, clean LlamaIndex documentation datasets for language model training! 🎉*


