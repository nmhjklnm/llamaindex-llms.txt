# 🚀 LlamaIndex llms.txt Dataset Creator

> High-quality, clean documentation dataset for LlamaIndex training with automated GitHub Actions

## ✨ What This Does

This project creates a curated `llms.txt` dataset from LlamaIndex documentation with intelligent filtering, cleaning, and automated version monitoring to ensure maximum quality for language model training.

## 🛠️ Installation & Setup

### 1. Basic Installation
```bash
pip install crawl4ai pathlib
crawl4ai-setup
```

## 🤖 Automated GitHub Actions

The project includes automated workflows that:
- **Monitor LlamaIndex versions daily** via PyPI API
- **Auto-crawl on version updates** with smart change detection
- **Archive historical versions** in `versions/` directory
- **Create tagged releases** for each version
- **Maintain clean git history** with automated commits

### Manual Triggers
You can also trigger crawling manually via GitHub Actions UI with a "force crawl" option.

## 🔧 Data Processing Pipeline

### Pre-Processing
- **Smart File Sorting**: Prioritizes shorter paths (less nested) and maintains stable alphabetical order
- **Version Detection**: Automatically identifies and separates `stable`, `latest`, and other version documentation
- **Changelog Exclusion**: Removes changelog files to focus on core documentation

### Post-Processing Quality Control
- **404 Detection**: Identifies and removes "Not Found" pages
- **Content Length Filtering**: Removes files with insufficient content (< 10 words)
- **Numeric Code Block Removal**: Strips code blocks containing only numbers
- **Link Cleaning**: Removes or simplifies markdown links
- **Content Pruning**: Advanced filtering using PruningContentFilter

### Final Output
- **llms.txt**: Combined dataset of all quality documentation
- **Versioned Archives**: Historical versions preserved in `versions/v{version}/`
- **Statistics Tracking**: Detailed reports on filtering results
- 

## 📁 Output Structure

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

### GitHub Actions (Automated)
The workflow runs automatically:
- Daily at 6 AM UTC
- On new LlamaIndex releases
- Manual trigger available

Perfect for maintaining up-to-date, clean LlamaIndex documentation datasets for language model training! 🎉


