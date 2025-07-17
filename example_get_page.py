import requests
import warnings
from requests.auth import HTTPBasicAuth

# SSL証明書検証を無効化している警告を抑制
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# 認証情報（本番運用では環境変数や.envで管理推奨）
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

username = os.getenv('CONFLUENCE_USERNAME', 'your-email@example.com')
api_token = os.getenv('CONFLUENCE_API_TOKEN', 'your-api-token')

# APIエンドポイント
base_url = os.getenv('CONFLUENCE_BASE_URL', 'https://nttcom.atlassian.net')
url = f"{base_url}/wiki/api/v2/pages/4515299949?body-format=storage"

# ヘッダー
headers = {
    "Accept": "application/json"
}

# GETリクエスト送信（SSL証明書検証を無効化）
response = requests.get(
    url,
    headers=headers,
    auth=HTTPBasicAuth(username, api_token),
    verify=False
)

# 結果表示
print("Status:", response.status_code)
try:
    print("Response:", response.json())
except Exception:
    print("Response Text:", response.text) 