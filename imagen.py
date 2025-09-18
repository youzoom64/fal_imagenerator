import os
import requests
import fal_client
from PIL import Image
from io import BytesIO

# APIキーを設定（環境変数または直接設定）
os.environ["FAL_KEY"] = "b488e96d-07f9-4819-ad46-1fa63085406c:94fa3a45388437253fd0e273105e8161"  # ここにあなたのAPIキーを入力

def generate_image(prompt, width=1024, height=1024, num_images=1, guidance_scale=3.5, num_inference_steps=28, seed=None):
    """
    FLUX-1/devを使用して画像を生成する関数
    """
    try:
        # リクエストパラメータ
        arguments = {
            "prompt": prompt,
            "image_size": "landscape_4_3",  # または "square_hd", "portrait_4_3"等
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "num_images": num_images,
        }
        
        # seedが指定されている場合は追加
        if seed is not None:
            arguments["seed"] = seed
            
        # fal-ai/flux/dev エンドポイントを呼び出し
        result = fal_client.subscribe(
            "fal-ai/flux/dev",
            arguments=arguments
        )
        
        print(f"生成完了！ {len(result['images'])}枚の画像が生成されました。")
        
        # 画像をダウンロードして保存
        for i, image_data in enumerate(result['images']):
            image_url = image_data['url']
            
            # 画像をダウンロード
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            
            # ファイル名を生成
            filename = f"flux_generated_{i+1}.png"
            image.save(filename)
            print(f"画像を保存しました: {filename}")
            
        return result
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    # 使用例
    prompt = "A beautiful sunset over a mountain range with cherry blossoms in the foreground"
    
    print("FLUX-1/devで画像生成を開始...")
    result = generate_image(
        prompt=prompt,
        num_images=2,
        guidance_scale=3.5,
        num_inference_steps=28
    )
    
    if result:
        print("生成された画像情報:")
        for i, img in enumerate(result['images']):
            print(f"画像 {i+1}: {img['url']}")