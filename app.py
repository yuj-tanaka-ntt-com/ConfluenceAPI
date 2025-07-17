#!/usr/bin/env python3
"""
Confluence API Webアプリケーション
"""

# .envの環境変数を読み込む
from dotenv import load_dotenv
load_dotenv()

import os
import json
import warnings
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from requests.auth import HTTPBasicAuth
from confluence.api_client import ConfluenceAPI
from confluence.service import extract_page_content, build_page_tree, build_descendants_tree
from confluence.utils import extract_page_id_from_url
from confluence.translator import translate_en_to_ja
import config
from requests.exceptions import HTTPError

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


print("=== Flaskアプリ起動処理開始 ===")
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
CORS(app)

def get_confluence_client():
    base_url = config.CONFLUENCE_BASE_URL
    username = config.CONFLUENCE_USERNAME
    api_token = config.CONFLUENCE_API_TOKEN
    if not all([base_url, username, api_token]):
        return None
    return ConfluenceAPI(base_url, username, api_token)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/page_by_url', methods=['POST'])
def get_page_by_url():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'リクエストボディが空です'}), 400
        page_input = data.get('page_input', '').strip()
        page_id = extract_page_id_from_url(page_input)
        if not page_id:
            return jsonify({'error': 'ページIDが抽出できませんでした'}), 400

        confluence = get_confluence_client()
        if not confluence:
            return jsonify({'error': 'Confluence設定が不完全です'}), 400

        # ページ本体（まずv1、404ならv2で再取得）
        try:
            page_data = confluence.get_page_content(page_id)
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                # v2 APIで再取得
                url = f"{confluence.base_url}/wiki/api/v2/pages/{page_id}?body-format=storage"
                headers = {"Accept": "application/json"}
                resp = confluence.session.get(url, headers=headers, verify=False)
                if resp.status_code == 404:
                    return jsonify({'error': 'ページが存在しないか、権限がありません（404）'}), 404
                resp.raise_for_status()
                page_data = resp.json()
            else:
                raise

        page_info = extract_page_content(page_data)
        # page_info['content'] には必ず原文（英語）のみをセットすること！
        # 英語本文を日本語に翻訳
        translated_body = None
        print(f"[DEBUG] page_info: {page_info}")
        content = page_info.get('content')
        print(f"[DEBUG] 翻訳対象: {content}")
        if page_info and content:
            print(f"[DEBUG] 翻訳対象長: {len(content)}")
            try:
                translated_body = translate_en_to_ja(content)
                print(f"[DEBUG] 翻訳結果: {translated_body}")
            except Exception as e:
                print('[翻訳エラー]', e)
                translated_body = None

        # 子ページは必ずv2 APIで取得
        children_data = confluence.get_page_children_v2(page_id)
        children = []
        for child in children_data.get('results', []):
            children.append({
                'id': child.get('id'),
                'title': child.get('title'),
                'status': child.get('status'),
                'spaceId': child.get('spaceId'),
                'childPosition': child.get('childPosition')
            })

        return jsonify({
            'page': page_info,
            'children': children,
            'translated_body': translated_body
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print('[ERROR]', e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_page():
    try:
        data = request.json
        if not data or 'page_id' not in data:
            return jsonify({'error': 'page_idが指定されていません'}), 400
        page_id = str(data['page_id']).strip()
        confluence = get_confluence_client()
        if not confluence:
            return jsonify({'error': 'Confluence設定が不完全です'}), 400
        # ページ本体取得
        try:
            page_data = confluence.get_page_content(page_id)
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                url = f"{confluence.base_url}/wiki/api/v2/pages/{page_id}?body-format=storage"
                headers = {"Accept": "application/json"}
                resp = confluence.session.get(url, headers=headers, verify=False)
                if resp.status_code == 404:
                    return jsonify({'error': 'ページが存在しないか、権限がありません（404）'}), 404
                resp.raise_for_status()
                page_data = resp.json()
            else:
                raise
        page_info = extract_page_content(page_data)
        translated_body = None
        content = page_info.get('content')
        print(f"[DEBUG] 再翻訳対象: {content}")
        if page_info and content:
            print(f"[DEBUG] 再翻訳対象長: {len(content)}")
            try:
                translated_body = translate_en_to_ja(content)
                print(f"[DEBUG] 再翻訳結果: {translated_body}")
            except Exception as e:
                print('[翻訳エラー]', e)
                translated_body = None
        return jsonify({'translated_body': translated_body})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print('[ERROR]', e)
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    print("Confluence API Webアプリケーションを起動中...")
    print("http://localhost:5000 にアクセスしてください")
    print("Flaskサーバー起動: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)