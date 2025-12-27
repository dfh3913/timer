import tkinter as tk
from tkinter import font
import pygame
import os

# 初始化 pygame 混音器
pygame.init()
pygame.mixer.init()
# 加载音乐文件
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(base_dir, 'music.mp3')
    if not os.path.isfile(music_path):
        music_path = 'music.mp3'
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(1)
except Exception:
    print('Warning: music.mp3 not found or failed to load. 音频未加载。')
# 主应用类
class SimpleTimer:
    def __init__(self):
        self.root = tk.Tk()
        # 颜色和字体设置
        self.bg_color = "#000000"
        self.fg_color = "#FFFFFF"
        self.alpha_value = 0.8
        self.font_family = "HarmonyOS Sans SC" 
        # 计时变量
        self.set_mins = 0
        self.set_secs = 0
        self.remaining_seconds = 0
        self.is_paused = True
        self.is_running = False
        self.timer_id = None
        self.played_at_three = False
        # 结束后暂停音乐的计划 ID
        self.pause_after_end_id = None
        # 界面设置与组件创建
        self.setup_window()
        self.create_widgets()
        self.root.mainloop()
    # 新方法占位符
    def new_method(self):
        return None
    # 设置窗口属性
    def setup_window(self):
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", self.alpha_value)
        self.root.configure(bg=self.bg_color)
        # 居中显示
        sw = self.root.winfo_screenwidth()
        win_w = int(sw / 2)
        win_h = 60
        self.root.geometry(f"{win_w}x{win_h}+{int((sw-win_w)/2)}+0")
    # 创建界面组件
    def create_widgets(self):
        # 字体设置
        f_main = (self.font_family, 32, "bold")
        f_side = (self.font_family, 14)

        # 布局框架
        left_f = tk.Frame(self.root, bg=self.bg_color)
        left_f.place(relx=0.05, rely=0.5, anchor="w")

        mid_f = tk.Frame(self.root, bg=self.bg_color)
        mid_f.place(relx=0.5, rely=0.5, anchor="center")

        right_f = tk.Frame(self.root, bg=self.bg_color)
        right_f.place(relx=0.95, rely=0.5, anchor="e")

        # 左侧快速设置（秒为单位：30s、1min、2min、3min）
        for t in [30, 60, 120, 180]:
            if t < 60:
                label_text = f"{t}秒"
            else:
                label_text = f"{t//60}分"
            l = tk.Label(left_f, text=label_text, font=f_side, bg=self.bg_color, fg=self.fg_color, cursor="hand2")
            l.pack(side=tk.LEFT, padx=5)
            l.bind("<Button-1>", lambda e, secs=t: self.quick_set(secs))
        # 中间计时显示
        self.timer_lbl = tk.Label(mid_f, text="00:00", font=f_main, bg=self.bg_color, fg=self.fg_color, cursor="hand2")
        self.timer_lbl.pack()
        self.timer_lbl.bind("<Button-1>", self.toggle_timer)
        # 右侧时间设置
        tk.Label(right_f, text="设置:", font=f_side, bg=self.bg_color, fg="#888888").pack(side=tk.LEFT)
        self.m_lbl = tk.Label(right_f, text="00", font=f_side, bg="#222222", fg=self.fg_color, width=3)
        self.m_lbl.pack(side=tk.LEFT, padx=2)
        tk.Label(right_f, text=":", font=f_side, bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.s_lbl = tk.Label(right_f, text="00", font=f_side, bg="#222222", fg=self.fg_color, width=3)
        self.s_lbl.pack(side=tk.LEFT, padx=2)
        #  绑定滚轮事件调整时间
        self.m_lbl.bind("<MouseWheel>", lambda e: self.on_scroll(e, "min"))
        self.s_lbl.bind("<MouseWheel>", lambda e: self.on_scroll(e, "sec"))
        # 双击关闭程序
        self.root.bind("<Double-Button-1>", lambda e: self.root.destroy())
    # 滚轮调整时间
    def on_scroll(self, event, target):
        delta = 1 if event.delta > 0 else -1
        if target == "min": self.set_mins = max(0, min(99, self.set_mins + delta))
        else: self.set_secs = max(0, min(59, self.set_secs + delta))
        self.m_lbl.config(text=f"{self.set_mins:02d}")
        self.s_lbl.config(text=f"{self.set_secs:02d}")
        self.stop_timer()
        self.remaining_seconds = self.set_mins * 60 + self.set_secs
        self.played_at_three = False
        if self.pause_after_end_id:
            try:
                self.root.after_cancel(self.pause_after_end_id)
            except Exception:
                pass
            self.pause_after_end_id = None
        self.update_display()
    # 快速按秒设置时间（接收总秒数）
    def quick_set(self, total_seconds):
        self.stop_timer()
        self.set_mins = total_seconds // 60
        self.set_secs = total_seconds % 60
        self.m_lbl.config(text=f"{self.set_mins:02d}"), self.s_lbl.config(text=f"{self.set_secs:02d}")
        self.remaining_seconds = total_seconds
        self.played_at_three = False
        if self.pause_after_end_id:
            try:
                self.root.after_cancel(self.pause_after_end_id)
            except Exception:
                pass
            self.pause_after_end_id = None
        self.update_display()
    # 切换计时状态
    def toggle_timer(self, e):
        if self.remaining_seconds <= 0: return
        if not self.is_running:
            self.is_running, self.is_paused = True, False
            self.tick()
        else:
            self.is_paused = not self.is_paused
            if not self.is_paused: self.tick()
    # 停止计时
    def stop_timer(self):
        self.is_running = False
        if self.timer_id:
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass
            self.timer_id = None
        # 取消结束后暂停音乐的计划
        if self.pause_after_end_id:
            try:
                self.root.after_cancel(self.pause_after_end_id)
            except Exception:
                pass
            self.pause_after_end_id = None
        # 重置播放标志
        self.played_at_three = False
    # 计时逻辑
    def tick(self):
        if self.is_running and not self.is_paused:
            if self.remaining_seconds > 0:
                self.update_display()
                # 在剩余3秒时播放音乐
                if self.remaining_seconds == 3 and not self.played_at_three:
                    try:
                        pygame.mixer.music.play(-1)
                    except Exception:
                        pass
                    self.played_at_three = True
                # 继续倒计时
                self.remaining_seconds -= 1
                self.timer_id = self.root.after(1000, self.tick)
            else:
                self.remaining_seconds = 0
                self.update_display()
                self.is_running = False
                self.timer_lbl.config(fg="#FF4444")
                # 倒计时结束后 5 秒暂停音乐
                if self.pause_after_end_id:
                    try:
                        self.root.after_cancel(self.pause_after_end_id)
                    except Exception:
                        pass
                self.pause_after_end_id = self.root.after(5000, self.pause_music)
    # 暂停音乐播放
    def pause_music(self):
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass
        self.pause_after_end_id = None
        self.played_at_three = False
    # 更新显示
    def update_display(self):
        m, s = divmod(self.remaining_seconds, 60)
        self.timer_lbl.config(text=f"{m:02d}:{s:02d}", fg=self.fg_color)
# 运行程序
if __name__ == "__main__":
    SimpleTimer()