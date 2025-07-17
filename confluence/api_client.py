import requests
import base64
import warnings
from typing import Dict, Optional

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class ConfluenceAPI:
    """
    Confluence APIを使用してコンテンツを取得するクラス
    （API通信・データ取得部分のみ）
    """
    def __init__(self, base_url: str, username: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.session = requests.Session()
        credentials = f"{username}:{api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.session.headers.update({
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def get_space_content(self, space_key: str, limit: int = 25) -> Dict:
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
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {
            'expand': 'body.storage,version,children.page'
        }
        response = self.session.get(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()

    def search_content(self, query: str, cql: Optional[str] = None, limit: int = 25) -> Dict:
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
        url = f"{self.base_url}/rest/api/content/{page_id}/child/page"
        params = {
            'limit': limit,
            'expand': 'body.storage,version'
        }
        response = self.session.get(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()

    def get_space_info(self, space_key: str) -> Dict:
        url = f"{self.base_url}/rest/api/space/{space_key}"
        response = self.session.get(url, verify=False)
        response.raise_for_status()
        return response.json()

    # --- v2 API ---
    def get_space_id_by_key_v2(self, space_key: str) -> Optional[str]:
        url = f"{self.base_url}/wiki/api/v2/spaces?keys={space_key}"
        resp = self.session.get(url, verify=False)
        resp.raise_for_status()
        data = resp.json()
        if data and data.get('results'):
            return data['results'][0]['id']
        return None

    def get_space_pages_v2(self, space_id: str, limit: int = 25) -> dict:
        url = f"{self.base_url}/wiki/api/v2/spaces/{space_id}/pages?limit={limit}"
        resp = self.session.get(url, verify=False)
        resp.raise_for_status()
        return resp.json()

    def search_pages_v2(self, query: str, limit: int = 25) -> dict:
        url = f"{self.base_url}/wiki/api/v2/pages?limit={limit}&q={query}"
        resp = self.session.get(url, verify=False)
        resp.raise_for_status()
        return resp.json()

    def get_page_children_v2(self, page_id: str, limit: int = 10) -> dict:
        url = f"{self.base_url}/wiki/api/v2/pages/{page_id}/children?limit={limit}"
        resp = self.session.get(url, verify=False)
        resp.raise_for_status()
        return resp.json()

    def get_all_pages_in_space_v2(self, space_id: str) -> list:
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

    def get_all_descendants_v2(self, page_id: str, limit: int = 50) -> list:
        """
        v2 APIで指定ページID配下の全子孫ページを再帰的に取得
        """
        descendants = []
        def _fetch_children(pid):
            children_data = self.get_page_children_v2(pid, limit=limit)
            for child in children_data.get('results', []):
                descendants.append(child)
                _fetch_children(child.get('id'))
        _fetch_children(page_id)
        return descendants 