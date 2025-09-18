"""画像生成のコアロジック（text-to-image & image-to-image対応）"""
import os
import fal_client
from datetime import datetime

class ImageGenerator:
    def __init__(self, output_dir="generated_images"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate(self, api_key, model_endpoint, generation_params):
        """画像を生成"""
        os.environ["FAL_KEY"] = api_key
        
        try:
            result = fal_client.subscribe(model_endpoint, arguments=generation_params)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def build_text_to_image_params(self, prompt, negative_prompt, num_inference_steps, 
                                  guidance_scale, num_images, enable_safety_checker, 
                                  image_size_params, seed=None):
        """text-to-image用パラメータを構築"""
        params = {
            "prompt": prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "num_images": num_images,
            "enable_safety_checker": enable_safety_checker
        }
        
        # ネガティブプロンプト（空でない場合のみ追加）
        if negative_prompt:
            params["negative_prompt"] = negative_prompt
        
        # 画像サイズ設定
        if isinstance(image_size_params, dict):  # カスタムサイズ
            params["image_size"] = image_size_params
        else:  # プリセット
            params["image_size"] = image_size_params
        
        # シード値設定
        if seed:
            try:
                params["seed"] = int(seed)
            except (ValueError, TypeError):
                pass
        
        return params
    
    def build_image_to_image_params(self, prompt, negative_prompt, image_url, strength,
                                   num_inference_steps, guidance_scale, num_images, 
                                   enable_safety_checker, seed=None):
        """image-to-image用パラメータを構築"""
        params = {
            "prompt": prompt,
            "image_url": image_url,
            "strength": strength,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "num_images": num_images,
            "enable_safety_checker": enable_safety_checker
        }
        
        # ネガティブプロンプト（空でない場合のみ追加）
        if negative_prompt:
            params["negative_prompt"] = negative_prompt
        
        # シード値設定
        if seed:
            try:
                params["seed"] = int(seed)
            except (ValueError, TypeError):
                pass
        
        return params
    
    async def upload_image_to_fal(self, image_path):
        """画像をfal.aiストレージにアップロード"""
        try:
            with open(image_path, 'rb') as f:
                file_data = f.read()
            
            # fal.aiのストレージにアップロード
            url = await fal_client.upload_file(file_data)
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_image_to_fal_sync(self, image_path_or_pil):
        """画像をfal.aiストレージに同期アップロード（パスまたはPILイメージ）"""
        try:
            # PILイメージの場合は一時ファイルとして保存
            if hasattr(image_path_or_pil, 'save'):  # PIL Image オブジェクト
                import tempfile
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, "temp_upload_image.png")
                image_path_or_pil.save(temp_path)
                image_path = temp_path
            else:
                image_path = image_path_or_pil
            
            # Base64エンコード
            import base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # MIMEタイプを推定
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {'.jpg': 'jpeg', '.jpeg': 'jpeg', '.png': 'png', '.gif': 'gif', '.webp': 'webp'}
            mime_type = mime_types.get(ext, 'png')
            
            data_url = f"data:image/{mime_type};base64,{image_data}"
            return {"success": True, "url": data_url}
            
        except Exception as e:
            return {"success": False, "error": f"画像アップロードエラー: {str(e)}"}
    def generate_filename(self, index=0, mode="text-to-image"):
        """ファイル名を生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "txt2img" if mode == "text-to-image" else "img2img"
        return f"{prefix}_{timestamp}_{index+1}.png"
    
    def get_output_dir(self):
        """出力ディレクトリを取得"""
        return self.output_dir