#!/usr/bin/env python3
"""
本地测试脚本 - 用于调试和验证爬取功能
"""
import asyncio
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from main import main, get_current_version, update_version, archive_version

def test_version_functions():
    """测试版本管理函数"""
    print("🧪 测试版本管理函数...")
    
    # 测试版本更新
    test_version = "0.10.0"
    update_version(test_version)
    
    # 测试版本读取
    current = get_current_version()
    print(f"当前版本: {current}")
    
    # 测试归档功能（如果有现有内容的话）
    llms_file = Path("llms.txt")
    if llms_file.exists():
        print("发现现有 llms.txt，测试归档功能...")
        archive_version("test-archive")
    else:
        print("未发现现有 llms.txt，跳过归档测试")

async def test_crawl():
    """测试爬取功能"""
    print("🕷️ 开始测试爬取功能...")
    print("这可能需要几分钟时间...")
    
    try:
        await main()
        print("✅ 爬取测试完成")
        
        # 检查输出文件
        llms_file = Path("llms.txt")
        latest_dir = Path("latest")
        
        if llms_file.exists():
            size = llms_file.stat().st_size
            print(f"📄 llms.txt 生成成功，大小: {size:,} 字节")
        else:
            print("❌ llms.txt 未生成")
            
        if latest_dir.exists():
            md_files = list(latest_dir.glob("*.md"))
            print(f"📁 latest/ 目录包含 {len(md_files)} 个 .md 文件")
        else:
            print("❌ latest/ 目录未创建")
            
    except Exception as e:
        print(f"❌ 爬取过程中出错: {e}")
        import traceback
        traceback.print_exc()

def show_environment():
    """显示环境信息"""
    print("🔧 环境信息:")
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {Path.cwd()}")
    
    try:
        import crawl4ai
        print(f"crawl4ai 版本: {crawl4ai.__version__}")
    except ImportError:
        print("❌ crawl4ai 未安装")
    except AttributeError:
        print("crawl4ai 已安装（版本信息不可用）")

async def main_test():
    """主测试函数"""
    print("=" * 50)
    print("🚀 LlamaIndex 爬虫本地测试")
    print("=" * 50)
    
    show_environment()
    print()
    
    test_version_functions()
    print()
    
    # 询问是否运行完整爬取测试
    response = input("是否运行完整爬取测试？这可能需要几分钟 (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        await test_crawl()
    else:
        print("跳过爬取测试")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(main_test())
