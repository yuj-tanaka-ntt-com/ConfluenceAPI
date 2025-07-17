import requests
from bs4 import BeautifulSoup
from config import OPENAI_API_KEY, AZURE_OPENAI_KEY, AZURE_OPENAI_BASE, DEPLOYMENT_NAME, API_VERSION

# トークン数の概算（英語1単語≒1トークン、1文字≒0.5トークン程度）
def estimate_tokens(text):
    return max(1, int(len(text) / 2))

# HTMLをできるだけ大きなブロック単位で分割し、まとめて翻訳

def translate_en_to_ja(text: str) -> str:
    """
    Azure OpenAI APIを使って英語→日本語翻訳（大きなブロック単位で分割翻訳し品質向上）
    """
    if not AZURE_OPENAI_KEY or not AZURE_OPENAI_BASE or not DEPLOYMENT_NAME or not API_VERSION:
        print("[DEBUG] Azure OpenAIの設定が不足しています")
        raise ValueError("Azure OpenAIの設定が不足しています")
    url = f"{AZURE_OPENAI_BASE}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }
    soup = BeautifulSoup(text, "html.parser")
    translatable_tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "span", "div"]
    blocks = []
    current_block = []
    current_len = 0
    max_tokens = 1800  # APIのmax_tokensより少し余裕を持たせる
    # 1. 連続するテキストブロックをまとめる
    for tag in soup.find_all(translatable_tags):
        t = tag.get_text(strip=True)
        if t:
            t_len = estimate_tokens(t)
            if current_len + t_len > max_tokens and current_block:
                blocks.append(list(current_block))
                current_block = []
                current_len = 0
            current_block.append(tag)
            current_len += t_len
    if current_block:
        blocks.append(list(current_block))
    # 2. まとめて翻訳
    for block in blocks:
        en_texts = [tag.get_text(strip=True) for tag in block]
        joined = "\n".join(en_texts)
        payload = {
            "messages": [
                {"role": "system", "content": "You are a professional translator. Translate the following English text to Japanese. Preserve line breaks."},
                {"role": "user", "content": joined}
            ],
            "max_tokens": 2048,
            "temperature": 0.3
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            ja_joined = result["choices"][0]["message"]["content"].strip()
            ja_texts = ja_joined.split("\n")
            # 行数が一致しない場合は無理に詰め込む
            for tag, ja in zip(block, ja_texts):
                tag.clear()
                tag.append(ja)
        except Exception as e:
            print(f"[翻訳APIエラー] {e}")
            continue
    return str(soup)

# Azure OpenAI APIによる翻訳（単文用）
def translate_en_to_ja_azure(text: str) -> str:
    if not AZURE_OPENAI_KEY or not AZURE_OPENAI_BASE or not DEPLOYMENT_NAME or not API_VERSION:
        raise ValueError("Azure OpenAIの設定が不足しています")
    url = f"{AZURE_OPENAI_BASE}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are a professional translator. Translate the following English text to Japanese."},
            {"role": "user", "content": text}
        ],
        "max_tokens": 2048,
        "temperature": 0.3
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()
