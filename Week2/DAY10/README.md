# DAY10 — YOLO11n 物件偵測（從預訓練到自己訓練）

DAY9 教了 MediaPipe 的預訓練 OD 模型（只能認 COCO 80 類）。今天翻頁：**訓練自己想抓的東西**，並整合到即時應用（webcam / 網路串流 / CCTV）。

用 Ultralytics YOLO11n（2024 官方最新，小到 5.4MB 但準確度不俗）。

---

## 從 DAY9 → DAY10

| DAY9 (MediaPipe OD) | DAY10 (YOLO11n) |
|---|---|
| 預訓練，80 類固定 | **可自己訓練，類別自由** |
| .tflite 官方模型 | .pt PyTorch 模型 + Ultralytics 一鍵訓練 |
| 移動端友善 | Roboflow 生態圈 + 開發速度快 |
| 不能 fine-tune | 幾行 `model.train()` 就能 fine-tune |

---

## 檔案結構

```
Week2/DAY10/
├── README.md                    ← 你在讀
├── TRAINING_GUIDE.md            ← 訓練情境完整指南（CPU/GPU/Colab/雲端 路徑差異）
├── HOMEWORK.md                  ← 期末作業
├── requirements.txt
│
│  ─── 教學主線 (照 01 → 09 順序跑) ───
├── 01_什麼是YOLO.md
├── 02_預訓練yolo11n推論.py
├── 03_Roboflow下載dataset教學.md
├── 04_下載範例dataset.py
├── 05_訓練自己的YOLO.py
├── 06_評估訓練結果.py
├── 07_自訓練模型推論.py          ← imshow 版
├── 08_webcam串流推論.py          ← 瀏覽器串流版
├── 09_CCTV車流量檢測.py          ← 課程 finale
│
│  ─── 工具（不用照順序，需要時才用）───
├── convert_ls_json_to_yolo.py   ← Label Studio JSON → YOLO 訓練資料
├── get_cctv_url.py              ← 自動抓 台中 CCTV 的 MJPEG 串流 URL
├── ls_export_wrapper.py         ← 學員區網下載完整 YOLO zip 的 server (port 8082)
├── ls_gemma_backend.py          ← Gemma AI 輔助標註 backend (experimental)
├── stream_test.py               ← 純測 CCTV 串流連線（無 YOLO）
│
│  ─── 資料 ───
├── datasets/
│   ├── .gitkeep
│   └── fe/                     ← 範例：140 張 Fe 標註完整 dataset (已 push)
└── runs/                        ← 訓練結果 (gitignored)
```

---

## 教學主線一覽

| 檔案 | 內容 | 需要什麼 |
|---|---|---|
| `01_什麼是YOLO.md` | 概念白話：一鏡到底、v1 → 11 演進、跟 DAY9 對比 | 讀 |
| `02_預訓練yolo11n推論.py` | COCO 80 類預訓練 webcam 即時偵測（5 分鐘看到成果）| 跑 |
| `03_Roboflow下載dataset教學.md` | Roboflow Universe 拿 API key、下載步驟、人物 dataset 表 | 讀 |
| `04_下載範例dataset.py` | 用 roboflow 套件下 6 個常用資料集：剪刀石頭布 / 水族 / 口罩 / 西洋棋 / **工地帽子 / 純人物** | 跑 |
| `05_訓練自己的YOLO.py` | 自動掃 `datasets/` 讓你選、自動偵測 GPU 建議 batch size | 跑 |
| `06_評估訓練結果.py` | 讀 `runs/*/results.csv` 畫 mAP / Loss / Precision / Recall | 跑 |
| `07_自訓練模型推論.py` | 找最新 `best.pt` 上 webcam（**需要有 GUI 的 opencv-python**）| 跑 |
| `08_webcam串流推論.py` | 同 07 但改用**瀏覽器 MJPEG 串流** (port 9091)，避開 imshow 問題 | 跑 |
| `09_CCTV車流量檢測.py` | 台中 CCTV + ByteTrack 追蹤 + 過線計數 (port 9092) | 跑 |

---

## 工具說明

| 檔案 | 用途 |
|---|---|
| `convert_ls_json_to_yolo.py` | 把 Label Studio 匯出的 JSON 轉成 YOLO 訓練格式（自動拆 train/val/test + data.yaml）。支援本機 media 讀取 或 HTTP 從區網 LS 下載圖 |
| `get_cctv_url.py` | 用法：`python get_cctv_url.py C000002` → 印出 CCTV 實際 MJPEG 串流 URL（**永久有效**，不會過期）|
| `ls_export_wrapper.py` | 起 Flask server on 8082。學員瀏覽器打 <http://192.168.1.102:8082/> 就能點按鈕下載**含圖**的完整 YOLO zip |
| `ls_gemma_backend.py` | Label Studio ML backend 骨架，實驗性用 Gemma-31B 幫忙預標。實務上準確度不足，建議用 YOLO 預標更好 |
| `stream_test.py` | 純看 CCTV 畫面，不含 YOLO，用來驗證 stream URL 通不通 (port 9093) |

---

## 建議順序

1. `01`（觀念）→ `02`（先玩一下預訓練，5 分鐘看到成果）
2. `03`（Roboflow 開帳號拿 API key）→ `04`（下 dataset）
3. `05`（訓練）→ `06`（看結果）→ `07` 或 `08`（推論驗證）
4. `09`（實戰：CCTV 車流量）
5. `HOMEWORK.md`（回頭挑一個自己的題目）

---

## 訓練環境差異怎麼辦

不同學員硬體 / 環境 / 路徑都不一樣，請看 **[TRAINING_GUIDE.md](TRAINING_GUIDE.md)**：
- CPU / GTX / RTX / Colab 四種情境的參數建議
- 用 Label Studio 自標的資料怎麼接進來（本機 + 區網 HTTP fallback）
- 各種錯誤訊息對照表（OOM、cv2.imshow 掛掉、找不到 best.pt...）

---

## 各 server 埠號一覽（教室 demo 用）

| Server | Port | 起法 |
|---|---|---|
| Label Studio | 8081 | `label-studio start --host 0.0.0.0 --port 8081` |
| LS Export Wrapper | 8082 | `python ls_export_wrapper.py` |
| YOLO 自訓練模型串流 (08) | 9091 | `python 08_webcam串流推論.py` |
| CCTV 車流量檢測 (09) | 9092 | `python 09_CCTV車流量檢測.py` |
| CCTV 純串流測試 | 9093 | `python stream_test.py` |
| Gemma ML Backend | 9090 | `python ls_gemma_backend.py`（實驗）|
