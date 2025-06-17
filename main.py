import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter   # 可选

from urllib.parse import urlparse
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter
from pathlib import Path
import os
import shutil
import re

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

    OUTPUT_MD.write_text(
        "\n\n---\n\n".join(f.read_text(encoding="utf-8").strip() for f in md_files),
        encoding="utf-8"
    )

    print("✅ llms.txt saved")

def archive_version(version_tag):
    """Archive current latest to versioned directory"""
    if LATEST_DIR.exists():
        archive_dir = Path(f"versions/v{version_tag}")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files to archive
        for file in LATEST_DIR.glob("*.md"):
            shutil.copy2(file, archive_dir / file.name)
        
        # Create versioned llms.txt
        archive_llms = archive_dir / "llms.txt"
        shutil.copy2(OUTPUT_MD, archive_llms)
        
        print(f"✅ Archived version {version_tag}")

code_block = re.compile(r'```[^\n]*\n(.*?)```', re.DOTALL)
def strip_numeric(md_text):
    return code_block.sub(
        lambda match: "" if re.fullmatch(r'[\d\s]*', match.group(1)) else match.group(0),
        md_text
    )

async def main():
    # Create directories
    LATEST_DIR.mkdir(exist_ok=True)
    
    # 1️⃣ 让 Markdown 生成器把链接都丢掉
    md_gen = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,        # 把 [A](B) → A
            "skip_internal_links": True  # 干掉 #锚点
        },
        # 2️⃣ 想再去点页面杂质就挂个过滤器
        content_filter=PruningContentFilter(threshold=0.55)
    )

    # 3️⃣ 只截 MkDocs–Material 真正的正文容器
    cfg = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=4, 
            filter_chain=FilterChain([url_filter, exclude_filter]),
            include_external=False,
            # max_pages=80,
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        target_elements=["article.md-content__inner.md-typeset"],  # 视版本自行调整
        # excluded_tags=["nav", "header", "footer", "form"],    # 再保险
        word_count_threshold=20,
        markdown_generator=md_gen,
    )
    from crawl4ai.async_dispatcher import SemaphoreDispatcher  # 1️⃣ 引入 dispatcher
        
    dispatcher = SemaphoreDispatcher(max_session_permit=20)
    async with AsyncWebCrawler() as crawler:
        from urllib.parse import urlparse, unquote

        results = await crawler.arun("https://docs.llamaindex.ai/en/latest/", config=cfg, dispatcher=dispatcher)
        for i, result in enumerate(results):
            parsed = urlparse(result.url)


            path = parsed.path.strip("/")
            safe_slug = path.replace("/", ".") if path else "index"

            safe_slug = unquote(safe_slug)

            filename = f"{safe_slug}.md"
            filepath = f"latest/{filename}"

            # 去除404和空内容
            if not result.markdown  or len(result.markdown) < 10:
                print(f"Skipped empty content: {result.url}")
                continue
            if result.markdown.strip() == "# 404 - Not found":
                print(f"Skip 404 page:: {result.url}")
                continue


            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(strip_numeric(result.markdown) 
                        if result.markdown is not None 
                        else "")
            print(f"Saved: {filename}")
    
    # Combine files after crawling
    combine_markdown_files()

if __name__ == "__main__":
    asyncio.run(main())