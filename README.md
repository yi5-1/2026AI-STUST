# 2026 AI - STUST 學習筆記

南臺科技大學 (STUST) 2026 AI 課程的個人練習與作業 repo，記錄從 Python 基礎、GUI、網頁、電腦視覺一路到深度學習 / YOLO 物件偵測 的完整學習過程。

---

## 目錄結構

```
project/
├── hello.md                          # Markdown 練習
├── Week1/                            # 第 1 週：基礎 → 電腦視覺
│   ├── DAY2/                         # Python 語法基礎
│   ├── DAY3/                         # 迴圈 + matplotlib
│   ├── DAY4/                         # pandas + tkinter GUI
│   ├── DAY5/                         # socket + pygame 多人遊戲
│   ├── DAY6/                         # aiohttp / Flask + DB + WebSocket
│   └── DAY7/                         # OpenCV 電腦視覺
├── Week2/                            # 第 2 週：專題整合 + 深度學習
│   ├── DAY8/                         # 期中專題整合日 (5 題選 1)
│   ├── DAY9/                         # CNN + Teachable Machine + MediaPipe
│   └── DAY10/                        # YOLO11n + Roboflow + Label Studio
└── README.md
```

---

## 學習脈絡（一路上升）

```
DAY2 語法基礎  →  DAY3 迴圈 + 視覺化  →  DAY4 pandas + tkinter GUI  →  DAY5 socket + pygame 多人
   (變數/條件)        (列表/檔案/plt)         (Excel/作業/GUI)              (TCP/threading/pygame)

→  DAY6 aiohttp + WebSocket + Canvas  →  DAY7 OpenCV 電腦視覺
   (瀏覽器多人 / DB / 會員系統)          (灰階/Canny/霍夫圓/形狀分類)

→  DAY8 期中專題（選題整合前 6 天）

→  DAY9 CNN + Teachable Machine + MediaPipe OD
   (預訓練 / 手刻 CNN / 遷移學習)

→  DAY10 YOLO11n 自訓練物件偵測
   (Roboflow 生態 / Label Studio 標註 / CCTV 車流量)
```

每個檔名都用中文命名（例如 `def 畢氏定理(a, b)`），方便對照當天課程主題快速回頭翻閱。

---

## Week 1 — 基礎到電腦視覺

### DAY 2 — Python 基礎語法
變數、型別、條件、布林邏輯、函式與模組。13 個小檔案，每個聚焦一個概念。
從 `變數教學.py` 到 `畢氏定理.py` 到 `斜向拋射.py`。

### DAY 3 — 迴圈、列表、CSV、matplotlib
`for/while` 迴圈、list、`csv.reader` 讀 CSV、matplotlib 折線 / 直方 / 散點 / 圓餅圖。
最後做「台南市各區人口比例」圓餅圖。

### DAY 4 — pandas + tkinter GUI
- `作業-湖西鄉人口圖表統計.py`：pandas 讀 Excel + matplotlib 出生死亡差方圖
- `GUI/` 子資料夾：11 個 tkinter 教學檔（`01_第一個視窗` → `10_湖西鄉人口GUI`），逐步教到把 matplotlib 嵌進 tkinter Canvas

### DAY 5 — socket + pygame 多人遊戲
- `Server.py` / `Client.py` / `ChatServer.py` — 最小 TCP echo + 聊天室
- `pygame_multiplayer/` — 多人 2D 遊戲（WASD 移動、小地圖、聊天泡泡、道具、Buff 系統）

### DAY 6 — Web + 資料庫
| 子專案 | 教什麼 |
|---|---|
| `web_basics/` | aiohttp + SQLite 留言板 — fetch / GET / POST / JSON / SQL 入門 |
| `web_auth/` | aiohttp + PostgreSQL + `.env` 讀密碼 — 註冊 / 登入兩個 API |
| `web_shooter/` | pygame 遊戲移植成瀏覽器版 — WebSocket + HTML5 Canvas |
| `電商平台/` | Flask + PostgreSQL 電商應用（含 spec 文件、admin 面板）|

### DAY 7 — OpenCV 電腦視覺
- `視覺.py` / `像素展示.py` — 基本操作
- `霍夫圓檢測.py` / `凸包檢測(幾何形狀分類).py` — 傳統 CV 算法
- `視角切換與形狀偵測.py` — trackbar 即時調參
- `tkinter影像處理工具.py` — 整合 tkinter GUI + OpenCV 即時處理

---

## Week 2 — 深度學習與物件偵測

### DAY 8 — 期中專題整合日
把 DAY2-7 學的技能組合成一個 demo 作品。5 個專題選 1：

| 專題 | 一句話 | 整合 |
|---|---|---|
| A_智慧視覺打卡系統 | 用鏡頭辨識 + 資料庫記錄出勤 | DAY7 + DAY4/6 + DAY3 |
| B_多人網頁遊戲排行榜 | web_shooter 加帳號、存分、排行榜 | DAY6 + DAY5 + DAY2 |
| C_開放資料分析儀表板 | 讀公開資料，互動式切換圖表 | DAY4 + DAY3 + DAY6 |
| D_體感操控小遊戲 | 用鏡頭偵測手勢控制 pygame | DAY7 + DAY5 + DAY2 |
| E_即時視覺監控站 | 一台擷取 + 多台瀏覽器同步觀看 | DAY7 + DAY6 + DAY5 |

每個資料夾裡有自己的 README + 起手式骨架。

### DAY 9 — CNN + Teachable Machine + MediaPipe
| 檔案 | 內容 |
|---|---|
| `01_什麼是CNN.md` | 白話介紹卷積 / 池化 / 全連接 |
| `02_Teachable_Machine_教學.md` | Google 網頁 GUI 訓練分類器（不寫程式） |
| `03_載入TM模型_鏡頭辨識.py` | 把 TM 匯出的 `.h5` 接上 webcam 即時分類 |
| `04_從零寫一個CNN_MNIST.py` | 手刻最小 CNN 訓練 MNIST |
| `05_遷移學習_MobileNet.py` | ImageNet 預訓練 MobileNetV2 分類鏡頭 |
| `06_作業_辨識自己的物體.py` | 空殼作業：接自己 TM 模型做應用 |
| `07_手寫辨識_tkinter.py` | tkinter 畫布用滑鼠寫數字 + CNN 預測 |
| `08_物件偵測_mediapipe.py` | MediaPipe EfficientDet-Lite0 webcam OD（COCO 80 類 + 中文標籤） |
| M1–M4 pptx | 機器學習導論 / 深度學習入門 / 工作流 / 模型部署 |

### DAY 10 — YOLO11n 自訓練 + Label Studio + CCTV
從**預訓練玩票 → 自訓練工業級 → 部署到即時串流**的完整流程。

**教學主線**（01-09 依序）：01_YOLO 觀念 → 02_預訓練玩 → 03_Roboflow 教學 → 04_下 dataset → 05_訓練 → 06_評估 → 07_推論 → 08_串流版 → 09_CCTV 車流量檢測（ByteTrack + 過線計數）

**工具**（不編號）：
- `convert_ls_json_to_yolo.py` — Label Studio 匯出的 JSON 轉 YOLO 訓練格式
- `ls_export_wrapper.py` — 學員區網一鍵下載完整 YOLO zip 的 server
- `get_cctv_url.py` — 自動抓 台中 CCTV 的 MJPEG 串流 URL
- `stream_test.py` — 純測 CCTV 連線
- `ls_gemma_backend.py` — Gemma 輔助標註 (experimental)

**文件**：
- `TRAINING_GUIDE.md` — CPU / GPU / Colab 各種硬體情境的參數建議、常見錯誤對照
- `HOMEWORK.md` — 期末作業指引

**範例資料集**：`datasets/fe/` 已 push 140 張標好的 Fe 樣本，`git clone` 就能訓練

詳見 [Week2/DAY10/README.md](Week2/DAY10/README.md)

---

## hello.md

Markdown 語法初體驗，練習標題與項目符號。

---

## 環境需求（依 DAY 分）

| DAY | 主要套件 |
|---|---|
| 2 / 3 | 內建 |
| 3 / 4 | matplotlib、pandas、openpyxl |
| 4 (GUI) | 內建（tkinter）|
| 5 | pygame |
| 6 | aiohttp、Flask、SQLAlchemy、psycopg2、python-dotenv |
| 7 | opencv-python、pillow、numpy |
| 8 | 依專題而定 |
| 9 | tensorflow、tf-keras、mediapipe、pillow、matplotlib（見 DAY9/requirements.txt）|
| 10 | ultralytics、roboflow、torch、pandas、opencv-python、flask（見 DAY10/requirements.txt）|

**中文字型**：matplotlib 與 GUI 統一用 `Microsoft JhengHei`（Windows 內建）。

---

## 給 clone 這個 repo 的學員的話

**依 DAY 順序看**，不要跳，每個 DAY 的作品是下一 DAY 的基礎。真的手癢想跳的話，最少也要先跑 DAY7 才進 DAY9 / DAY10（電腦視覺基礎沒有的話，YOLO 前的推理管線會看不懂）。

不同 DAY 的環境套件**盡量分開 conda env**（尤其 DAY9 的 TensorFlow 跟 DAY10 的 PyTorch）。或用一個大 env 但版本要照 DAY 的 requirements 鎖。

有問題看每個 DAY 的 README 或 TRAINING_GUIDE.md。
