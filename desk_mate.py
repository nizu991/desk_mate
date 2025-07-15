import tkinter as tk
import pyautogui
import time
import threading
import math
from PIL import Image, ImageTk
import sys
import os

class MascotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "white")

        self.canvas = tk.Canvas(self.root, width=200, height=200, bg='white', highlightthickness=0)
        self.exclaim = self.canvas.create_text(100, 20, text="！", font=("Rounded M Plus 1c", 30, "bold"), fill="red", state='hidden')
        self.canvas.pack()

        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        # 背景透過処理なしで画像読み込み
        self.img = tk.PhotoImage(file=os.path.join(base_path, "mascot_transparent.png"))
        self.img_L = tk.PhotoImage(file=os.path.join(base_path, "mascot_left.png"))
        self.img_R = tk.PhotoImage(file=os.path.join(base_path, "mascot_right.png"))
        self.img_sleep = tk.PhotoImage(file=os.path.join(base_path, "mascot_sleeping.png"))

        self.image_obj = self.canvas.create_image(100, 100, image=self.img)
        self.canvas.tag_bind(self.image_obj, "<Button-1>", self.wake_up)

        # 右クリック検知をダブルクリック検知に変更
        self.canvas.bind("<Double-Button-3>", self.close_app)

        self.x = 300
        self.y = 300
        self.root.geometry(f"+{self.x}+{self.y}")

        self.running = True
        self.asleep = False
        self.waking_up = False  # ← 追加: 「目覚め中」フラグ

        self.zzz_text = self.canvas.create_text(
            100, 30,
            text="Zzz...",
            font=("Rounded M Plus 1c", 16, "bold"),
            fill="#87CEFA",
            state='hidden'
        )

        threading.Thread(target=self.update_position, daemon=True).start()
        threading.Thread(target=self.sleep, daemon=True).start()
        threading.Thread(target=self.animate_zzz, daemon=True).start()

        self.root.mainloop()

    def load_image(self, filepath):
        img = Image.open(filepath).convert("RGBA")
        tk_img = ImageTk.PhotoImage(img)
        if not hasattr(self, '_image_refs'):
            self._image_refs = []
        self._image_refs.append(tk_img)
        return tk_img

    def sleep(self):
        sleep_counter = 0
        prev_pos = pyautogui.position()

        while self.running:
            curr_pos = pyautogui.position()

            if self.is_mouse_stationary(curr_pos, prev_pos):
                sleep_counter += 1
            else:
                sleep_counter = 0

            if sleep_counter >= 5 and not self.asleep:
                self.canvas.itemconfig(self.image_obj, image=self.img_sleep)
                self.canvas.itemconfig(self.zzz_text, state='normal')
                self.asleep = True

            prev_pos = curr_pos
            time.sleep(1)

    def wake_up(self, event=None):
        if self.asleep:
            self.waking_up = True  # ← 動作停止フラグ ON
            self.canvas.itemconfig(self.exclaim, state='normal')  # 「！」表示
            self.canvas.itemconfig(self.image_obj, image=self.img)
            self.canvas.itemconfig(self.zzz_text, state='hidden')
            self.asleep = False

        # 0.3秒後に「！」を非表示＆動作再開
            def end_wake_animation():
                self.canvas.itemconfig(self.exclaim, state='hidden')
                self.waking_up = False  # ← 動作再開

            self.root.after(500, end_wake_animation)

    def is_mouse_stationary(self, pos1, pos2, threshold=3):
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dist = math.hypot(dx, dy)
        return dist < threshold

    def update_position(self):
        while self.running:
            if not self.asleep and not self.waking_up:  # ← 起きていて、かつ目覚め中でないときだけ動く
                mx, my = pyautogui.position()
                dx = mx - self.x
                dy = my - self.y
                dist = math.hypot(dx, dy)

                if dist > 5:
                    speed = min(dist * 0.05, 10)
                    self.x += dx / dist * speed
                    self.y += dy / dist * speed

                    if dx < 0:
                        self.canvas.itemconfig(self.image_obj, image=self.img_L)
                    else:
                        self.canvas.itemconfig(self.image_obj, image=self.img_R)
                else:
                    self.canvas.itemconfig(self.image_obj, image=self.img)

            offset = math.sin(time.time() * 3) * 10
            self.root.geometry(f"+{int(self.x)}+{int(self.y + offset)}")

            time.sleep(0.02)


    def animate_zzz(self):
        phase = 0
        while self.running:
            if self.asleep:
                offset = math.sin(phase) * 5
                self.canvas.coords(self.zzz_text, 100, 30 + offset)
                phase += 0.2
            time.sleep(0.05)

    def close_app(self, event=None):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    MascotApp()
