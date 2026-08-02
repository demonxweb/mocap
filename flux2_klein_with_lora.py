import torch
from diffusers import Flux2KleinPipeline

# 1. 載入原始的 FLUX.2-klein-9B 模型
pipeline = Flux2KleinPipeline.from_pretrained(
    "black-forest-labs/FLUX.2-klein-9B", 
    torch_dtype=torch.bfloat16
).to("cuda")

# 2. 直接載入你剛剛訓練好的 LoRA 權重
pipeline.load_lora_weights("./path_to_your_trained_lora", weight_name="pytorch_lora_weights.safetensors")

# 3. 調整 LoRA 的影響強度 (Scale，通常設定在 0.7 ~ 1.0 之間)
pipeline.fuse_lora(lora_scale=0.8)

# 4. 開始使用多圖參考與 LoRA 進行推理生成
generated_image = pipeline(
    prompt="a photo of ohwx character in a cyberpunk city",
    reference_images=[...], # 你的多張參考圖
    num_inference_steps=20,
    guidance_scale=3.5
).images[0]
