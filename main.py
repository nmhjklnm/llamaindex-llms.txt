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

    if not md_files:
        print("⚠️ 没有找到 markdown 文件进行合并")
        return

    print(f"📄 准备合并 {len(md_files)} 个文件:")
    for f in md_files[:5]:  # 只显示前5个文件名
        print(f"  - {f.name}")
    if len(md_files) > 5:
        print(f"  ... 还有 {len(md_files) - 5} 个文件")

    combined_content = []
    for f in md_files:
        try:
            content = f.read_text(encoding="utf-8").strip()
            if content:
                combined_content.append(content)
        except Exception as e:
            print(f"⚠️ 读取文件 {f.name} 时出错: {e}")

    if combined_content:
        OUTPUT_MD.write_text(
            "\n\n---\n\n".join(combined_content),
            encoding="utf-8"
        )
        print(f"✅ llms.txt 保存成功，包含 {len(combined_content)} 个文档")
    else:
        print("❌ 没有有效内容可合并")

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

async def main():
    print("🚀 开始爬取 LlamaIndex 文档...")
    
    # Create directories
    LATEST_DIR.mkdir(exist_ok=True)
    print(f"📁 创建目录: {LATEST_DIR}")
    
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
            # max_pages=80,  # 限制页面数量用于测试
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        target_elements=["article.md-content__inner.md-typeset"],  # 视版本自行调整
        # excluded_tags=["nav", "header", "footer", "form"],    # 再保险
        word_count_threshold=20,
        markdown_generator=md_gen,
    )
    
    try:
        from crawl4ai.async_dispatcher import SemaphoreDispatcher  # 1️⃣ 引入 dispatcher
        
        dispatcher = SemaphoreDispatcher(max_session_permit=20)
        print("🕷️ 初始化爬虫...")
        
        async with AsyncWebCrawler() as crawler:
            from urllib.parse import urlparse, unquote

            print("📡 开始爬取 https://docs.llamaindex.ai/en/latest/ ...")
            results = await crawler.arun("https://docs.llamaindex.ai/en/latest/", config=cfg, dispatcher=dispatcher)
            
            print(f"📋 获得 {len(results)} 个爬取结果")
            saved_count = 0
            
            for i, result in enumerate(results):
                parsed = urlparse(result.url)

                path = parsed.path.strip("/")
                safe_slug = path.replace("/", ".") if path else "index"
                safe_slug = unquote(safe_slug)

                filename = f"{safe_slug}.md"
                filepath = LATEST_DIR / filename

                # 去除404和空内容
                if not result.markdown or len(result.markdown) < 10:
                    print(f"⏭️ 跳过空内容: {result.url}")
                    continue
                if result.markdown.strip() == "# 404 - Not found":
                    print(f"⏭️ 跳过404页面: {result.url}")
                    continue

                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(strip_numeric(result.markdown) 
                                if result.markdown is not None 
                                else "")
                    print(f"💾 保存: {filename}")
                    saved_count += 1
                except Exception as e:
                    print(f"❌ 保存文件 {filename} 时出错: {e}")
        
        print(f"✅ 爬取完成，保存了 {saved_count} 个文件")
        
    except Exception as e:
        print(f"❌ 爬取过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Combine files after crawling
    print("🔄 合并文件...")
    combine_markdown_files()
    print("🎉 全部完成！")

if __name__ == "__main__":
    asyncio.run(main())