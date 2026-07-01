# 遊戲主畫面：WASD 移動、左鍵射擊、Enter 聊天、HP 條、補血道具、GameOver 重生

import pygame
import threading
import json
import time

from constants import (
    WORLD_W, WORLD_H, SCREEN_W, SCREEN_H, MINIMAP_SIZE,
    MAX_HP, MOVE_SPEED, PLAYER_SIZE, CHAT_DURATION,
    BULLET_RADIUS, PICKUP_RADIUS,
)


def run_game(sock, config):
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(f"多人射擊 - {config['id']}")

    try:
        font = pygame.font.SysFont("Microsoft JhengHei", 16)
        big  = pygame.font.SysFont("Microsoft JhengHei", 32, bold=True)
        huge = pygame.font.SysFont("Microsoft JhengHei", 64, bold=True)
    except Exception:
        font = pygame.font.Font(None, 20)
        big  = pygame.font.Font(None, 40)
        huge = pygame.font.Font(None, 72)

    clock = pygame.time.Clock()
    pygame.key.stop_text_input()

    # ====== 狀態 ======
    my_id = config["id"]
    my_x, my_y = WORLD_W / 2, WORLD_H / 2

    latest = {"players": [], "bullets": [], "pickups": []}
    state_lock = threading.Lock()
    running = True

    chat_active = False
    chat_text   = ""

    # ====== 網路傳送 / 接收 ======
    def send(m):
        try:
            sock.sendall((json.dumps(m) + "\n").encode("utf-8"))
        except OSError:
            pass

    def recv_loop():
        buf = b""
        while running:
            try:
                data = sock.recv(8192)
            except OSError:
                return
            if not data:
                return
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                try:
                    msg = json.loads(line.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                if msg.get("type") == "state":
                    with state_lock:
                        latest["players"] = msg["players"]
                        latest["bullets"] = msg["bullets"]
                        latest["pickups"] = msg["pickups"]

    threading.Thread(target=recv_loop, daemon=True).start()

    # ====== 繪圖小工具 ======
    def draw_shape(surf, shape, col, sx, sy, size):
        col = tuple(col)
        if shape == "circle":
            pygame.draw.circle(surf, col, (sx, sy), size)
            pygame.draw.circle(surf, (0, 0, 0), (sx, sy), size, 2)
        elif shape == "square":
            r = pygame.Rect(sx - size, sy - size, size * 2, size * 2)
            pygame.draw.rect(surf, col, r)
            pygame.draw.rect(surf, (0, 0, 0), r, 2)
        elif shape == "triangle":
            pts = [(sx, sy - size), (sx - size, sy + size), (sx + size, sy + size)]
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    def draw_hp_bar(surf, sx, sy, hp):
        w, h = 40, 5
        x = sx - w // 2
        y = sy - PLAYER_SIZE - 12
        pygame.draw.rect(surf, (60, 0, 0), (x, y, w, h))
        pygame.draw.rect(surf, (60, 200, 60), (x, y, int(w * hp / MAX_HP), h))
        pygame.draw.rect(surf, (0, 0, 0), (x, y, w, h), 1)

    def draw_bubble(surf, sx, sy, text):
        if not text:
            return
        t = font.render(text, True, (0, 0, 0))
        w, h = t.get_size()
        pad = 6
        b = pygame.Rect(sx - w // 2 - pad, sy - PLAYER_SIZE - 30 - h - pad,
                        w + pad * 2, h + pad * 2)
        pygame.draw.rect(surf, (255, 255, 255), b, border_radius=8)
        pygame.draw.rect(surf, (0, 0, 0), b, 2, border_radius=8)
        tip = [(sx - 5, b.bottom), (sx + 5, b.bottom), (sx, b.bottom + 6)]
        pygame.draw.polygon(surf, (255, 255, 255), tip)
        pygame.draw.line(surf, (0, 0, 0), tip[0], tip[2], 2)
        pygame.draw.line(surf, (0, 0, 0), tip[1], tip[2], 2)
        surf.blit(t, (b.x + pad, b.y + pad))

    def find_me(snap):
        for p in snap:
            if p["id"] == my_id:
                return p
        return None

    # ====== 主迴圈 ======
    try:
        while running:
            dt = clock.tick(60) / 1000
            now = time.time()

            with state_lock:
                players_snap = list(latest["players"])
                bullets_snap = list(latest["bullets"])
                pickups_snap = list(latest["pickups"])

            me = find_me(players_snap)
            alive = (me is None) or me.get("alive", True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if chat_active:
                        if event.key == pygame.K_RETURN:
                            if chat_text.strip():
                                send({"type": "chat", "text": chat_text.strip()})
                            chat_text = ""
                            chat_active = False
                            pygame.key.stop_text_input()
                        elif event.key == pygame.K_BACKSPACE:
                            chat_text = chat_text[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            chat_text = ""
                            chat_active = False
                            pygame.key.stop_text_input()
                    else:
                        if event.key == pygame.K_RETURN:
                            if alive:
                                chat_active = True
                                pygame.key.start_text_input()
                            else:
                                send({"type": "respawn"})

                elif event.type == pygame.TEXTINPUT and chat_active:
                    chat_text += event.text

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if alive and not chat_active:
                        mx, my = event.pos
                        # 我在螢幕中央，所以滑鼠位置減中央就是方向向量
                        dx = mx - SCREEN_W / 2
                        dy = my - SCREEN_H / 2
                        if dx * dx + dy * dy > 4:
                            send({"type": "shoot", "dx": dx, "dy": dy})

            # 移動（活著且沒在打字時才能動）
            if alive and not chat_active:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]: my_y -= MOVE_SPEED * dt
                if keys[pygame.K_s]: my_y += MOVE_SPEED * dt
                if keys[pygame.K_a]: my_x -= MOVE_SPEED * dt
                if keys[pygame.K_d]: my_x += MOVE_SPEED * dt
                my_x = max(0, min(WORLD_W, my_x))
                my_y = max(0, min(WORLD_H, my_y))
                send({"type": "update", "x": my_x, "y": my_y})
            elif me:
                # 死亡狀態下讓相機跟著 server 給的位置（尤其是重生後）
                my_x = me.get("x", my_x)
                my_y = me.get("y", my_y)

            # 相機以自己為中心
            cam_x = my_x - SCREEN_W / 2
            cam_y = my_y - SCREEN_H / 2

            screen.fill((240, 240, 220))

            # 地圖格線
            grid = 100
            gx0 = int(-cam_x % grid)
            gy0 = int(-cam_y % grid)
            for x in range(gx0, SCREEN_W, grid):
                pygame.draw.line(screen, (210, 210, 190), (x, 0), (x, SCREEN_H))
            for y in range(gy0, SCREEN_H, grid):
                pygame.draw.line(screen, (210, 210, 190), (0, y), (SCREEN_W, y))

            # 世界邊界
            pygame.draw.rect(screen, (150, 150, 150),
                             pygame.Rect(-cam_x, -cam_y, WORLD_W, WORLD_H), 3)

            # 補血道具
            for pk in pickups_snap:
                sx = int(pk["x"] - cam_x)
                sy = int(pk["y"] - cam_y)
                if -50 < sx < SCREEN_W + 50 and -50 < sy < SCREEN_H + 50:
                    pygame.draw.circle(screen, (100, 220, 100), (sx, sy), PICKUP_RADIUS)
                    pygame.draw.circle(screen, (0, 0, 0), (sx, sy), PICKUP_RADIUS, 2)
                    # 白十字
                    pygame.draw.rect(screen, (255, 255, 255), (sx - 2, sy - 7, 4, 14))
                    pygame.draw.rect(screen, (255, 255, 255), (sx - 7, sy - 2, 14, 4))

            # 玩家
            for p in players_snap:
                sx = int(p["x"] - cam_x)
                sy = int(p["y"] - cam_y)
                if not (-50 < sx < SCREEN_W + 50 and -50 < sy < SCREEN_H + 50):
                    continue
                if p.get("alive", True):
                    draw_shape(screen, p["shape"], p["color"], sx, sy, PLAYER_SIZE)
                    draw_hp_bar(screen, sx, sy, p["hp"])
                else:
                    # 死亡樣式：灰圈 + X_X
                    pygame.draw.circle(screen, (120, 120, 120), (sx, sy), PLAYER_SIZE, 2)
                    xx = font.render("X_X", True, (120, 120, 120))
                    screen.blit(xx, (sx - xx.get_width() // 2, sy - xx.get_height() // 2))
                id_s = font.render(p["id"], True, (0, 0, 0))
                screen.blit(id_s, (sx - id_s.get_width() // 2, sy + PLAYER_SIZE + 6))
                if p.get("chat") and now - p.get("chat_time", 0) < CHAT_DURATION:
                    draw_bubble(screen, sx, sy, p["chat"])

            # 子彈
            for b in bullets_snap:
                sx = int(b["x"] - cam_x)
                sy = int(b["y"] - cam_y)
                if -50 < sx < SCREEN_W + 50 and -50 < sy < SCREEN_H + 50:
                    pygame.draw.circle(screen, (255, 80, 20), (sx, sy), BULLET_RADIUS)
                    pygame.draw.circle(screen, (0, 0, 0), (sx, sy), BULLET_RADIUS, 1)

            # 準心
            if alive and not chat_active:
                mx, my = pygame.mouse.get_pos()
                pygame.draw.line(screen, (0, 0, 0), (mx - 8, my), (mx + 8, my), 2)
                pygame.draw.line(screen, (0, 0, 0), (mx, my - 8), (mx, my + 8), 2)

            # 小地圖
            mm_x, mm_y = 10, SCREEN_H - MINIMAP_SIZE - 10
            mm_rect = pygame.Rect(mm_x, mm_y, MINIMAP_SIZE, MINIMAP_SIZE)
            pygame.draw.rect(screen, (30, 30, 30), mm_rect)
            pygame.draw.rect(screen, (255, 255, 255), mm_rect, 2)
            # 相機視野
            view_x = mm_x + cam_x * MINIMAP_SIZE / WORLD_W
            view_y = mm_y + cam_y * MINIMAP_SIZE / WORLD_H
            view_w = SCREEN_W * MINIMAP_SIZE / WORLD_W
            view_h = SCREEN_H * MINIMAP_SIZE / WORLD_H
            pygame.draw.rect(screen, (255, 255, 0),
                             pygame.Rect(view_x, view_y, view_w, view_h), 1)
            for pk in pickups_snap:
                mx = mm_x + int(pk["x"] * MINIMAP_SIZE / WORLD_W)
                my = mm_y + int(pk["y"] * MINIMAP_SIZE / WORLD_H)
                pygame.draw.circle(screen, (100, 220, 100), (mx, my), 3)
            for p in players_snap:
                if not p.get("alive", True):
                    continue
                mx = mm_x + int(p["x"] * MINIMAP_SIZE / WORLD_W)
                my = mm_y + int(p["y"] * MINIMAP_SIZE / WORLD_H)
                pygame.draw.circle(screen, tuple(p["color"]), (mx, my), 3)

            # HUD 血條（自己）
            if me:
                hp = me["hp"]
                pygame.draw.rect(screen, (60, 0, 0), (10, 10, 300, 24))
                pygame.draw.rect(screen, (60, 200, 60), (10, 10, int(300 * hp / MAX_HP), 24))
                pygame.draw.rect(screen, (255, 255, 255), (10, 10, 300, 24), 2)
                hp_text = font.render(f"HP {hp} / {MAX_HP}", True, (255, 255, 255))
                screen.blit(hp_text, (15, 12))

            # 玩家數
            cnt = font.render(f"線上：{len(players_snap)}", True, (0, 0, 0))
            screen.blit(cnt, (SCREEN_W - cnt.get_width() - 10, 10))

            # 聊天輸入欄
            if chat_active:
                box = pygame.Rect(10, SCREEN_H - 40, SCREEN_W - 20, 30)
                pygame.draw.rect(screen, (255, 255, 255), box)
                pygame.draw.rect(screen, (0, 0, 0), box, 2)
                t = font.render("> " + chat_text, True, (0, 0, 0))
                screen.blit(t, (box.x + 6, box.y + 6))
            else:
                hint = font.render("WASD 移動 | 滑鼠左鍵射擊 | Enter 打字", True, (80, 80, 80))
                screen.blit(hint, (10, SCREEN_H - 25))

            # GameOver 遮罩
            if me and not me.get("alive", True):
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                go = huge.render("GAME OVER", True, (255, 60, 60))
                screen.blit(go, (SCREEN_W // 2 - go.get_width() // 2, SCREEN_H // 2 - 80))
                hint2 = big.render("按 Enter 重生", True, (255, 255, 255))
                screen.blit(hint2, (SCREEN_W // 2 - hint2.get_width() // 2, SCREEN_H // 2 + 10))

            pygame.display.flip()

    finally:
        running = False
