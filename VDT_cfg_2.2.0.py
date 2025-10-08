import tkinter as tk
from tkinter import ttk
import os
import sys
import tempfile
import pyautogui
import ctypes
from PIL import Image, ImageTk
import subprocess
import shutil

# nuitka打包关闭启动画面
if "NUITKA_ONEFILE_PARENT" in os.environ:
   splash_filename = os.path.join(
      tempfile.gettempdir(),
      "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
   )
   if os.path.exists(splash_filename):
      os.unlink(splash_filename)

# nuitka打包后获取文件路径
def get_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def backup_config_file():
    """备份数据文件"""
    original_path = r'data\data.csv'
    backup_dir = r'data'

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    if not os.path.exists(original_path):
        return

    max_backup_num = 0
    for filename in os.listdir(backup_dir):
        if filename.startswith('data.csv.'):
            backup_num = int(filename.split('.')[-1])
            if backup_num > max_backup_num:
                max_backup_num = backup_num

    new_backup_num = 1
    backup_path = os.path.join(backup_dir, f'data.csv.{new_backup_num:03d}')

    shutil.copy2(original_path, backup_path)
    return backup_path

backup_file = backup_config_file()

user32 = ctypes.windll.user32
SCREEN_WIDTH = user32.GetSystemMetrics(0)
SCREEN_HEIGHT = user32.GetSystemMetrics(1)

def load_config():
    """基础高度比例和预设坐标"""
    with open(r'data\data.csv', 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f.readlines()]

        mode_line = all_lines[0] if len(all_lines) > 0 else '1,'
        mode = int(mode_line.split(',')[0]) if mode_line else 1

        lines = []
        for line in all_lines[1:13]:
            if line and ',' in line:
                parts = line.split(',')
                lines.append(parts[mode].strip() if mode == 2 else parts[1].strip())
            else:
                lines.append('0')

        scale_factor = 1.0
        if len(all_lines) >= 15 and all_lines[14]:
            try:
                scale_factor = float(all_lines[14].split(',')[0])
            except:
                pass

    return {
        'WIN_HEIGHT_1': float(lines[0]) if len(lines) > 0 else 0.13,
        'SCALE_FACTOR': scale_factor,
        'WIN_POSITIONS': {
            'win1_x': float(lines[1]),
            'win2_x': float(lines[2]),
            'win3_x': float(lines[3]),
            'col_x': float(lines[4]),
            'h_y': float(lines[5]),
            'c_y': float(lines[6]),
            'a_y': float(lines[7]),
            'x_y': float(lines[8]),
            'w_y': float(lines[9]),
            's_y': float(lines[10]),
            'y_y': float(lines[11]),
        }
    }

# 读取配置
config = load_config()
WIN_HEIGHT_1 = config['WIN_HEIGHT_1']
WIN_POSITIONS = config['WIN_POSITIONS']

class ConfigTool:
    """设置主窗口"""
    def __init__(self, backup_file, main_app):
        self.backup_file = backup_file
        self.main_app = main_app
        self.root = tk.Toplevel()
        self.root.title("VD_Toggler配置工具 v2.2")
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.root.bind("<Unmap>", self.on_minimize)

        # 设置窗口图标
        icon_path = 'img/els/cfg.png'
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon_photo)

        # 窗口大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 860
        window_height = 560
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(True, True)

        # 计算基础字体大小
        self.base_font_size = -16
        self.title_font_size = -18
        self.button_font_size = -14

        # 创建字体对象
        font_family = ["Microsoft YaHei", "sans-serif"]
        self.default_font = (font_family[0], self.base_font_size)
        self.title_font = (font_family[0], self.title_font_size, 'bold', 'italic')
        self.issue_font = (font_family[0], self.base_font_size, 'bold')
        self.button_font = (font_family[0], self.button_font_size, 'bold')

        # 将窗口居中显示
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"+{x}+{y}")

        self.current_page = "功能"
        self.setup_ui()

    def setup_ui(self):
        """设置窗口内容"""
        self.root.configure(bg='WhiteSmoke')

        # 主容器
        main_frame = tk.Frame(self.root, bg='WhiteSmoke')
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 配置网格权重
        main_frame.grid_rowconfigure(0, weight=0)  # 页面切换按钮
        main_frame.grid_rowconfigure(1, weight=1)  # 页面内容区域
        main_frame.grid_rowconfigure(2, weight=0)  # 提示文本
        main_frame.grid_rowconfigure(3, weight=0)  # 底部按钮
        main_frame.grid_columnconfigure(0, weight=1)  # 单列布局

        # 提示文本
        label = tk.Label(main_frame,
                        text="你可以通过拖动按钮来自定义布局。\n若想保留更改，请点击“确定”；若想放弃更改，请点击“取消”。",
                        wraplength=0.16,font=self.default_font,justify="left",bg='WhiteSmoke')
        label.grid(row=2, column=0, columnspan=3, sticky="w", pady=(0, 15))

        # 页面切换按钮区域
        tab_frame = tk.Frame(main_frame, bg='WhiteSmoke')
        tab_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        # 功能按钮
        self.function_btn = tk.Button(tab_frame, text="功能", font=self.button_font,
                                     width=7, height=1, command=lambda: self.switch_page("功能"), bg='Gainsboro')
        self.function_btn.pack(side="left", padx=(0, 5))

        # UI按钮  
        self.ui_btn = tk.Button(tab_frame, text="UI", font=self.button_font,
                               width=7, height=1, command=lambda: self.switch_page("UI"), bg='WhiteSmoke')
        self.ui_btn.pack(side="left", padx=(5, 0))

        # 页面内容区域
        self.content_frame = tk.Frame(main_frame, bg='WhiteSmoke')
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # 底部按钮区域
        bottom_frame = tk.Frame(main_frame, bg='WhiteSmoke')
        bottom_frame.grid(row=3, column=0, sticky="ew")

        button_frame1 = tk.Frame(bottom_frame, bg='WhiteSmoke')
        button_frame1.pack(side="left")
        button_frame2 = tk.Frame(bottom_frame, bg='WhiteSmoke')
        button_frame2.pack(side="right")

        # 复原按钮
        reset_btn = tk.Button(button_frame1, text="复原", font=self.default_font, width=7,
                             command=self.show_reset_confirm, bg='white')
        reset_btn.pack(side="left")

        # 确定按钮
        ok_btn = tk.Button(button_frame2, text="确定", font=self.default_font, width=7,
                          command=self.on_ok, bg='white')
        ok_btn.pack(side="right", padx=(10, 0))

        # 取消按钮
        cancel_btn = tk.Button(button_frame2, text="取消", font=self.default_font, width=7,
                              command=self.on_cancel, bg='white')
        cancel_btn.pack(side="right")

        # 初始化功能页面
        self.create_function_page()

    def switch_page(self, page_name):
        """切换页面"""
        self.current_page = page_name

        if page_name == "功能":
            self.function_btn.config(bg='Gainsboro')
            self.ui_btn.config(bg='WhiteSmoke')
        else:
            self.function_btn.config(bg='WhiteSmoke')
            self.ui_btn.config(bg='Gainsboro')

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if page_name == "功能":
            self.create_function_page()
        else:
            self.create_ui_page()

    def create_function_page(self):
        """创建功能页面"""
        page_frame = tk.Frame(self.content_frame, bg='WhiteSmoke')
        page_frame.pack(fill="both", expand=True, padx=10)

        page_frame.grid_rowconfigure(0, weight=0)  # 瞬匿模式
        page_frame.grid_rowconfigure(1, weight=0)  # 自动静音
        page_frame.grid_rowconfigure(2, weight=0)  # 自动熄屏
        page_frame.grid_rowconfigure(3, weight=0)  # 快捷键
        page_frame.grid_columnconfigure(0, weight=1)

        # 瞬匿模式
        hide_frame = tk.LabelFrame(page_frame, text=" 瞬匿模式 ", font=self.title_font, bg='WhiteSmoke', padx=10, pady=5)
        hide_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=10)

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            current_hide = int(lines[13].split(',')[0])

        self.hide_var = tk.IntVar(value=current_hide)
        tk.Label(hide_frame, text="按钮在切换桌面后立即消失？", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(0, 10))
        tk.Radiobutton(hide_frame, text="是", font=self.default_font, variable=self.hide_var,
                      value=1, command=self.update_hide, bg='WhiteSmoke').pack(side="left", padx=(0, 10))
        tk.Radiobutton(hide_frame, text="否", font=self.default_font, variable=self.hide_var,
                      value=0, command=self.update_hide, bg='WhiteSmoke').pack(side="left")

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            current_hide_mode = int(lines[13].split(',')[1])

        self.hide_mode_var = tk.IntVar(value=current_hide_mode)
        tk.Label(hide_frame, text="按钮消失方式:", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(120, 10))
        tk.Radiobutton(hide_frame, text="隐藏", font=self.default_font, variable=self.hide_mode_var,
                      value=1, command=self.update_hide_mode, bg='WhiteSmoke').pack(side="left", padx=(0, 10))
        tk.Radiobutton(hide_frame, text="退出", font=self.default_font, variable=self.hide_mode_var,
                      value=2, command=self.update_hide_mode, bg='WhiteSmoke').pack(side="left")

        # 自动静音模式
        audio_frame = tk.LabelFrame(page_frame, text=" 自动静音 ", font=self.title_font, bg='WhiteSmoke', padx=10, pady=5)
        audio_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=10)

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            current_audio_mode = int(lines[15].split(',')[0])

        self.close_audio_var = tk.IntVar(value=current_audio_mode)
        tk.Label(audio_frame, text="在切换桌面时静音？", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(0, 10))
        tk.Radiobutton(audio_frame, text="是", font=self.default_font, variable=self.close_audio_var,
                      value=1, command=self.update_close_audio, bg='WhiteSmoke').pack(side="left", padx=(0, 10))
        tk.Radiobutton(audio_frame, text="否", font=self.default_font, variable=self.close_audio_var,
                      value=0, command=self.update_close_audio, bg='WhiteSmoke').pack(side="left")

        # 自动熄屏
        screen_frame = tk.LabelFrame(page_frame, text=" 自动熄屏 ", font=self.title_font, bg='WhiteSmoke', padx=10, pady=5)
        screen_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=10)

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            current_screen_mode = int(lines[13].split(',')[2])

        self.close_screen_var = tk.IntVar(value=current_screen_mode)
        tk.Label(screen_frame, text="在切换桌面时熄屏？", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(0, 10))
        tk.Radiobutton(screen_frame, text="是", font=self.default_font, variable=self.close_screen_var,
                      value=1, command=self.update_lock_screen, bg='WhiteSmoke').pack(side="left", padx=(0, 10))
        tk.Radiobutton(screen_frame, text="否", font=self.default_font, variable=self.close_screen_var,
                      value=0, command=self.update_lock_screen, bg='WhiteSmoke').pack(side="left")

        # 快捷键设置
        shortcut_frame = tk.LabelFrame(page_frame, text=" 附加快捷键 ", font=self.title_font, bg='WhiteSmoke', padx=10, pady=5)
        shortcut_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=10)

        shortcut_ctrl_frame = tk.Frame(shortcut_frame, bg='WhiteSmoke')
        shortcut_ctrl_frame.pack(fill="x", anchor="w")

        tk.Label(shortcut_ctrl_frame, text="切换桌面时触发:", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(0, 10))

        clear_btn = tk.Button(shortcut_ctrl_frame, text="清空", font=self.default_font, width=5, 
                             command=self.clear_shortcut_combs, bg='WhiteSmoke')
        clear_btn.pack(side="right", padx=(0, 10))

        add_btn = tk.Button(shortcut_ctrl_frame, text="+", font=self.default_font, width=3, 
                           command=self.add_shortcut_comb, bg='WhiteSmoke')
        add_btn.pack(side="right", padx=(0, 10))

        # 下拉框
        self.shortcut_comb_frame = tk.Frame(shortcut_ctrl_frame, bg='WhiteSmoke')
        self.shortcut_comb_frame.pack(fill="x", pady=(5, 0))

        self.shortcut_combs = []
        self.load_shortcut_config()

    def create_ui_page(self):
        """创建UI页面"""
        page_frame = tk.Frame(self.content_frame, bg='WhiteSmoke')
        page_frame.pack(fill="both", expand=True, padx=10)

        page_frame.grid_rowconfigure(0, weight=0)  # 基础设置
        page_frame.grid_rowconfigure(1, weight=0)  # 按钮大小
        page_frame.grid_rowconfigure(2, weight=0)  # 按钮不透明度
        page_frame.grid_rowconfigure(3, weight=0)  # 隐藏移速
        page_frame.grid_columnconfigure(0, weight=1)

        # 基础设置
        mode_frame = tk.LabelFrame(page_frame, text=" 基础设置 ", font=self.title_font, bg='WhiteSmoke', padx=10, pady=5)
        mode_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=10)

        with open(r'data\data.csv', 'r') as f:
            first_line = f.readline().strip()
            current_mode = int(first_line.split(',')[0]) if first_line else 1

        self.switch_var = tk.IntVar(value=current_mode)
        tk.Label(mode_frame, text="按钮位置:", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(0, 10))
        tk.Radiobutton(mode_frame, text="左侧", font=self.default_font, variable=self.switch_var,
                      value=2, command=self.update_switch, bg='WhiteSmoke').pack(side="left")
        tk.Radiobutton(mode_frame, text="右侧", font=self.default_font, variable=self.switch_var,
                      value=1, command=self.update_switch, bg='WhiteSmoke').pack(side="left", padx=(0, 10))

        with open(r'data\data.csv', 'r') as f:
            first_line = f.readline().strip()
            current_mode2 = int(first_line.split(',')[1]) if first_line else 0

        self.switch2_var = tk.IntVar(value=current_mode2)
        tk.Label(mode_frame, text="悬浮球位置:", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(230, 10))
        tk.Radiobutton(mode_frame, text="贴边", font=self.default_font, variable=self.switch2_var,
                      value=0, command=self.update_ball, bg='WhiteSmoke').pack(side="left")
        tk.Radiobutton(mode_frame, text="自由", font=self.default_font, variable=self.switch2_var,
                      value=1, command=self.update_ball, bg='WhiteSmoke').pack(side="left", padx=(0, 10))

        # 按钮大小设置
        size_frame = tk.LabelFrame(page_frame, text=" 按钮大小 ", font=self.title_font, bg='WhiteSmoke', padx=10, pady=10)
        size_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=10)

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            current_size = float(lines[14].split(',')[0])

        self.size_var = tk.DoubleVar(value=current_size)
        tk.Label(size_frame, text="按钮大小的缩放倍数:", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(0, 12))

        size_slider = tk.Scale(size_frame, from_=0.1, to=3.0, resolution=0.1, font=self.default_font,
                              orient=tk.HORIZONTAL, variable=self.size_var,
                              command=self.update_size_setting,
                              length=536, showvalue=0, bg='WhiteSmoke')
        size_slider.pack(side="left")

        self.size_value_label = tk.Label(size_frame, text=f"{current_size:.1f}", font=self.default_font, bg='WhiteSmoke')
        self.size_value_label.pack(side="left", padx=(10, 0))

        # 按钮不透明度
        alpha_frame = tk.LabelFrame(page_frame, text=" 按钮不透明度 ", font=self.title_font, bg='WhiteSmoke', padx=10, pady=10)
        alpha_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=10)

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 15:
                parts = lines[14].strip().split(',')
                current_alpha = float(parts[2]) if len(parts) > 2 else 0.3
            else:
                current_alpha = 0.3

        self.alpha_var = tk.DoubleVar(value=current_alpha)
        tk.Label(alpha_frame, text="图形按钮:", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(0, 12))

        alpha_slider = tk.Scale(alpha_frame, from_=0.1, to=1.0, resolution=0.1, font=self.default_font,
                               orient=tk.HORIZONTAL, variable=self.alpha_var,
                               command=self.update_alpha_setting,
                               length=220, showvalue=0, bg='WhiteSmoke')
        alpha_slider.pack(side="left")

        self.alpha_value_label = tk.Label(alpha_frame, text=f"{current_alpha:.1f}", font=self.default_font, bg='WhiteSmoke')
        self.alpha_value_label.pack(side="left", padx=(10, 0))

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 15:
                parts = lines[14].strip().split(',')
                current_alpha2 = float(parts[3]) if len(parts) > 2 else 0.8
            else:
                current_alpha2 = 0.8

        self.alpha2_var = tk.DoubleVar(value=current_alpha2)
        tk.Label(alpha_frame, text="文字按钮:", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(46, 12))

        alpha2_slider = tk.Scale(alpha_frame, from_=0.1, to=1.0, resolution=0.1, font=self.default_font,
                               orient=tk.HORIZONTAL, variable=self.alpha2_var,
                               command=self.update_alpha2_setting,
                               length=220, showvalue=0, bg='WhiteSmoke')
        alpha2_slider.pack(side="left")

        self.alpha2_value_label = tk.Label(alpha_frame, text=f"{current_alpha2:.1f}", font=self.default_font, bg='WhiteSmoke')
        self.alpha2_value_label.pack(side="left", padx=(10, 0))

        # 隐藏移速设置
        speed_frame = tk.LabelFrame(page_frame, text=" 隐藏移速 ", font=self.title_font, bg='WhiteSmoke', padx=10, pady=10)
        speed_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=10)

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 15:
                parts = lines[14].strip().split(',')
                current_speed = float(parts[1]) if len(parts) > 1 else 1.0
            else:
                current_speed = 1.0

        self.speed_var = tk.DoubleVar(value=current_speed)
        tk.Label(speed_frame, text="隐藏时按钮移速的倍数:", font=self.issue_font, bg='WhiteSmoke').pack(side="left", padx=(0, 12))

        speed_slider = tk.Scale(speed_frame, from_=0.2, to=3.0, resolution=0.2, font=self.default_font,
                               orient=tk.HORIZONTAL, variable=self.speed_var,
                               command=self.update_speed_setting,
                               length=520, showvalue=0, bg='WhiteSmoke')
        speed_slider.pack(side="left")

        self.speed_value_label = tk.Label(speed_frame, text=f"{current_speed:.1f}", font=self.default_font, bg='WhiteSmoke')
        self.speed_value_label.pack(side="left", padx=(10, 0))

    def update_switch(self):
        """更新左右模式状态到配置文件"""
        selected_mode = self.switch_var.get()
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            if not lines:
                lines = ["1,0,\n"]
            parts = lines[0].strip().split(',')
            if len(parts) < 2:
                parts = ['1', '0']
            parts[0] = str(selected_mode)
            lines[0] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

        self.main_app.mode = selected_mode
        self.main_app.reload_windows()

    def update_ball(self):
        """更新悬浮球状态到配置文件"""
        selected_mode = self.switch2_var.get()
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            if not lines:
                lines = ["1,0,\n"]
            parts = lines[0].strip().split(',')
            if len(parts) < 2:
                parts = ['1', '0']
            parts[1] = str(selected_mode)
            lines[0] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

    def update_hide(self):
        """更新是否开启瞬匿模式到配置文件"""
        selected_mode = self.hide_var.get()
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            while len(lines) < 14:
                lines.append("0\n")
            parts = lines[13].strip().split(',')
            if len(parts) < 2:
                parts = ['0', '1']
            parts[0] = str(selected_mode)
            lines[13] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

    def update_hide_mode(self):
        """更新瞬匿模式方式到配置文件"""
        selected_mode = self.hide_mode_var.get()
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            while len(lines) < 14:
                lines.append("0\n")
            parts = lines[13].strip().split(',')
            if len(parts) < 2:
                parts = ['0', '1']
            parts[1] = str(selected_mode)
            lines[13] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

    def update_close_audio(self):
        """更新自动静音模式到配置文件"""
        selected_mode = self.close_audio_var.get()
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            while len(lines) < 16:
                lines.append("0\n")
            parts = lines[15].strip().split(',')
            if len(parts) < 2:
                parts = ['0', '1']
            parts[0] = str(selected_mode)
            lines[15] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

    def update_lock_screen(self):
        """更新自动熄屏模式到配置文件"""
        selected_mode = self.close_screen_var.get()
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            parts = lines[13].strip().split(',')
            parts[2] = str(selected_mode)
            lines[13] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

    def update_size_setting(self, value):
        """更新按钮大小设置到配置文件"""
        self.size_value_label.config(text=f"{float(value):.1f}")
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            while len(lines) < 15:
                lines.append("1.0\n")
            parts = lines[14].strip().split(',')
            if len(parts) < 1:
                parts = ['1.0']
            parts[0] = str(float(value))
            lines[14] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

        self.main_app.reload_windows()

    def update_alpha_setting(self, value):
        """更新图形按钮透明度设置到配置文件"""
        alpha_value = float(value)
        self.alpha_value_label.config(text=f"{alpha_value:.1f}")
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            parts = lines[14].strip().split(',')
            if len(parts) < 3:
                parts = ['1.0', '1.0', '0.3', '0.8']
            parts[2] = str(alpha_value)
            lines[14] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

        self.main_app.reload_windows()

    def update_alpha2_setting(self, value):
        """更新文字按钮透明度设置到配置文件"""
        alpha2_value = float(value)
        self.alpha2_value_label.config(text=f"{alpha2_value:.1f}")
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            parts = lines[14].strip().split(',')
            if len(parts) < 3:
                parts = ['1.0', '1.0', '0.3', '0.8']
            parts[3] = str(alpha2_value)
            lines[14] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

        self.main_app.reload_windows()

    def update_speed_setting(self, value):
        """更新移动速度设置到配置文件"""
        speed_value = float(value)
        self.speed_value_label.config(text=f"{speed_value:.1f}")
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            while len(lines) < 15:
                lines.append("1.0\n")
            parts = lines[14].strip().split(',')
            if len(parts) < 2:
                parts = ['1.0', '1.0']
            parts[1] = str(speed_value)
            lines[14] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

    def load_shortcut_config(self):
        """读取数据加载快捷键下拉框"""
        with open(r'data\data.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            while len(lines) < 17:
                lines.append("")
            shortcut_line = lines[16].strip()
            shortcuts = shortcut_line.split(',') if shortcut_line else []
            for key in shortcuts[:4]:
                self.add_shortcut_comb(init_key=key)

    def add_shortcut_comb(self, init_key=None):
        """添加快捷键下拉框"""
        if len(self.shortcut_combs) >= 4:  # 限制最多4个下拉框
            return

        # 定义支持的按键选项
        key_options = [
            "请选择", "Ctrl", "Alt", "Shift", "Win",
            "Enter", "Space", "Backspace", "Tab", "Esc", "Left", "Right", "Up", "Down",
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
        ]

        # 创建下拉框
        comb = ttk.Combobox(self.shortcut_comb_frame, values=key_options, font=self.default_font, state="readonly", width=10)

        # 初始化选中值
        if init_key and init_key in key_options:
            comb.current(key_options.index(init_key))
        else:
            comb.current(0)

        comb.pack(side="left", padx=(0, 10), pady=(0, 5))
        self.shortcut_combs.append(comb)  # 加入管理列表

        # 绑定选择变化事件
        comb.bind("<<ComboboxSelected>>", self.update_shortcut_config)

    def clear_shortcut_combs(self):
        """清空快捷键下拉框"""
        for comb in self.shortcut_combs:
            comb.destroy()
        self.shortcut_combs.clear()
        self.update_shortcut_config()

    def update_shortcut_config(self, event=None):
        """保存下拉框选中的快捷键"""
        valid_shortcuts = [comb.get() for comb in self.shortcut_combs if comb.get() != "请选择"][:4]
        shortcut_str = ','.join(valid_shortcuts)  # 转换为字符串

        with open(r'data\data.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            while len(lines) < 17:
                lines.append("")
            lines[16] = shortcut_str + "\n"

        with open(r'data\data.csv', 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def on_ok(self):
        """点击确定按钮的处理"""
        if self.backup_file and os.path.exists(self.backup_file):
            os.remove(self.backup_file)  # 删除备份文件
        self.root.destroy()
        self.main_app.root.quit()

    def on_cancel(self):
        """点击取消按钮的处理"""
        original_file = r'data\data.csv'
        if self.backup_file and os.path.exists(self.backup_file):
            if os.path.exists(original_file):
                os.remove(original_file)  # 删除当前配置文件
            shutil.move(self.backup_file, original_file)
        self.root.destroy()
        self.main_app.root.quit()

    def on_minimize(self, event):
        """窗口最小化时的处理"""
        if event.widget != self.root:
            return
        # 隐藏所有VirtualDesktopToggler窗口
        for win in self.main_app.windows.values():
            win.withdraw()
        self.root.bind("<Map>", self.on_restore)

    def on_restore(self, event):
        """窗口从最小化恢复时的处理"""
        if event.widget != self.root:
            return
        # 显示所有VirtualDesktopToggler窗口
        for win in self.main_app.windows.values():
            win.deiconify()
        self.main_app.windows['win3'].withdraw()
        self.root.unbind("<Map>")

    def show_reset_confirm(self):
        """点击复原按钮的处理"""
        self.root.configure(bg='white')
        confirm_win = tk.Toplevel(self.root, bg='white')
        confirm_win.title("VD_Toggler配置工具")

        icon_path = 'img/els/cfg.png'
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_img)
            confirm_win.tk.call('wm', 'iconphoto', confirm_win._w, icon_photo)

        # 设置窗口位置和大小
        window_width = 520
        window_height = 220
        screen_width = confirm_win.winfo_screenwidth()
        screen_height = confirm_win.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        confirm_win.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 计算基础字体大小
        self.warn_font_size = -18
        self.text_font_size = -16

        # 创建字体对象
        font_family = ["Microsoft YaHei", "sans-serif"]
        self.warn_font = (font_family[0], self.warn_font_size, 'bold')
        self.text_font = (font_family[0], self.text_font_size)

        # 添加内容
        label_1 = tk.Label(confirm_win, text="是否要恢复到默认设置？", font=self.warn_font, padx=20, pady=30, bg='white')
        label_1.pack()

        label_2 = tk.Label(confirm_win, text="此操作将清除您所有的自定义设置，且不可恢复。", font=self.text_font, padx=20, pady=0, bg='white')
        label_2.pack()

        bottom_frame = tk.Frame(confirm_win, bg='white')
        bottom_frame.pack(side='bottom', fill='x', pady=(0, 5))

        separator = tk.Frame(bottom_frame, height=2, bd=1, relief='sunken', bg='white')
        separator.pack(fill='x', pady=5)

        button_frame = tk.Frame(bottom_frame, bg='white')
        button_frame.pack(pady=10)

        # 确定按钮
        ok_btn = tk.Button(button_frame, text="确定", width=10, command=lambda: self.reset_to_default(confirm_win), bg='white')
        ok_btn.pack(side="left", padx=20)

        # 取消按钮
        cancel_btn = tk.Button(button_frame, text="取消", width=10, command=confirm_win.destroy, bg='white')
        cancel_btn.pack(side="right", padx=20)

    def reset_to_default(self, confirm_win):
        """恢复默认设置"""
        try:
            default_path = get_path(r'else\data.csv')
            target_path = r'data\data.csv'
            if os.path.exists(default_path):
                shutil.copy2(default_path, target_path)
            os.remove(self.backup_file)
            self.main_app.root.quit()
        except Exception as e:
            print(f"恢复默认设置失败: {str(e)}")
        finally:
            confirm_win.destroy()

class VirtualDesktopToggler:
    """设置按钮控件"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(1)
        self.windows = {}
        self.win_sizes = {}
        self.dragging = None
        self.orig_pos = {}

        with open(r'data\data.csv', 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            parts = first_line.split(',')
            self.mode = int(parts[0]) if parts else 1
            self.sub_mode = int(parts[1]) if len(parts) > 1 else 0

        self.setup_ui()
        self.config_tool = ConfigTool(backup_file, self)
        self.config = self.load_config_cache()  # 缓存配置

    def load_scaled_image(self, path, target_size):
        """加载并缩放图片填充按钮"""
        img_pil = Image.open(path).convert("RGBA")
        canvas = Image.new("RGBA", target_size, (0,0,0,0))

        img_ratio = img_pil.width / img_pil.height
        target_ratio = target_size[0] / target_size[1]

        if img_ratio > target_ratio:
            scaled_w = target_size[0]
            scaled_h = int(target_size[0] / img_ratio)
        else:
            scaled_h = target_size[1]
            scaled_w = int(target_size[1] * img_ratio)

        scaled_img = img_pil.resize((scaled_w, scaled_h), Image.LANCZOS)
        x = (target_size[0] - scaled_w) // 2
        y = (target_size[1] - scaled_h) // 2
        canvas.paste(scaled_img, (x, y), scaled_img)
        return ImageTk.PhotoImage(canvas)

    def setup_ui(self):
        scale_factor = float(open(r'data\data.csv').readlines()[14].split(',')[0])

        # 尺寸计算
        base_size = int(SCREEN_HEIGHT / 12 * scale_factor)
        win3_size = (base_size, base_size) if self.sub_mode == 1 else (
        int(SCREEN_HEIGHT/24 * scale_factor), 
        int(SCREEN_HEIGHT/12 * scale_factor)
        )
        control_size = (
        int(SCREEN_WIDTH/9 * scale_factor), 
        int(SCREEN_HEIGHT/20 * scale_factor)
        )

        # 创建窗口
        for i in range(1,10):
            win = tk.Toplevel()
            win.overrideredirect(1)
            win.wm_attributes('-topmost', 1)
            win.wm_attributes('-transparentcolor', 'white')
            win.configure(bg='white')
            self.windows[f'win{i}'] = win

        # 窗口位置和尺寸设置
        pos_settings = [
            (1, base_size, base_size, SCREEN_WIDTH*WIN_POSITIONS['win1_x'], SCREEN_HEIGHT*(1-WIN_HEIGHT_1)),
            (2, base_size, base_size, SCREEN_WIDTH*WIN_POSITIONS['win2_x'], SCREEN_HEIGHT*(1-WIN_HEIGHT_1)),
            (3, *win3_size, 
                SCREEN_WIDTH*WIN_POSITIONS['win3_x'] if int(open(r'data\data.csv').readline().split(',')[1]) == 1 
                else (0 if self.mode == 2 else SCREEN_WIDTH - win3_size[0]), 
                SCREEN_HEIGHT*(1-WIN_HEIGHT_1)),
            (4, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['h_y']),
            (5, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['c_y']),
            (6, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['a_y']),
            (7, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['x_y']),
            (8, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['w_y']),
            (9, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['s_y']),    
        ]

        for num, w, h, x, y in pos_settings:
            win = self.windows[f'win{num}']
            win.name = f'win{num}'
            win.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
            self.win_sizes[f'win{num}'] = (w, h)

        self.update_appearance()
        self.bind_events()
        self.root.withdraw()

    def update_appearance(self):

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 15:
                parts = lines[14].strip().split(',')
                alpha1 = float(parts[2]) if len(parts) > 2 else 0.3
            else:
                alpha1 = 0.3

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 15:
                parts = lines[14].strip().split(',')
                alpha2 = float(parts[3]) if len(parts) > 2 else 0.8
            else:
                alpha2 = 0.8

        alpha_config = {
            1: ('L1', alpha1),
            2: ('R1', alpha1),
            3: ('B2', alpha1) if self.mode == 2 else ('B1', 0.3),
            4: ('H', alpha2),
            5: ('C', alpha2),
            6: ('A', alpha2),
            7: ('X', alpha2),
            8: ('W', alpha2),
            9: ('S', alpha2),
        }

        for num in range(1,10):
            win = self.windows[f'win{num}']
            img_file, alpha = alpha_config[num]
            img_path = f'img/cfg/{img_file}.png'
            self.orig_pos[f'win{num}'] = (win.winfo_x(), win.winfo_y())

            w, h = self.win_sizes[f'win{num}']
            img = self.load_scaled_image(img_path, (w, h))

            for child in win.winfo_children():
                child.destroy()

            label = tk.Label(win, image=img, bg='white')
            label.pack(fill="both", expand=True)
            label.image = img

            win.wm_attributes('-alpha', alpha) 
            self.orig_pos[f'win{num}'] = (win.winfo_x(), win.winfo_y())

            self.windows['win3'].withdraw()

    def reload_windows(self):
        """重新加载所有窗口"""
        # 刷新配置缓存
        self.reload_config_cache()
        config = self.config
        scale_factor = config['scale_factor']

        # 计算新尺寸
        base_size = int(SCREEN_HEIGHT / 12 * scale_factor)
        sub_mode = config['sub_mode']
        win3_size = (base_size, base_size) if sub_mode == 1 else (
            int(SCREEN_HEIGHT/24 * scale_factor), 
            int(SCREEN_HEIGHT/12 * scale_factor)
        )
        control_size = (
            int(SCREEN_WIDTH/9 * scale_factor), 
            int(SCREEN_HEIGHT/20 * scale_factor)
        )

        # 计算新位置
        pos = config['win_positions']
        win3_x = SCREEN_WIDTH * pos['win3_x'] if sub_mode == 1 else (0 if config['mode'] == 2 else SCREEN_WIDTH - win3_size[0])
        win3_y = SCREEN_HEIGHT * (1 - config['win_height_1'])

        # 位置尺寸配置列表
        new_settings = [
            (1, base_size, base_size, SCREEN_WIDTH*pos['win1_x'], SCREEN_HEIGHT*(1 - config['win_height_1'])),
            (2, base_size, base_size, SCREEN_WIDTH*pos['win2_x'], SCREEN_HEIGHT*(1 - config['win_height_1'])),
            (3, *win3_size, win3_x, win3_y),
            (4, *control_size, SCREEN_WIDTH*pos['col_x'], SCREEN_HEIGHT*pos['h_y']),
            (5, *control_size, SCREEN_WIDTH*pos['col_x'], SCREEN_HEIGHT*pos['c_y']),
            (6, *control_size, SCREEN_WIDTH*pos['col_x'], SCREEN_HEIGHT*pos['a_y']),
            (7, *control_size, SCREEN_WIDTH*pos['col_x'], SCREEN_HEIGHT*pos['x_y']),
            (8, *control_size, SCREEN_WIDTH*pos['col_x'], SCREEN_HEIGHT*pos['w_y']),
            (9, *control_size, SCREEN_WIDTH*pos['col_x'], SCREEN_HEIGHT*pos['s_y']),
        ]

        # 复用窗口
        for num, w, h, x, y in new_settings:
            win_name = f'win{num}'
            win = self.windows.get(win_name)
            if not win:
                # 仅在窗口不存在时创建
                win = tk.Toplevel()
                win.overrideredirect(1)
                win.wm_attributes('-topmost', 1)
                win.wm_attributes('-transparentcolor', 'white')
                win.configure(bg='white')
                self.windows[win_name] = win
            # 更新窗口属性
            win.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
            self.win_sizes[win_name] = (w, h)

        # 更新外观
        self.update_appearance()

    def load_config_cache(self):
        """一次性加载配置到内存"""
        config = {}
        with open(r'data\data.csv', 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]

        # 解析模式配置
        first_line = lines[0] if lines else '1,'
        parts = first_line.split(',')
        config['mode'] = int(parts[0]) if parts else 1
        config['sub_mode'] = int(parts[1]) if len(parts) > 1 else 0

        # 解析缩放因子和透明度
        if len(lines) >= 15:
            scale_parts = lines[14].split(',')
            config['scale_factor'] = float(scale_parts[0]) if scale_parts else 1.0
            config['speed'] = float(scale_parts[1]) if len(scale_parts) > 1 else 1.0
            config['alpha1'] = float(scale_parts[2]) if len(scale_parts) > 2 else 0.3
            config['alpha2'] = float(scale_parts[3]) if len(scale_parts) > 3 else 0.8

        # 解析窗口位置
        pos_config = load_config()
        config['win_positions'] = pos_config['WIN_POSITIONS']
        config['win_height_1'] = pos_config['WIN_HEIGHT_1']

        return config

    def reload_config_cache(self):
        """配置变更时刷新缓存"""
        self.config = self.load_config_cache()

    def set_windows_visibility(self, visible):
        """设置所有窗口的可见性"""
        for win in self.windows.values():
            if visible:
                win.deiconify()
            else:
                win.withdraw()

    def bind_events(self):
        """拖拽事件"""
        for win in self.windows.values():
            win.bind('<Button-1>', self.on_drag_start)
            win.bind('<B1-Motion>', self.on_drag_motion)
            win.bind('<ButtonRelease-1>', self.on_drag_end)

    def on_drag_start(self, event):
        """拖动开始的处理"""
        widget = event.widget.master 
        self.dragging = widget
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.orig_pos = (widget.winfo_x(), widget.winfo_y())

    def on_drag_motion(self, event):
        """拖动过程的处理"""
        if not self.dragging:
            return
        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y
        new_x = self.orig_pos[0] + delta_x
        new_y = self.orig_pos[1] + delta_y

        # 更新被拖动窗口的位置
        self.dragging.geometry(f"+{new_x}+{new_y}")

        win_name = self.dragging.name

        # 同步处理win1-3垂直坐标
        if win_name in ['win1', 'win2', 'win3']:
            current_y = new_y 

            for n in ['1', '2', '3']:
                other_win_name = f'win{n}'
                if other_win_name != win_name:
                    other_win = self.windows.get(other_win_name)
                    if other_win:
                        current_x = other_win.winfo_x()
                        other_win.geometry(f"+{current_x}+{current_y}")

        # 同步处理win4-9横向坐标
        elif win_name in ['win4', 'win5', 'win6', 'win7', 'win8', 'win9']:
            current_x = new_x

            control_wins = [f'win{i}' for i in range(4, 10)]
            for other_win_name in control_wins:
                if other_win_name != win_name:
                    other_win = self.windows.get(other_win_name)
                    if other_win:
                        current_y = other_win.winfo_y()
                        other_win.geometry(f"+{int(current_x)}+{int(current_y)}")

    def on_drag_end(self, event):
        """拖动结束的处理"""
        if self.dragging:
            self.save_positions()
        self.dragging = None

    def save_positions(self):
        """保存窗口位置到配置文件"""
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()

        mode_line = lines[0].strip().split(',')
        current_mode = int(mode_line[0])

        # 计算相对位置
        positions = {
            'WIN_HEIGHT_1': 1 - (self.windows['win1'].winfo_y() / SCREEN_HEIGHT),
            'win1_x': self.windows['win1'].winfo_x() / SCREEN_WIDTH,
            'win2_x': self.windows['win2'].winfo_x() / SCREEN_WIDTH,
            'win3_x': self.windows['win3'].winfo_x() / SCREEN_WIDTH,
            'col_x': self.windows['win4'].winfo_x() / SCREEN_WIDTH,
            'h_y': self.windows['win4'].winfo_y() / SCREEN_HEIGHT,
            'c_y': self.windows['win5'].winfo_y() / SCREEN_HEIGHT,
            'a_y': self.windows['win6'].winfo_y() / SCREEN_HEIGHT,
            'x_y': self.windows['win7'].winfo_y() / SCREEN_HEIGHT,
            'w_y': self.windows['win8'].winfo_y() / SCREEN_HEIGHT,
            's_y': self.windows['win9'].winfo_y() / SCREEN_HEIGHT,
        }

        # 更新配置行
        config_lines = [
            positions['WIN_HEIGHT_1'],
            positions['win1_x'],
            positions['win2_x'],
            positions['win3_x'],
            positions['col_x'],
            positions['h_y'],
            positions['c_y'],
            positions['a_y'],
            positions['x_y'],
            positions['w_y'],
            positions['s_y'],
        ]

        # 更新当前模式对应的值
        for i, value in enumerate(config_lines):
            idx = i + 1  # 第1行是WIN_HEIGHT_1，第2行是win1_x，以此类推
            if idx < len(lines):
                parts = lines[idx].strip().split(',')
                if len(parts) < 2:
                    parts = ['0', '0']

                parts[current_mode] = str(value)
                lines[idx] = ','.join(parts) + '\n'

        with open(r'data\data.csv', 'w') as f:
            f.writelines(lines)

if __name__ == '__main__':
    app = VirtualDesktopToggler()
    app.root.mainloop()
