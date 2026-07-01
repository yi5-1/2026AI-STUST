# 客戶端入口：Lobby (選 IP/ID/造型/顏色) → 連線 → 進入遊戲
# 用法：python client.py

import socket
import json
import sys

import pygame

from constants import PORT
from lobby import show_lobby
from game  import run_game


def main():
    # 1) 顯示大廳，讓玩家選 Server IP / ID / 造型 / 顏色
    config = show_lobby()
    if config is None:
        pygame.quit()
        return

    # 2) 連線
    sock = socket.socket()
    try:
        sock.connect((config["ip"], PORT))
    except OSError as e:
        print(f"連線失敗：{e}")
        pygame.quit()
        return

    # 3) 送出 join 訊息 → 進入遊戲
    join = {
        "type":  "join",
        "id":    config["id"],
        "shape": config["shape"],
        "color": config["color"],
    }
    try:
        sock.sendall((json.dumps(join) + "\n").encode("utf-8"))
    except OSError as e:
        print(f"傳送 join 失敗：{e}")
        pygame.quit()
        sock.close()
        return

    # 4) 主遊戲迴圈
    try:
        run_game(sock, config)
    finally:
        try:
            sock.close()
        except OSError:
            pass
        pygame.quit()


if __name__ == "__main__":
    main()
