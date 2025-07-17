#!/usr/bin/env python3
"""
Confluence APIの使用例
"""

import json
import os
from confluence_api import ConfluenceAPI

# 環境変数を読み込み（dotenvが利用可能な場合）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenvがインストールされていません。環境変数を直接設定してください。")

def example_get_all_pages():
    """
    スペース内のすべてのページを取得する例
    """
    print("=== スペース内のすべてのページを取得 ===")
    
    # 環境変数を安全に取得
    base_url = os.getenv('CONFLUENCE_BASE_URL', '')
    username = os.getenv('CONFLUENCE_USERNAME', '')
    api_token = os.getenv('CONFLUENCE_API_TOKEN', '')
    
    confluence = ConfluenceAPI(
        base_url=base_url,
        username=username,
        api_token=api_token
    )
    
    space_key = os.getenv('CONFLUENCE_SPACE_KEY', 'DEMO')
    
    try:
        # スペースの情報を取得
        space_info = confluence.get_space_info(space_key)
        print(f"スペース: {space_info.get('name')} ({space_info.get('key')})")
        
        # スペース内のコンテンツを取得
        content = confluence.get_space_content(space_key, limit=50)
        
        print(f"\n取得したコンテンツ数: {content.get('size', 0)}")
        print(f"総コンテンツ数: {content.get('_expandable', {}).get('totalSize', 'Unknown')}")
        
        # ページのみをフィルタリング
        pages = [item for item in content.get('results', []) if item.get('type') == 'page']
        
        print(f"\nページ数: {len(pages)}")
        
        for i, page in enumerate(pages, 1):
            extracted = confluence.extract_page_content(page)
            print(f"\n{i}. {extracted['title']}")
            print(f"   ID: {extracted['id']}")
            print(f"   ステータス: {extracted['status']}")
            print(f"   バージョン: {extracted['version']}")
            print(f"   URL: {extracted['url']}")
            
            # コンテンツの最初の100文字を表示
            content_preview = extracted['content'][:100].replace('\n', ' ').strip()
            if content_preview:
                print(f"   プレビュー: {content_preview}...")
        
    except Exception as e:
        print(f"エラー: {e}")

def example_search_pages():
    """
    ページを検索する例
    """
    print("\n=== ページ検索の例 ===")
    
    # 環境変数を安全に取得
    base_url = os.getenv('CONFLUENCE_BASE_URL', '')
    username = os.getenv('CONFLUENCE_USERNAME', '')
    api_token = os.getenv('CONFLUENCE_API_TOKEN', '')
    
    confluence = ConfluenceAPI(
        base_url=base_url,
        username=username,
        api_token=api_token
    )
    
    space_key = os.getenv('CONFLUENCE_SPACE_KEY', 'DEMO')
    
    try:
        # キーワード検索
        search_term = "documentation"
        print(f"検索キーワード: '{search_term}'")
        
        results = confluence.search_content(search_term, limit=10)
        
        print(f"検索結果数: {results.get('size', 0)}")
        
        for i, result in enumerate(results.get('results', []), 1):
            print(f"\n{i}. {result.get('title')}")
            print(f"   タイプ: {result.get('type')}")
            print(f"   スペース: {result.get('space', {}).get('name', 'Unknown')}")
            print(f"   ステータス: {result.get('status')}")
            
            # 結果の詳細情報を取得
            if result.get('type') == 'page':
                page_detail = confluence.get_page_content(result.get('id'))
                extracted = confluence.extract_page_content(page_detail)
                print(f"   最終更新: {extracted['updated']}")
        
    except Exception as e:
        print(f"エラー: {e}")

def example_get_page_hierarchy():
    """
    ページ階層を取得する例
    """
    print("\n=== ページ階層の取得 ===")
    
    # 環境変数を安全に取得
    base_url = os.getenv('CONFLUENCE_BASE_URL', '')
    username = os.getenv('CONFLUENCE_USERNAME', '')
    api_token = os.getenv('CONFLUENCE_API_TOKEN', '')
    
    confluence = ConfluenceAPI(
        base_url=base_url,
        username=username,
        api_token=api_token
    )
    
    space_key = os.getenv('CONFLUENCE_SPACE_KEY', 'DEMO')
    
    try:
        # スペースのコンテンツを取得
        content = confluence.get_space_content(space_key, limit=20)
        
        # トップレベルのページを取得
        top_level_pages = [item for item in content.get('results', []) 
                          if item.get('type') == 'page' and not item.get('ancestors')]
        
        print(f"トップレベルページ数: {len(top_level_pages)}")
        
        for page in top_level_pages:
            print(f"\n📄 {page.get('title')}")
            
            # 子ページを取得
            children = confluence.get_page_children(page.get('id'), limit=10)
            
            for child in children.get('results', []):
                print(f"  └─ 📄 {child.get('title')}")
                
                # 孫ページを取得
                grandchildren = confluence.get_page_children(child.get('id'), limit=5)
                for grandchild in grandchildren.get('results', []):
                    print(f"    └─ 📄 {grandchild.get('title')}")
        
    except Exception as e:
        print(f"エラー: {e}")

def example_export_page_content():
    """
    ページコンテンツをエクスポートする例
    """
    print("\n=== ページコンテンツのエクスポート ===")
    
    # 環境変数を安全に取得
    base_url = os.getenv('CONFLUENCE_BASE_URL', '')
    username = os.getenv('CONFLUENCE_USERNAME', '')
    api_token = os.getenv('CONFLUENCE_API_TOKEN', '')
    
    confluence = ConfluenceAPI(
        base_url=base_url,
        username=username,
        api_token=api_token
    )
    
    space_key = os.getenv('CONFLUENCE_SPACE_KEY', 'DEMO')
    
    try:
        # スペースのコンテンツを取得
        content = confluence.get_space_content(space_key, limit=5)
        
        export_data = []
        
        for page in content.get('results', []):
            if page.get('type') == 'page':
                # ページの詳細を取得
                page_detail = confluence.get_page_content(page.get('id'))
                extracted = confluence.extract_page_content(page_detail)
                
                # エクスポート用データを作成
                export_item = {
                    'title': extracted['title'],
                    'id': extracted['id'],
                    'space_key': extracted['space_key'],
                    'content': extracted['content'],
                    'version': extracted['version'],
                    'created': extracted['created'],
                    'updated': extracted['updated'],
                    'url': extracted['url']
                }
                
                export_data.append(export_item)
                
                print(f"📄 {extracted['title']} - エクスポート完了")
        
        # JSONファイルに保存
        with open('confluence_export.json', 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ {len(export_data)}ページを confluence_export.json にエクスポートしました")
        
    except Exception as e:
        print(f"エラー: {e}")

def main():
    """
    メイン関数
    """
    print("Confluence API 使用例")
    print("=" * 50)
    
    # 環境変数の確認
    required_vars = ['CONFLUENCE_BASE_URL', 'CONFLUENCE_USERNAME', 'CONFLUENCE_API_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  以下の環境変数が設定されていません:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n.envファイルを設定するか、環境変数を直接設定してください。")
        return
    
    # 各例を実行
    example_get_all_pages()
    example_search_pages()
    example_get_page_hierarchy()
    example_export_page_content()
    
    print("\n✅ すべての例が完了しました")

if __name__ == "__main__":
    main() 