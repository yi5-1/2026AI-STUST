# 大廳畫面：用 pygame 讓玩家用滑鼠選 Server IP、ID、造型、顏色
# show_lobby() 回傳 dict {"ip","id","shape","color"}，若視窗被關閉則回傳 None

import pygame
from constants import SCREEN_W, SCREEN_H, SHAPES, COLORS


def show_lobby():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("加入遊戲")
    try:
        font  = pygame.font.SysFont("Microsoft JhengHei", 20)
        big   = pygame.font.SysFont("Microsoft JhengHei", 32, bold=True)
        small = pygame.font.SysFont("Microsoft JhengHei", 16)
    except Exception:
        font  = pygame.font.Font(None, 22)
        big   = pygame.font.Font(None, 36)
        small = pygame.font.Font(None, 18)
    clock = pygame.time.Clock()
    pygame.key.stop_text_input()

    # 狀態
    ip_text     = "127.0.0.1"
    id_text     = ""
    shape_idx   = 0
    color_idx   = 0
    focus       = None     # "ip" | "id" | None

    # 版面矩形（一次算好，之後 event / draw 都用同一組）
    ip_rect      = pygame.Rect(300, 150, 400, 40)
    id_rect      = pygame.Rect(300, 220, 400, 40)
    shape_rects  = [pygame.Rect(300 + i * 100, 300, 80, 80) for i in range(len(SHAPES))]
    color_rects  = [pygame.Rect(300 + i * 70,  420, 60, 60) for i in range(len(COLORS))]
    connect_rect = pygame.Rect(400, 540, 200, 60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                focus = None
                pygame.key.stop_text_input()

                if ip_rect.collidepoint(mx, my):
                    focus = "ip"; pygame.key.start_text_input()
                elif id_rect.collidepoint(mx, my):
                    focus = "id"; pygame.key.start_text_input()

                for i, r in enumerate(shape_rects):
                    if r.collidepoint(mx, my):
                        shape_idx = i
                for i, r in enumerate(color_rects):
                    if r.collidepoint(mx, my):
                        color_idx = i

                if connect_rect.collidepoint(mx, my):
                    if ip_text.strip() and id_text.strip():
                        pygame.key.stop_text_input()
                        return {
                            "ip":    ip_text.strip(),
                            "id":    id_text.strip()[:12],
                            "shape": SHAPES[shape_idx],
                            "color": COLORS[color_idx][1],
                        }

            elif event.type == pygame.KEYDOWN:
                if focus == "ip" and event.key == pygame.K_BACKSPACE:
                    ip_text = ip_text[:-1]
                elif focus == "id" and event.key == pygame.K_BACKSPACE:
                    id_text = id_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if ip_text.strip() and id_text.strip():
                        pygame.key.stop_text_input()
                        return {
                            "ip":    ip_text.strip(),
                            "id":    id_text.strip()[:12],
                            "shape": SHAPES[shape_idx],
                            "color": COLORS[color_idx][1],
                        }

            elif event.type == pygame.TEXTINPUT:
                if focus == "ip":
                    ip_text += event.text
                elif focus == "id":
                    id_text += event.text

        # ====== 繪製 ======
        screen.fill((30, 30, 50))

        title = big.render("加入遊戲", True, (255, 255, 255))
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        # IP 欄位
        screen.blit(font.render("Server IP：", True, (255, 255, 255)), (190, 158))
        pygame.draw.rect(screen, (255, 255, 255), ip_rect)
        pygame.draw.rect(screen, (255, 220, 0) if focus == "ip" else (150, 150, 150), ip_rect, 3)
        screen.blit(font.render(ip_text, True, (0, 0, 0)), (ip_rect.x + 8, ip_rect.y + 8))

        # ID 欄位
        screen.blit(font.render("你的 ID：", True, (255, 255, 255)), (190, 228))
        pygame.draw.rect(screen, (255, 255, 255), id_rect)
        pygame.draw.rect(screen, (255, 220, 0) if focus == "id" else (150, 150, 150), id_rect, 3)
        screen.blit(font.render(id_text, True, (0, 0, 0)), (id_rect.x + 8, id_rect.y + 8))

        # 造型選擇
        screen.blit(font.render("造型：", True, (255, 255, 255)), (200, 330))
        for i, (name, r) in enumerate(zip(SHAPES, shape_rects)):
            pygame.draw.rect(screen, (60, 60, 80), r)
            pygame.draw.rect(screen, (255, 220, 0) if i == shape_idx else (150, 150, 150), r, 3)
            cx, cy = r.center
            col = tuple(COLORS[color_idx][1])
            if name == "circle":
                pygame.draw.circle(screen, col, (cx, cy), 25)
            elif name == "square":
                pygame.draw.rect(screen, col, (cx - 25, cy - 25, 50, 50))
            elif name == "triangle":
                pygame.draw.polygon(screen, col, [(cx, cy - 25), (cx - 25, cy + 25), (cx + 25, cy + 25)])

        # 顏色選擇
        screen.blit(font.render("顏色：", True, (255, 255, 255)), (200, 445))
        for i, ((cname, col), r) in enumerate(zip(COLORS, color_rects)):
            pygame.draw.rect(screen, tuple(col), r)
            pygame.draw.rect(screen, (255, 220, 0) if i == color_idx else (150, 150, 150), r, 3)

        # 連線按鈕
        can_connect = ip_text.strip() != "" and id_text.strip() != ""
        btn_col = (50, 180, 80) if can_connect else (80, 80, 80)
        pygame.draw.rect(screen, btn_col, connect_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), connect_rect, 2, border_radius=8)
        t = font.render("連線 (Enter)", True, (255, 255, 255))
        screen.blit(t, (connect_rect.centerx - t.get_width() // 2,
                        connect_rect.centery - t.get_height() // 2))

        # 操作提示
        hint = small.render("點擊欄位輸入文字  |  點擊造型/顏色選擇  |  Enter 連線", True, (200, 200, 200))
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 30))

        pygame.display.flip()
        clock.tick(60)
