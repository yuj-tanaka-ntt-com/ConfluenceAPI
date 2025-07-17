import re
from typing import Optional

def extract_page_id_from_url(page_input: str) -> Optional[str]:
    """
    入力値からページIDを抽出（数字のみ or URL）
    """
    page_input = page_input.strip()
    # クエリやフラグメントを除去
    page_input = re.sub(r'[?#].*$', '', page_input)
    # デバッグ出力
    print(f"[DEBUG] extract_page_id_from_url input: {page_input}")
    # 数字のみ
    if page_input.isdigit():
        print(f"[DEBUG] ID抽出: {page_input}")
        return page_input
    # /pages/123456789 形式
    match = re.search(r'/pages/(\d+)', page_input)
    if match:
        print(f"[DEBUG] /pages/抽出: {match.group(1)}")
        return match.group(1)
    # /wiki/spaces/SPACE_KEY/pages/123456789 形式
    match = re.search(r'/wiki/spaces/[^/]+/pages/(\d+)', page_input)
    if match:
        print(f"[DEBUG] /wiki/spaces/抽出: {match.group(1)}")
        return match.group(1)
    # 例: https://xxx.atlassian.net/wiki/pages/viewpage.action?pageId=123456789
    match = re.search(r'pageId=(\d+)', page_input)
    if match:
        print(f"[DEBUG] pageId抽出: {match.group(1)}")
        return match.group(1)
    # 最後に、末尾がスラッシュまたは何もない状態で数字の場合のみ（URLの最後がID）
    match = re.search(r'(?:/)?(\d+)$', page_input)
    if match:
        print(f"[DEBUG] 末尾数字抽出: {match.group(1)}")
        return match.group(1)
    print("[DEBUG] ID抽出失敗")
    return None