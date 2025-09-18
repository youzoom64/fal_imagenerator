"""モデル定義と管理を行うクラス"""

class ModelManager:
    def __init__(self):
        # text-to-image モデル
        self.text_to_image_models = {
            "FLUX.1 [dev] - 高品質バランス型": "fal-ai/flux/dev",
            "FLUX.1 [schnell] - 高速生成": "fal-ai/flux/schnell", 
            "FLUX.1 Pro v1.1 - 最高品質": "fal-ai/flux-pro/v1.1",
            "FLUX.1 Pro Ultra - 2K対応": "fal-ai/flux-pro/v1.1-ultra",
            "Recraft V3 - ベクターアート特化": "fal-ai/recraft-v3",
            "Stable Diffusion 3.5 Large - 汎用高品質": "fal-ai/stable-diffusion-v35-large",
            "Ideogram V3 - タイポグラフィ特化": "fal-ai/ideogram/v3",
            "FLUX with LoRA - カスタマイゼーション": "fal-ai/flux-lora",
            "Fast SDXL - 高速SDXL": "fal-ai/fast-sdxl",
            "Qwen Image - テキスト編集特化": "fal-ai/qwen-image"
        }
        
        # image-to-image モデル
        self.image_to_image_models = {
            "FLUX.1 [dev] - 高品質変換": "fal-ai/flux/dev/image-to-image",
            "FLUX.1 [schnell] Redux - 高速変換": "fal-ai/flux/schnell/image-to-image",
            "FLUX.1 Kontext [pro] - 高度編集": "fal-ai/flux-pro/kontext",
            "FLUX with LoRA - カスタム変換": "fal-ai/flux-lora/image-to-image",
            "Fast SDXL - 高速SDXL変換": "fal-ai/fast-sdxl/image-to-image",
            "PhotoMaker - 人物写真特化": "fal-ai/photomaker"
        }
        
        # 統合モデルリスト（下位互換用）
        self.available_models = {**self.text_to_image_models, **self.image_to_image_models}
        
        # モデルパラメータ（text-to-image用）
        self.text_to_image_parameters = {
            "fal-ai/flux/dev": {"max_inference_steps": 28, "default_inference_steps": 28, "default_guidance_scale": 3.5, "default_safety_checker": True},
            "fal-ai/flux/schnell": {"max_inference_steps": 4, "default_inference_steps": 4, "default_guidance_scale": 3.5, "default_safety_checker": True},
            "fal-ai/flux-pro/v1.1": {"max_inference_steps": 25, "default_inference_steps": 25, "default_guidance_scale": 3.5, "default_safety_checker": True},
            "fal-ai/flux-pro/v1.1-ultra": {"max_inference_steps": 25, "default_inference_steps": 25, "default_guidance_scale": 3.5, "default_safety_checker": True},
            "fal-ai/recraft-v3": {"max_inference_steps": 12, "default_inference_steps": 12, "default_guidance_scale": 7.5, "default_safety_checker": True},
            "fal-ai/stable-diffusion-v35-large": {"max_inference_steps": 50, "default_inference_steps": 28, "default_guidance_scale": 7.5, "default_safety_checker": True},
            "fal-ai/ideogram/v3": {"max_inference_steps": 12, "default_inference_steps": 12, "default_guidance_scale": 7.5, "default_safety_checker": True},
            "fal-ai/flux-lora": {"max_inference_steps": 28, "default_inference_steps": 28, "default_guidance_scale": 3.5, "default_safety_checker": True},
            "fal-ai/fast-sdxl": {"max_inference_steps": 8, "default_inference_steps": 5, "default_guidance_scale": 2.0, "default_safety_checker": True},
            "fal-ai/qwen-image": {"max_inference_steps": 20, "default_inference_steps": 20, "default_guidance_scale": 7.5, "default_safety_checker": True}
        }
        
        # image-to-imageパラメータ
        self.image_to_image_parameters = {
            "fal-ai/flux/dev/image-to-image": {"max_inference_steps": 40, "default_inference_steps": 40, "default_guidance_scale": 3.5, "default_strength": 0.95, "default_safety_checker": True},
            "fal-ai/flux/schnell/image-to-image": {"max_inference_steps": 4, "default_inference_steps": 4, "default_guidance_scale": 3.5, "default_strength": 0.95, "default_safety_checker": True},
            "fal-ai/flux-pro/kontext": {"max_inference_steps": 25, "default_inference_steps": 25, "default_guidance_scale": 3.5, "default_strength": 0.8, "default_safety_checker": True},
            "fal-ai/flux-lora/image-to-image": {"max_inference_steps": 28, "default_inference_steps": 28, "default_guidance_scale": 3.5, "default_strength": 0.95, "default_safety_checker": True},
            "fal-ai/fast-sdxl/image-to-image": {"max_inference_steps": 25, "default_inference_steps": 25, "default_guidance_scale": 7.5, "default_strength": 0.95, "default_safety_checker": True},
            "fal-ai/photomaker": {"max_inference_steps": 50, "default_inference_steps": 50, "default_guidance_scale": 5.0, "default_strength": 1.0, "default_safety_checker": True}
        }
        
        # 統合パラメータリスト
        self.model_parameters = {**self.text_to_image_parameters, **self.image_to_image_parameters}
    
    def get_models_by_type(self, model_type):
        """タイプ別のモデルを取得"""
        if model_type == "text-to-image":
            return self.text_to_image_models
        elif model_type == "image-to-image":
            return self.image_to_image_models
        else:
            return self.available_models
    
    def is_image_to_image_model(self, endpoint):
        """image-to-imageモデルかどうか判定"""
        return endpoint in self.image_to_image_models.values()
    
    def get_model_display_name(self, model_endpoint):
        """エンドポイントから表示名を取得"""
        for display_name, endpoint in self.available_models.items():
            if endpoint == model_endpoint:
                return display_name
        return list(self.available_models.keys())[0]
    
    def get_model_endpoint(self, display_name):
        """表示名からエンドポイントを取得"""
        return self.available_models.get(display_name, "fal-ai/flux/dev")
    
    def get_model_parameters(self, endpoint):
        """モデルのパラメータを取得"""
        return self.model_parameters.get(endpoint, {
            "max_inference_steps": 50, 
            "default_inference_steps": 28, 
            "default_guidance_scale": 3.5,
            "default_strength": 0.95,
            "default_safety_checker": True
        })
    
    def get_model_names(self, model_type=None):
        """利用可能なモデル名のリストを取得"""
        if model_type:
            return list(self.get_models_by_type(model_type).keys())
        return list(self.available_models.keys())