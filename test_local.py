#!/usr/bin/env python3
"""
Local test script - for debugging and validating crawling functionality
"""
import asyncio
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import main, get_current_version, update_version, archive_version

def test_version_functions():
    """Test version management functions"""
    print("🧪 Testing version management functions...")
    
    # Test version update
    test_version = "0.10.0"
    update_version(test_version)
    
    # Test version reading
    current = get_current_version()
    print(f"Current version: {current}")
    
    # Test archive functionality (if existing content exists)
    llms_file = Path("llms.txt")
    if llms_file.exists():
        print("Found existing llms.txt, testing archive functionality...")
        archive_version("test-archive")
    else:
        print("No existing llms.txt found, skipping archive test")

async def test_crawl():
    """Test crawling functionality"""
    print("🕷️ Starting crawling functionality test...")
    print("This may take a few minutes...")
    
    try:
        await main()
        print("✅ Crawling test completed")
        
        # Check output files
        llms_file = Path("llms.txt")
        latest_dir = Path("latest")
        
        if llms_file.exists():
            size = llms_file.stat().st_size
            print(f"📄 llms.txt generated successfully, size: {size:,} bytes")
        else:
            print("❌ llms.txt not generated")
            
        if latest_dir.exists():
            md_files = list(latest_dir.glob("*.md"))
            print(f"📁 latest/ directory contains {len(md_files)} .md files")
        else:
            print("❌ latest/ directory not created")
            
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        import traceback
        traceback.print_exc()

def show_environment():
    """Show environment information"""
    print("🔧 Environment information:")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {Path.cwd()}")
    
    try:
        import crawl4ai
        print(f"crawl4ai version: {crawl4ai.__version__}")
    except ImportError:
        print("❌ crawl4ai not installed")
    except AttributeError:
        print("crawl4ai installed (version info unavailable)")

async def main_test():
    """Main test function"""
    print("=" * 50)
    print("🚀 LlamaIndex Crawler Local Test")
    print("=" * 50)
    
    show_environment()
    print()
    
    test_version_functions()
    print()
    
    # Ask whether to run full crawling test
    response = input("Run full crawling test? This may take a few minutes (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        await test_crawl()
    else:
        print("Skipping crawling test")
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    asyncio.run(main_test())
