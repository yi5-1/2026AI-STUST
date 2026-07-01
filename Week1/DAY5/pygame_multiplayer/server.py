# 多人小遊戲 - 伺服器端
# 責任：管理玩家 / 子彈 / 補血道具的狀態，30Hz 廣播給所有 client

import socket
import threading
import json
import time
import math
import random

from constants import (
    PORT, WORLD_W, WORLD_H, TICK_HZ,
    MAX_HP, BULLET_SPEED, BULLET_LIFETIME, BULLET_RADIUS, BULLET_DAMAGE,
    PLAYER_SIZE, PICKUP_HEAL, PICKUP_RADIUS, PICKUP_MAX, PICKUP_SPAWN_INTERVAL,
)

HOST = "0.0.0.0"

# ====== 共享狀態 ======
players = {}   # {cid: {"id","x","y","shape","color","hp","alive","chat","chat_time"}}
bullets = []   # [{"id","owner","x","y","vx","vy","t"}]
pickups = []   # [{"id","x","y"}]
conns   = []   # [(socket, cid)]
lock    = threading.Lock()

bullet_id_counter = 0
pickup_id_counter = 0


def 隨機重生點():
    return random.randint(200, WORLD_W - 200), random.randint(200, WORLD_H - 200)


def 遊戲Tick():
    """每 1/TICK_HZ 秒：移動子彈、處理碰撞、生成補血、廣播狀態"""
    global bullet_id_counter, pickup_id_counter
    last = time.time()
    last_pickup_spawn = 0

    while True:
        now = time.time()
        dt = now - last
        last = now

        with lock:
            # 1) 子彈移動 / 消失 / 命中
            for b in list(bullets):
                if now - b["t"] > BULLET_LIFETIME:
                    bullets.remove(b)
                    continue
                b["x"] += b["vx"] * dt
                b["y"] += b["vy"] * dt
                if b["x"] < 0 or b["x"] > WORLD_W or b["y"] < 0 or b["y"] > WORLD_H:
                    bullets.remove(b)
                    continue
                # 命中判定：跳過自己 & 已死玩家
                for cid, p in players.items():
                    if cid == b["owner"] or not p.get("alive", True):
                        continue
                    dx = p["x"] - b["x"]
                    dy = p["y"] - b["y"]
                    if dx * dx + dy * dy < (PLAYER_SIZE + BULLET_RADIUS) ** 2:
                        p["hp"] -= BULLET_DAMAGE
                        if p["hp"] <= 0:
                            p["hp"] = 0
                            p["alive"] = False
                        bullets.remove(b)
                        break

            # 2) 補血道具：定時補位到上限
            if now - last_pickup_spawn > PICKUP_SPAWN_INTERVAL and len(pickups) < PICKUP_MAX:
                pickup_id_counter += 1
                pickups.append({
                    "id": pickup_id_counter,
                    "x": random.randint(80, WORLD_W - 80),
                    "y": random.randint(80, WORLD_H - 80),
                })
                last_pickup_spawn = now

            # 3) 玩家撿補血
            for p in players.values():
                if not p.get("alive", True):
                    continue
                for pk in list(pickups):
                    dx = p["x"] - pk["x"]
                    dy = p["y"] - pk["y"]
                    if dx * dx + dy * dy < (PLAYER_SIZE + PICKUP_RADIUS) ** 2:
                        p["hp"] = min(MAX_HP, p["hp"] + PICKUP_HEAL)
                        pickups.remove(pk)

            # 4) 整包狀態
            state = {
                "type": "state",
                "players": list(players.values()),
                "bullets": [{"x": b["x"], "y": b["y"]} for b in bullets],
                "pickups": [{"x": pk["x"], "y": pk["y"]} for pk in pickups],
            }

        # 廣播
        msg = (json.dumps(state) + "\n").encode("utf-8")
        dead = []
        for conn, cid in list(conns):
            try:
                conn.sendall(msg)
            except OSError:
                dead.append((conn, cid))
        if dead:
            with lock:
                for conn, cid in dead:
                    if (conn, cid) in conns:
                        conns.remove((conn, cid))
                    players.pop(cid, None)
                    try:
                        conn.close()
                    except OSError:
                        pass

        time.sleep(1 / TICK_HZ)


def 處理單一連線(conn, cid, addr):
    global bullet_id_counter
    print(f"[{cid}] {addr} 已連線")
    conns.append((conn, cid))
    buf = b""
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                try:
                    msg = json.loads(line.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

                t = msg.get("type")
                with lock:
                    if t == "join":
                        x, y = 隨機重生點()
                        players[cid] = {
                            "id":    str(msg.get("id", f"P{cid}"))[:12],
                            "shape": msg.get("shape", "circle"),
                            "color": msg.get("color", [200, 50, 50]),
                            "x": x, "y": y,
                            "hp":    MAX_HP,
                            "alive": True,
                            "chat": "", "chat_time": 0,
                        }
                        print(f"[{cid}] 加入為 {players[cid]['id']}")

                    elif t == "update" and cid in players and players[cid].get("alive", True):
                        players[cid]["x"] = max(0, min(WORLD_W, float(msg.get("x", 0))))
                        players[cid]["y"] = max(0, min(WORLD_H, float(msg.get("y", 0))))

                    elif t == "shoot" and cid in players and players[cid].get("alive", True):
                        dx = float(msg.get("dx", 0))
                        dy = float(msg.get("dy", 0))
                        d = math.sqrt(dx * dx + dy * dy)
                        if d > 0:
                            bullet_id_counter += 1
                            bullets.append({
                                "id":    bullet_id_counter,
                                "owner": cid,
                                "x":     players[cid]["x"],
                                "y":     players[cid]["y"],
                                "vx":    dx / d * BULLET_SPEED,
                                "vy":    dy / d * BULLET_SPEED,
                                "t":     time.time(),
                            })

                    elif t == "chat" and cid in players:
                        players[cid]["chat"]      = str(msg.get("text", ""))[:80]
                        players[cid]["chat_time"] = time.time()

                    elif t == "respawn" and cid in players:
                        x, y = 隨機重生點()
                        players[cid]["hp"]    = MAX_HP
                        players[cid]["alive"] = True
                        players[cid]["x"]     = x
                        players[cid]["y"]     = y
    finally:
        with lock:
            players.pop(cid, None)
            conns[:] = [(c, i) for c, i in conns if i != cid]
        try:
            conn.close()
        except OSError:
            pass
        print(f"[{cid}] 中斷連線")


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server 開啟於 {HOST}:{PORT}(Ctrl+C 停止)")

    threading.Thread(target=遊戲Tick, daemon=True).start()

    cid_counter = 0
    try:
        while True:
            conn, addr = s.accept()
            cid_counter += 1
            threading.Thread(
                target=處理單一連線,
                args=(conn, cid_counter, addr),
                daemon=True,
            ).start()
    except KeyboardInterrupt:
        print("\nServer 關閉中...")
    finally:
        s.close()


if __name__ == "__main__":
    main()
