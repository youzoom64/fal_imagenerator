"""画像表示・処理関連のユーティリティ"""
import requests
from PIL import Image, ImageTk
from io import BytesIO

class ImageDisplayManager:
    def __init__(self, thumbnail_size=(200, 200)):
        self.thumbnail_size = thumbnail_size
    
    def create_image_display(self, image_url, filename):
        """URLから画像を取得してサムネイル表示用に処理"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            
            # サムネイル作成
            thumbnail = image.copy()
            thumbnail.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(thumbnail)
            
            return {
                "success": True,
                "image": image,
                "photo": photo,
                "filename": filename
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }