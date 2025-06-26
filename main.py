import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter   # optional

from urllib.parse import urlparse
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter
from pathlib import Path
import os
import shutil
import re
import unicodedata
from wordfreq import zipf_frequency
from ftfy import fix_text
from tqdm.auto import tqdm

# Update filters to match LangGraph documentation structure
url_filter = URLPatternFilter(patterns=["*docs.llamaindex.ai*"], reverse=False)
# Keep excluding unwanted patterns
exclude_filter = URLPatternFilter(patterns=["*docs.llamaindex.ai/en/stable/*",
                                            "*wiki*",
                                            "*cloud*", "*.js", "*.css", "*.png", "*.jpg",
                                              "*.gif"], 
                                            reverse=True)


LATEST_DIR, OUTPUT_MD = Path("latest"), Path("llms.txt")

def sort_key(p: Path):
    parts = p.stem.split(".")          
    return len(parts), parts           

def combine_markdown_files():
    """Combine all markdown files into llms.txt"""
    md_files = sorted(
        (f for f in LATEST_DIR.glob("*.md") if "changelog" not in f.stem.lower()),  # skip changelog 
        key=sort_key
    )

    if not md_files:
        print("⚠️ No markdown files found for combining")
        return

    print(f"📄 Preparing to combine {len(md_files)} files:")
    for f in md_files[:5]:  # Only show first 5 file names
        print(f"  - {f.name}")
    if len(md_files) > 5:
        print(f"  ... and {len(md_files) - 5} more files")

    combined_content = []
    for f in md_files:
        try:
            content = f.read_text(encoding="utf-8").strip()
            if content:
                combined_content.append(content)
        except Exception as e:
            print(f"⚠️ Error reading file {f.name}: {e}")

    if combined_content:
        OUTPUT_MD.write_text(
            "\n\n---\n\n".join(combined_content),
            encoding="utf-8"
        )
        print(f"✅ llms.txt saved successfully, containing {len(combined_content)} documents")
    else:
        print("❌ No valid content to combine")

def archive_version(version_tag):
    """Archive current latest to versioned directory"""
    if not OUTPUT_MD.exists():
        print(f"⚠️ No llms.txt to archive for version {version_tag}")
        return
        
    archive_dir = Path(f"versions/v{version_tag}")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy current llms.txt to versioned directory
    archive_llms = archive_dir / "llms.txt"
    shutil.copy2(OUTPUT_MD, archive_llms)
    
    # Also copy individual markdown files if they exist
    if LATEST_DIR.exists():
        for file in LATEST_DIR.glob("*.md"):
            shutil.copy2(file, archive_dir / file.name)
    
    print(f"✅ Archived version {version_tag} to {archive_dir}")

def get_current_version():
    """Get current version from LAST_VERSION file"""
    version_file = Path("LAST_VERSION")
    if version_file.exists():
        return version_file.read_text().strip()
    return None

def update_version(version_tag):
    """Update LAST_VERSION file with new version"""
    version_file = Path("LAST_VERSION")
    version_file.write_text(version_tag)
    print(f"✅ Updated version to {version_tag}")

code_block = re.compile(r'```[^\n]*\n(.*?)```', re.DOTALL)
def strip_numeric(md_text):
    return code_block.sub(
        lambda match: "" if re.fullmatch(r'[\d\s]*', match.group(1)) else match.group(0),
        md_text
    )

def is_noise(text: str,
             min_len: int = 25,
             word_freq_th: float = 2.0,
             valid_ratio_th: float = 0.4,
             alpha_ratio_th: float = 0.3) -> bool:
    """
    Returns True if content should be discarded
    - min_len: Discard paragraphs that are too short
    - word_freq_th: Using wordfreq's Zipf frequency, common words > 2
    - valid_ratio_th: Common words / total words ratio threshold
    - alpha_ratio_th: Alphanumeric character ratio threshold (to remove ====, ------ etc.)
    """
    t = text.strip()
    if len(t) < min_len:
        return True

    # All symbols/non-alphanumeric characters
    alpha_num = sum(ch.isalnum() for ch in t)
    if alpha_num / len(t) < alpha_ratio_th:
        return True

    # Word-level statistics (only check English alphabet words; can extend for Chinese or other languages)
    words = re.findall(r"[A-Za-z]+", t.lower())
    if words:
        valid = sum(zipf_frequency(w, "en") >= word_freq_th for w in words)
        if valid / len(words) < valid_ratio_th:
            return True
    return False

def filter_content():
    """Filter noise content from llms.txt"""
    if not OUTPUT_MD.exists():
        print("⚠️ llms.txt does not exist, skipping content filtering")
        return
    
    print("🧹 Starting content filtering...")
    
    # Read the combined file
    data = OUTPUT_MD.read_text(encoding="utf-8", errors="ignore")
    paragraphs = re.split(r"\n\s*\n", data)      # Split by empty lines
    
    kept = []
    for p in tqdm(paragraphs, desc="Filtering paragraphs"):
        p = fix_text(p)                          # Fix garbled text
        if is_noise(p):
            continue
        kept.append(p.strip())
    
    # Write filtered content back to llms.txt
    OUTPUT_MD.write_text("\n\n".join(kept), encoding="utf-8")
    print(f"✅ Filtering completed, {len(kept):,} paragraphs remaining, updated {OUTPUT_MD}")

async def main():
    print("🚀 Starting LlamaIndex documentation crawling...")
    
    # Create directories
    LATEST_DIR.mkdir(exist_ok=True)
    print(f"📁 Created directory: {LATEST_DIR}")
    
    # 1️⃣ Make Markdown generator remove all links
    md_gen = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,        # Convert [A](B) → A
            "skip_internal_links": True  # Remove #anchor links
        },
        # 2️⃣ Add a filter to remove more page clutter
        content_filter=PruningContentFilter(threshold=0.55)
    )

    # 3️⃣ Only extract MkDocs–Material actual content container
    cfg = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=4, 
            filter_chain=FilterChain([url_filter, exclude_filter]),
            include_external=False,
            # max_pages=80,  # Limit page count for testing
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        target_elements=["article.md-content__inner.md-typeset"],  # Adjust according to version
        # excluded_tags=["nav", "header", "footer", "form"],    # Extra safety
        word_count_threshold=20,
        markdown_generator=md_gen,
    )
    
    try:
        from crawl4ai.async_dispatcher import SemaphoreDispatcher  # 1️⃣ Import dispatcher
        
        dispatcher = SemaphoreDispatcher(max_session_permit=20)
        print("🕷️ Initializing crawler...")
        
        async with AsyncWebCrawler() as crawler:
            from urllib.parse import urlparse, unquote

            print("📡 Starting crawl of https://docs.llamaindex.ai/en/latest/ ...")
            results = await crawler.arun("https://docs.llamaindex.ai/en/latest/", config=cfg, dispatcher=dispatcher)
            
            print(f"📋 Got {len(results)} crawl results")
            saved_count = 0
            
            for i, result in enumerate(results):
                parsed = urlparse(result.url)

                path = parsed.path.strip("/")
                safe_slug = path.replace("/", ".") if path else "index"
                safe_slug = unquote(safe_slug)

                filename = f"{safe_slug}.md"
                filepath = LATEST_DIR / filename

                # Remove 404 and empty content
                if not result.markdown or len(result.markdown) < 10:
                    print(f"⏭️ Skipping empty content: {result.url}")
                    continue
                if result.markdown.strip() == "# 404 - Not found":
                    print(f"⏭️ Skipping 404 page: {result.url}")
                    continue

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(strip_numeric(result.markdown) 
                                if result.markdown is not None 
                                else "")
                    print(f"💾 Saved: {filename}")
                    saved_count += 1
                except Exception as e:
                    print(f"❌ Error saving file {filename}: {e}")
        
        print(f"✅ Crawling completed, saved {saved_count} files")
        
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Combine files after crawling
    print("🔄 Combining files...")
    combine_markdown_files()
    
    # Filter content after combining
    filter_content()
    
    print("🎉 All done!")

if __name__ == "__main__":
    asyncio.run(main())