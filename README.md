# 🚀 LlamaIndex llms.txt Dataset Creator

> High-quality, clean documentation dataset for LlamaIndex

## ✨ What This Does

This project creates a curated `llms.txt` dataset from LlamaIndex documentation with intelligent filtering and cleaning to ensure maximum quality for language model training.

## 🔧 Data Processing Pipeline

### Pre-Processing
- **Smart File Sorting**: Prioritizes shorter paths (less nested) and maintains stable alphabetical order
- **Version Detection**: Automatically identifies and separates `stable`, `latest`, and other version documentation
- **Changelog Exclusion**: Removes changelog files to focus on core documentation

### Post-Processing Quality Control
- **404 Detection**: Identifies and removes "Not Found" pages
- **Content Length Filtering**: Removes files with insufficient content (< 10 words)
- **Noise Removal**: Advanced filtering using:
  - Word frequency analysis (WordFreq library)
  - Character composition validation
  - Text encoding repair (ftfy)
  - Unicode normalization

### Final Output
- **Combined Dataset**: All quality documentation merged into a single `llms.txt`
- **Cleaned Version**: Further processed `llms.full.txt` with noise removal
- **Statistics Tracking**: Detailed reports on filtering results

## 📊 Quality Metrics

The pipeline tracks and reports:
- Total files processed
- 404 pages detected and removed
- Short content files filtered out
- Paragraphs retained after noise filtering

## 🎯 Key Features

- **Intelligent Sorting**: Documents organized by logical hierarchy
- **Multi-layer Validation**: Content quality verified at multiple stages
- **Encoding Safety**: Handles various text encodings and fixes corruption
- **Noise Intelligence**: Uses linguistic analysis to identify low-quality content
- **Progress Tracking**: Real-time processing updates with tqdm

Perfect for training language models on clean, structured LlamaIndex documentation! 🎉
