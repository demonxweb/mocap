import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
from diffusers import FlowMatchEulerDiscreteScheduler, AutoencoderKL
from diffusers.models.transformers.transformer_flux2 import Flux2KleinTransformerModel # 依 diffusers 最新類別為準
from peft import LoraConfig, get_peft_model

# ==========================================
# 1. 多圖參考資料集定義
# ==========================================
class Flux2MultiRefDataset(Dataset):
    """
    資料夾結構設計:
    dataset_root/
      ├── sample_001/
      │     ├── ref_1.jpg
      │     ├── ref_2.jpg
      │     └── target.jpg
      └── sample_002/
            ├── ref_1.jpg
            └── target.jpg
    """
    def __init__(self, root_dir, size=1024):
        self.root_dir = root_dir
        self.groups = [os.path.join(root_dir, d) for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
        self.transform = transforms.Compose([
            transforms.Resize((size, size), interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.CenterCrop((size, size)),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]) # 壓至 [-1, 1]
        ])

    def __len__(self):
        return len(self.groups)

    def __getitem__(self, idx):
        group_path = self.groups[idx]
        image_files = sorted([os.path.join(group_path, f) for f in os.listdir(group_path) if f.endswith(('png', 'jpg', 'jpeg'))])
        
        # 假設最後一張為 target，前面全為 reference images
        target_path = image_files[-1]
        ref_paths = image_files[:-1] if len(image_files) > 1 else [image_files[0]]
        
        target_img = self.transform(Image.open(target_path).convert("RGB"))
        ref_imgs = torch.stack([self.transform(Image.open(p).convert("RGB")) for p in ref_paths])
        
        caption = "a high quality consistent character generation based on multiple references"
        
        return {
            "ref_images": ref_imgs,         # 形状: [N_refs, 3, 1024, 1024]
            "target_image": target_img,     # 形状: [3, 1024, 1024]
            "caption": caption
        }

def collate_fn(batch):
    return {
        "ref_images": [item["ref_images"] for item in batch],
        "target_image": torch.stack([item["target_image"] for item in batch]),
        "caption": [item["caption"] for item in batch]
    }

# ==========================================
# 2. 主訓練程序
# ==========================================
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_id = "black-forest-labs/FLUX.2-klein-base-9B"
    
    print("正在載入 FLUX.2 Klein 9B 基礎組件...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, subfolder="tokenizer")
    text_encoder = AutoModelForCausalLM.from_pretrained(
        model_id, subfolder="text_encoder", torch_dtype=torch.bfloat16
    ).to(device)
    
    vae = AutoencoderKL.from_pretrained(
        model_id, subfolder="vae", torch_dtype=torch.bfloat16
    ).to(device)
    
    transformer = Flux2KleinTransformerModel.from_pretrained(
        model_id, subfolder="transformer", torch_dtype=torch.bfloat16
    )

    # 凍結基礎模型
    transformer.requires_grad_(False)
    text_encoder.requires_grad_(False)
    vae.requires_grad_(False)

    # ==========================================
    # 3. 注入 LoRA 權重 (PEFT)
    # ==========================================
    print("正在注入 LoRA 結構...")
    lora_config = LoraConfig(
        r=16,
        lora_alpha=16,
        target_modules=["to_q", "to_k", "to_v", "to_out.0", "add_q_proj", "add_k_proj", "add_v_proj"],
        lora_dropout=0.0,
        bias="none",
    )
    transformer = get_peft_model(transformer, lora_config)
    transformer.print_trainable_parameters()
    transformer.to(device)
    transformer.train()

    # 排程器 (Flow Matching)
    scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")

    # ==========================================
    # 4. 資料集與優化器設定
    # ==========================================
    dataset = Flux2MultiRefDataset(root_dir="./my_multiref_dataset")
    dataloader = DataLoader(dataset, batch_size=1, shuffle=True, collate_fn=collate_fn)

    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, transformer.parameters()),
        lr=1e-4, weight_decay=1e-2
    )

    # ==========================================
    # 5. 訓練迴圈 (Training Loop)
    # ==========================================
    epochs = 3
    global_step = 0

    print("開始執行 FLUX.2 Klein 多圖參考 LoRA 訓練...")
    for epoch in range(epochs):
        for batch in dataloader:
            optimizer.zero_grad()
            
            ref_images = batch["ref_images"][0].to(device, dtype=torch.bfloat16)
            target_image = batch["target_image"].to(device, dtype=torch.bfloat16).unsqueeze(0)
            caption = batch["caption"][0]
            
            with torch.no_grad():
                # 1. VAE 編碼：目標圖與多張參考圖
                target_latents = vae.encode(target_image).latent_dist.sample() * vae.config.scaling_factor
                ref_latents = vae.encode(ref_images).latent_dist.sample() * vae.config.scaling_factor
                
                # 2. 文字編碼 (Qwen VL)
                text_inputs = tokenizer(caption, return_tensors="pt", padding=True, truncation=True, max_length=256).to(device)
                encoder_hidden_states = text_encoder(**text_inputs, output_hidden_states=True).hidden_states[-1]

            # 3. Flow Matching 加噪流程
            noise = torch.randn_like(target_latents)
            timesteps = torch.randint(0, scheduler.config.num_train_timesteps, (1,), device=device).long()
            
            # 根據 Flow Matching 公式混合噪點與目標 Latents
            sigmas = scheduler.sigmas[timesteps].to(device)
            noisy_latents = (1.0 - sigmas) * target_latents + sigmas * noise

            # 4. 傳入 Transformer 預測 (整合多圖參考特徵 `reference_latents`)
            model_pred = transformer(
                hidden_states=noisy_latents,
                encoder_hidden_states=encoder_hidden_states,
                timestep=timesteps,
                reference_latents=ref_latents,  # FLUX.2 Klein 接收多參考特徵的接口
                return_dict=False
            )[0]

            # 5. 計算 Flow Matching 專屬 Loss
            target_flow = noise - target_latents
            loss = torch.nn.functional.mse_loss(model_pred.float(), target_flow.float())

            loss.backward()
            optimizer.step()
            
            global_step += 1
            print(f"Epoch [{epoch+1}/{epochs}] | Step [{global_step}] | Loss: {loss.item():.4f}")

            if global_step % 300 == 0:
                save_path = f"./flux2_klein_multiref_checkpoint_{global_step}"
                transformer.save_pretrained(save_path)
                print(f"已儲存 Checkpoint 至: {save_path}")

    transformer.save_pretrained("./final_flux2_klein_multiref_lora")
    print("訓練完成！")

if __name__ == "__main__":
    main()
