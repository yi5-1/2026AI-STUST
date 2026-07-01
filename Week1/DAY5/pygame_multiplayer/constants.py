# 全部共用常數 — server 和 client 都 import 這個檔案
# 只改一個地方，兩邊就一致

PORT = 5555

# 世界 / 螢幕大小
WORLD_W = 2000
WORLD_H = 2000
SCREEN_W = 1000
SCREEN_H = 700
TICK_HZ = 30           # server 每秒廣播次數

# 玩家
PLAYER_SIZE = 16
MAX_HP = 100
MOVE_SPEED = 260       # 像素/秒

# 子彈
BULLET_SPEED = 500     # 中等速度
BULLET_RADIUS = 5
BULLET_DAMAGE = 5      # 20 發 × 5 = 100 HP，剛好打死
BULLET_LIFETIME = 1.5  # 子彈存活秒數

# 補血道具
PICKUP_HEAL = 25
PICKUP_RADIUS = 14
PICKUP_MAX = 6                 # 場上同時最多幾個
PICKUP_SPAWN_INTERVAL = 4      # 幾秒生成一個

# UI
MINIMAP_SIZE = 180
CHAT_DURATION = 5              # 聊天泡泡秒數

# 選單可選項
SHAPES = ["circle", "square", "triangle"]
COLORS = [
    ("紅", [220,  50,  50]),
    ("藍", [ 50, 100, 220]),
    ("綠", [ 50, 200,  80]),
    ("黃", [240, 220,  60]),
    ("紫", [180,  80, 220]),
]
