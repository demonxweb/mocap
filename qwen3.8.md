# Download GGUF

https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/main
- 模型: Qwen3.8-27B-Q4_K_M.gguf
- 視覺模型: mmproj-BF16.gguf 


# 參數說明

* -t: 使用多少個 CPU 執行緒（Threads）
* -b: 當伺服器接收到長篇的 Prompt（提示詞）或者有多個並行請求需要處理時，系統會把這些 Token 分批次（Logical Batch）送進模型運算。
* -ub: 這是硬體（特別是 GPU）在實際執行底層矩陣運算時，每一小批次塞進去的 Token 數量。它永遠小於或等於邏輯批次大小（-b）
* --temp: 控制生成文字的隨機性與創造力
* --top-p: 只從累積機率加起來等於設定機率的候選字清單中挑選
* --top-k: 無論模型的候選字有多少，強制規定「每一次只許從機率最高的字裡面挑選」

> --temp 0.6 --top-p 0.5 --top-k 15 透過「降溫 + 雙重過濾（砍掉機率低的、限制只看前 15 名）」，讓模型變成一個「講話謹慎、實事求是、不容易亂發揮」的助手。如果你這組設定是用來跑程式碼生成、除錯或問答，它會表現得非常精準且穩定。

* --ctx-size: 調整content-length 最大262144，記憶體不足可以調到100k
* --cache-type-k , --cache-type-v: 調整q8_0或q4_0 可減少記憶體使用，但精度會下降
* --spec-type , --spec-draft-n-max: 調整MTP，增加吐字速度
* --fit: 自動記憶體分配與計算
* --jinja: 啟用jinja chat template
* --chat-template-kwargs: 開啟thinking 並設定成medium
* --no-mmap: 不要將權重載到主記憶體，減少主記憶體佔用
* -ngl: 參數載入到VRAM的層數
* --parallel: 多個並行對話或 API 請求
* --kv-unified: 多個並行對話，共用單一統一的 KV 緩衝區
* --no-context-shift: 對話或輸入長度超過上限時，伺服器不會自動幫你刪除或滑動舊內容
* --repeat-penalty: 懲罰已出現過的 Token, 1.0（預設／無懲罰）, 1.0 到 1.15（輕微懲罰，最常用）, 大於 1.2（強烈懲罰）
* --override-tensor: 利用正規表達式（Regex）精準指定：「哪些特定的張量留在 CPU，哪些張量丟給 GPU」如將專家層移至CPU(blk\.\d+\.ffn_.*_exps\.=CPU)


# qwen3.8.bat

```
@echo off
llama-server.exe ^
-m Qwen3.8-27B-Q4_K_M.gguf ^
-mm mmproj-BF16.gguf ^
-t 10 ^
-b 512 ^
-ub 256 ^
--ctx-size 262144 ^
-fa on ^
--cache-type-k q8_0 ^
--cache-type-v q8_0 ^
--spec-type draft-mtp ^
--spec-draft-n-max 3 ^
--jinja ^
--chat-template-kwargs "{\"enable_thinking\": true, \"preserve_think\": false, \"reasoning_effort\": \"medium\"}" ^
--no-mmap ^
--fit off ^
--no-context-shift ^
--repeat-penalty 1.0 ^
--metrics ^
--parallel 2 ^
--kv-unified ^
--host 0.0.0.0 ^
--port 8080 ^
--temp 0.6 ^
--top-p 0.5 ^
--top-k 15

```
