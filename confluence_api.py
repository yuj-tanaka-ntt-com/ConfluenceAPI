import requests
import json
import base64
import warnings
from typing import Dict, List, Optional
import os
from datetime import datetime

# SSL証明書検証を無効化している警告を抑制
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class ConfluenceAPI:
    """
    Confluence APIを使用してコンテンツを取得するクラス
    """
    
    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Confluence APIクライアントを初期化
        
        Args:
            base_url: ConfluenceのベースURL (例: https://your-domain.atlassian.net)
            username: ユーザー名またはメールアドレス
            api_token: APIトークン
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.session = requests.Session()
        
        # Basic認証の設定
        credentials = f"{username}:{api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.session.headers.update({
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_space_content(self, space_key: str, limit: int = 25) -> Dict:
        """
        指定されたスペースのコンテンツを取得
        
        Args:
            space_key: スペースキー
            limit: 取得するコンテンツの最大数
            
        Returns:
            APIレスポンスの辞書
        """
        url = f"{self.base_url}/rest/api/content"
        params = {
            'spaceKey': space_key,
            'limit': limit,
            'expand': 'body.storage,version'
        }
        
        response = self.session.get(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    
    def get_page_content(self, page_id: str) -> Dict:
        """
        指定されたページの詳細を取得
        
        Args:
            page_id: ページID
            
        Returns:
            APIレスポンスの辞書
        """
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {
            'expand': 'body.storage,version,children.page'
        }
        
        response = self.session.get(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    
    def search_content(self, query: str, cql: Optional[str] = None, limit: int = 25) -> Dict:
        """
        コンテンツを検索
        
        Args:
            query: 検索クエリ
            cql: CQL (Confluence Query Language) クエリ
            limit: 取得する結果の最大数
            
        Returns:
            APIレスポンスの辞書
        """
        url = f"{self.base_url}/rest/api/content/search"
        params = {
            'limit': str(limit)
        }
        
        if cql:
            params['cql'] = cql
        else:
            params['query'] = query
        
        response = self.session.get(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    
    def get_page_children(self, page_id: str, limit: int = 25) -> Dict:
        """
        指定されたページの子ページを取得
        
        Args:
            page_id: ページID
            limit: 取得する子ページの最大数
            
        Returns:
            APIレスポンスの辞書
        """
        url = f"{self.base_url}/rest/api/content/{page_id}/child/page"
        params = {
            'limit': limit,
            'expand': 'body.storage,version'
        }
        
        response = self.session.get(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    
    def get_space_info(self, space_key: str) -> Dict:
        """
        スペースの情報を取得
        
        Args:
            space_key: スペースキー
            
        Returns:
            APIレスポンスの辞書
        """
        url = f"{self.base_url}/rest/api/space/{space_key}"
        
        response = self.session.get(url, verify=False)
        response.raise_for_status()
        return response.json()
    
    def extract_page_content(self, page_data: Dict) -> Dict:
        """
        ページデータからコンテンツを抽出
        
        Args:
            page_data: APIから取得したページデータ
            
        Returns:
            抽出されたコンテンツの辞書
        """
        return {
            'id': page_data.get('id'),
            'title': page_data.get('title'),
            'type': page_data.get('type'),
            'status': page_data.get('status'),
            'space_key': page_data.get('space', {}).get('key'),
            'space_name': page_data.get('space', {}).get('name'),
            'content': page_data.get('body', {}).get('storage', {}).get('value', ''),
            'version': page_data.get('version', {}).get('number'),
            'created': page_data.get('created'),
            'updated': page_data.get('version', {}).get('when'),
            'url': f"{self.base_url}/wiki{page_data.get('_links', {}).get('webui', '')}"
        }

    # --- v2 API ---
    def get_space_id_by_key_v2(self, space_key: str) -> Optional[str]:
        """
        スペースキーからスペースIDを取得（v2 API）
        """
        url = f"{self.base_url}/wiki/api/v2/spaces?keys={space_key}"
        resp = self.session.get(url, verify=False)
        resp.raise_for_status()
        data = resp.json()
        if data and data.get('results'):
            return data['results'][0]['id']
        return None

    def get_space_pages_v2(self, space_id: str, limit: int = 25) -> dict:
        """
        スペースIDからページ一覧を取得（v2 API）
        """
        url = f"{self.base_url}/wiki/api/v2/spaces/{space_id}/pages?limit={limit}"
        resp = self.session.get(url, verify=False)
        resp.raise_for_status()
        return resp.json()

    def search_pages_v2(self, query: str, limit: int = 25) -> dict:
        """
        ページをキーワードで検索（v2 API）
        """
        url = f"{self.base_url}/wiki/api/v2/pages?limit={limit}&q={query}"
        resp = self.session.get(url, verify=False)
        resp.raise_for_status()
        return resp.json()

    def get_page_children_v2(self, page_id: str, limit: int = 10) -> dict:
        """
        ページIDから子ページ一覧を取得（v2 API）
        """
        url = f"{self.base_url}/wiki/api/v2/pages/{page_id}/children?limit={limit}"
        resp = self.session.get(url, verify=False)
        resp.raise_for_status()
        return resp.json()

    def get_all_pages_in_space_v2(self, space_id: str) -> list:
        """
        スペースID内の全ページをページネーションで取得（v2 API）
        """
        all_pages = []
        start = 0
        limit = 50
        while True:
            url = f"{self.base_url}/wiki/api/v2/spaces/{space_id}/pages?limit={limit}&start={start}"
            resp = self.session.get(url, verify=False)
            resp.raise_for_status()
            data = resp.json()
            results = data.get('results', [])
            all_pages.extend(results)
            if not data.get('_links', {}).get('next'):
                break
            start += limit
        return all_pages

    def build_page_tree(self, pages: list) -> list:
        """
        ページリストから階層構造（ツリー）を構築
        """
        page_dict = {page['id']: page for page in pages}
        tree = []
        for page in pages:
            parent_id = page.get('parentId')
            if parent_id and parent_id in page_dict:
                parent = page_dict[parent_id]
                if 'children' not in parent:
                    parent['children'] = []
                parent['children'].append(page)
            else:
                tree.append(page)
        return tree

    def get_descendants_by_ancestor_v1(self, ancestor_id: str, limit: int = 50) -> list:
        """
        v1 APIのCQL検索でancestor=ページIDの全ての子孫ページを取得（孫ページ以降も含む）
        """
        all_results = []
        start = 0
        
        print(f"Debug: v1 descendants API 開始 - ancestor_id: {ancestor_id}")
        
        while True:
            # URLエンコードしてCQLクエリを安全に送信
            import urllib.parse
            cql_query = f"ancestor={ancestor_id}"
            encoded_cql = urllib.parse.quote(cql_query)
            url = f"{self.base_url}/rest/api/content?cql={encoded_cql}&limit={limit}&start={start}&expand=body.storage,version,ancestors"
            print(f"Debug: リクエスト送信 - URL: {url}")
            
            resp = self.session.get(url, verify=False)
            print(f"Debug: レスポンスステータス: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"Debug: エラーレスポンス - {resp.text}")
                # 404エラーの場合、別のアプローチを試す
                if resp.status_code == 404:
                    print("Debug: 404エラー - 別のアプローチを試します")
                    return self.get_descendants_alternative(ancestor_id, limit)
                resp.raise_for_status()
            
            data = resp.json()
            results = data.get('results', [])
            all_results.extend(results)
            
            print(f"Debug: 取得した結果数: {len(results)}, 累計: {len(all_results)}")
            
            # 次のページがあるかチェック
            if not data.get('_links', {}).get('next'):
                print("Debug: 次のページなし - 終了")
                break
            start += limit
        
        print(f"Debug: v1 descendants API 完了 - 総結果数: {len(all_results)}")
        return all_results

    def get_descendants_alternative(self, ancestor_id: str, limit: int = 50) -> list:
        """
        代替方法: v2 APIを使用して階層的に子ページを取得
        """
        print(f"Debug: 代替方法開始 - ancestor_id: {ancestor_id}")
        
        all_results = []
        to_process = [ancestor_id]
        processed = set()
        
        while to_process:
            current_id = to_process.pop(0)
            if current_id in processed:
                continue
                
            processed.add(current_id)
            print(f"Debug: 処理中 - page_id: {current_id}")
            
            try:
                # v2 APIで子ページを取得
                children = self.get_children_v2(current_id, limit=limit)
                all_results.extend(children)
                
                # 子ページのIDを次の処理対象に追加
                for child in children:
                    child_id = child.get('id')
                    if child_id and child_id not in processed:
                        to_process.append(child_id)
                        
            except Exception as e:
                print(f"Debug: 子ページ取得エラー - page_id: {current_id}, error: {e}")
                continue
        
        print(f"Debug: 代替方法完了 - 総結果数: {len(all_results)}")
        return all_results

    def build_descendants_tree(self, descendants: list, ancestor_id: str) -> dict:
        """
        子孫ページリストから階層構造を構築
        """
        # ページIDをキーとした辞書を作成
        page_dict = {}
        for page in descendants:
            page_id = page.get('id')
            if page_id:
                # v2 APIの場合はparentIdを使用
                parent_id = page.get('parentId')
                # レベルは親ページの数で計算（簡易版）
                level = 1  # デフォルトレベル
                
                # v2 APIの場合は、URLを手動で構築（スペースキーをECL2SOPに固定）
                page_url = f"{self.base_url}/wiki/spaces/ECL2SOP/pages/{page_id}"
                print(f"Debug: ページURL生成 - ID: {page_id}, URL: {page_url}")
                
                page_dict[page_id] = {
                    'id': page_id,
                    'title': page.get('title'),
                    'type': page.get('type'),
                    'status': page.get('status'),
                    'spaceId': page.get('spaceId'),
                    'parent_id': parent_id,
                    'level': level,
                    'url': page_url,
                    'children': []
                }
        
        # 階層構造を構築
        tree = []
        for page_id, page_info in page_dict.items():
            parent_id = page_info['parent_id']
            if parent_id and parent_id in page_dict:
                # 親ページの子として追加
                page_dict[parent_id]['children'].append(page_info)
            elif page_id != ancestor_id:
                # ルートレベルのページとして追加（ancestor_id以外）
                tree.append(page_info)
        
        # v2 APIの場合は、flat_listをそのまま返す
        print("Debug: v2 API形式のため、フラットリストとして返します")
        return {
            'ancestor_id': ancestor_id,
            'total_count': len(descendants),
            'tree': tree,
            'flat_list': list(page_dict.values())
        }

    def get_children_v2(self, ancestor_id: str, limit: int = 50, cursor: str = None) -> list:
        """
        v2 APIで指定ページIDの子ページ一覧を取得（ネットワークエラー詳細出力付き）
        """
        all_results = []
        base_url = f"{self.base_url}/wiki/api/v2/pages/{ancestor_id}/children?limit={limit}"
        url = base_url if not cursor else f"{base_url}&cursor={cursor}"
        headers = {'Accept': 'application/json'}
        
        print(f"Debug: v2 children API 開始 - URL: {url}")
        
        while True:
            try:
                print(f"Debug: リクエスト送信 - URL: {url}")
                resp = self.session.get(url, headers=headers, verify=False, auth=(self.username, self.api_token))
                print(f"Debug: レスポンスステータス: {resp.status_code}")
                
                if resp.status_code != 200:
                    print(f"Debug: エラーレスポンス - {resp.text}")
                    resp.raise_for_status()
                
                data = resp.json()
                print(f"Debug: レスポンスデータ: {data}")
                
                results = data.get('results', [])
                all_results.extend(results)
                print(f"Debug: 取得した結果数: {len(results)}, 累計: {len(all_results)}")
                
                next_link = data.get('_links', {}).get('next')
                if not next_link:
                    print("Debug: 次のページなし - 終了")
                    break
                
                # next_linkは絶対パスまたは相対パス
                if next_link.startswith('http'):
                    url = next_link
                elif next_link.startswith('/'):
                    url = self.base_url + next_link
                else:
                    url = base_url + '&cursor=' + next_link
                print(f"Debug: 次のURL: {url}")
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Debug: 例外発生 - {error_details}")
                raise RuntimeError(f"v2 children API error: {e} (url={url}, details={error_details})")
        
        print(f"Debug: v2 children API 完了 - 総結果数: {len(all_results)}")
        return all_results

def main():
    """
    使用例
    """
    # 環境変数から認証情報を取得（推奨）
    base_url = os.getenv('CONFLUENCE_BASE_URL')
    username = os.getenv('CONFLUENCE_USERNAME')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')
    space_key = os.getenv('CONFLUENCE_SPACE_KEY', 'DEMO')
    
    # 環境変数が設定されていない場合は直接指定
    if not all([base_url, username, api_token]):
        print("環境変数が設定されていません。直接値を設定してください。")
        base_url = "https://your-domain.atlassian.net"
        username = "your-email@example.com"
        api_token = "your-api-token"
        space_key = "DEMO"
    
    try:
        # Confluence APIクライアントを初期化
        confluence = ConfluenceAPI(str(base_url), str(username), str(api_token))
        
        print(f"=== {space_key} スペースのコンテンツを取得 ===")
        
        # スペースの情報を取得
        space_info = confluence.get_space_info(space_key)
        print(f"スペース名: {space_info.get('name')}")
        print(f"スペースキー: {space_info.get('key')}")
        print()
        
        # スペースのコンテンツを取得
        content = confluence.get_space_content(space_key, limit=10)
        
        print(f"取得したコンテンツ数: {content.get('size', 0)}")
        print()
        
        # 各ページの情報を表示
        for page in content.get('results', []):
            extracted = confluence.extract_page_content(page)
            print(f"タイトル: {extracted['title']}")
            print(f"ID: {extracted['id']}")
            print(f"タイプ: {extracted['type']}")
            print(f"ステータス: {extracted['status']}")
            print(f"URL: {extracted['url']}")
            print(f"更新日: {extracted['updated']}")
            print("-" * 50)
        
        # 検索例
        print("\n=== 検索例 ===")
        search_results = confluence.search_content("test", limit=5)
        print(f"検索結果数: {search_results.get('size', 0)}")
        
        for result in search_results.get('results', []):
            print(f"- {result.get('title')} ({result.get('type')})")
        
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    main() 