# pygame 多人射擊小遊戲

多人 2D 射擊 demo：Server 1 台 + 多個 Client。

## 檔案結構
```
pygame_multiplayer/
├── constants.py   # 所有共用常數（世界大小、HP、子彈速度、造型/顏色清單...）
├── server.py      # 伺服器：管理玩家 / 子彈 / 補血道具、30Hz 廣播
├── client.py      # 客戶端入口：show_lobby() → 連線 → run_game()
├── lobby.py       # pygame 大廳畫面：IP / ID / 造型 / 顏色 選擇
├── game.py        # pygame 遊戲畫面：移動、射擊、HP、GameOver
└── README.md
```

## 功能

**遊玩**
- `WASD` 移動
- **滑鼠左鍵** 朝準心方向射擊子彈
- 每發子彈造成 **5 點傷害**（100 HP，**20 發打死**）
- 打死後畫面出現 `GAME OVER`，**按 Enter 隨機重生**
- 地圖上會隨機刷新綠色 **補血十字道具**，走過去自動撿，回 25 HP

**社交**
- 按 `Enter` 開聊天欄，中文英文都能打（IME 已修好）
- 送出後訊息變成頭頂 5 秒的對話泡泡

**畫面**
- 相機以自己為中心
- 左下角小地圖：顯示所有玩家 / 補血道具 / 目前視野框
- 頭上血條 + 螢幕左上大血條
- 準心跟著滑鼠

## 安裝
```bash
pip install pygame
```

## 執行

### 1) 開 Server（一台就好）
```bash
python server.py
```

### 2) 開 Client（多台都行）
```bash
python client.py
```
會跳出大廳視窗：
- 點 **Server IP** 欄位輸入（本機測試就 `127.0.0.1`）
- 點 **ID** 欄位輸入名字
- 點 **造型 / 顏色** 選按鈕（有黃色框的是目前選項）
- 點 **連線 (Enter)** 或按 Enter 進入遊戲

跨電腦要放行 Server 主機的 TCP 5555，兩台在同網段（能互相 ping）。

## 通訊協定

TCP，`\n` 分隔的 UTF-8 JSON。

| 方向 | type | 欄位 |
|---|---|---|
| C → S | `join`    | `id`, `shape`, `color` |
| C → S | `update`  | `x`, `y` |
| C → S | `shoot`   | `dx`, `dy`（方向向量，長度不重要）|
| C → S | `chat`    | `text` |
| C → S | `respawn` | (無) |
| S → C | `state`   | `players`, `bullets`, `pickups` |

Server 30Hz 廣播；子彈物理由 server 算（含碰撞、扣血、道具生成）。

## 參數調整

改 `constants.py` 就好，兩邊會同步：
- `MAX_HP` / `BULLET_DAMAGE`：打幾發死人（現在 100 / 5 → 20 發）
- `BULLET_SPEED`：子彈速度
- `PICKUP_HEAL` / `PICKUP_SPAWN_INTERVAL` / `PICKUP_MAX`：補血強度 / 頻率
- `MOVE_SPEED`：走路速度
