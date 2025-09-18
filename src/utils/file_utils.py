"""ファイル操作関連のユーティリティ"""
import os
import requests
from PIL import Image
from io import BytesIO

def save_image_from_url(url, filepath):
    """URLから画像をダウンロードして保存"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        image.save(filepath)
        return {"success": True, "image": image}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_thumbnail(image, size=(200, 200)):
    """サムネイル画像を作成"""
    thumbnail = image.copy()
    thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
    return thumbnail