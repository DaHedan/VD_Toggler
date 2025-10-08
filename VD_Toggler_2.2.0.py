import tkinter as tk
from pyvda import get_virtual_desktops, VirtualDesktop
import os
import pyautogui
import tempfile
import ctypes
from ctypes import cast, POINTER
from ctypes import *
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from PIL import Image, ImageTk
import subprocess

# nuitka打包关闭启动画面
if "NUITKA_ONEFILE_PARENT" in os.environ:
   splash_filename = os.path.join(
      tempfile.gettempdir(),
      "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
   )
   if os.path.exists(splash_filename):
      os.unlink(splash_filename)

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
            scale_factor = float(all_lines[14].split(',')[0])

    return {
        'WIN_HEIGHT_1': float(lines[0]),
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
            'win3_y': float(lines[11])
        }
    }

# 读取配置
config = load_config()
WIN_HEIGHT_1 = config['WIN_HEIGHT_1']
WIN_POSITIONS = config['WIN_POSITIONS']

class VirtualDesktopToggler:
    """设置按钮控件"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(1)
        self.windows = {}
        self.win_sizes = {}
        self.dragging = None
        self.orig_pos = {}
        self.mode = int(open(r'data\data.csv', 'r', encoding='utf-8').readline().strip().split(',')[0])
        self.sub_mode = int(open(r'data\data.csv', 'r', encoding='utf-8').readline().strip().split(',')[1])
        self.setup_ui()

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
                SCREEN_WIDTH*WIN_POSITIONS['win3_x'] if self.sub_mode == 1 
                else (0 if self.mode == 2 else SCREEN_WIDTH - win3_size[0]), 
                SCREEN_HEIGHT*(1-WIN_HEIGHT_1) if self.sub_mode == 0 else SCREEN_HEIGHT*WIN_POSITIONS['win3_y']),
            (4, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['h_y']),
            (5, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['c_y']),
            (6, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['a_y']),
            (7, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['x_y']),
            (8, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['w_y']),
            (9, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['s_y']),
        ]

        for num, w, h, x, y in pos_settings:
            win = self.windows[f'win{num}']
            win.minsize(int(w), int(h))
            win.maxsize(int(w), int(h))
            win.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
            self.win_sizes[f'win{num}'] = (w, h)

        self.update_appearance()
        self.bind_events()
        self.root.withdraw()

    def update_appearance(self):
        """设置按钮的显示方案"""
        desktops = get_virtual_desktops()
        desktop_count = len(desktops)
        current_desktop = VirtualDesktop.current()

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            parts = lines[14].strip().split(',')
            alpha1 = float(parts[2])
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            parts = lines[14].strip().split(',')
            alpha2 = float(parts[3])

        alpha_config = {
            1: ('L1', alpha1),
            2: ('R1', alpha1) if current_desktop.number != desktop_count else ('RA', 0.3),
            3: (('B2', alpha1) if self.mode == 2 else ('B1', alpha1)) if self.sub_mode == 0 else ('B3', alpha1),
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
            img_path = f'img/vdt/{img_file}.png'

            w, h = self.win_sizes[f'win{num}']
            img = self.load_scaled_image(img_path, (w, h))

            for child in win.winfo_children():
                child.destroy()

            label = tk.Label(win, image=img, bg='white')
            label.pack(fill="both", expand=True)
            label.image = img

            win.wm_attributes('-alpha', alpha) 
            self.orig_pos[f'win{num}'] = (win.winfo_x(), win.winfo_y())

        for w in ['win3','win4','win5','win6','win7','win8','win9']:
            self.windows[w].withdraw()
            self.check_main(None)

    def bind_events(self):
        """按钮事件绑定"""
        for num in [1, 2]:
            self.windows[f'win{num}'].bind('<Button-1>', lambda e,n=num: self.on_press(n))
            self.windows[f'win{num}'].bind('<ButtonRelease-1>', lambda e,n=num: self.on_release(n))
            self.windows[f'win{num}'].bind('<Button-3>', self.show_controls)

        self.windows['win3'].bind('<Button-1>', self.restore_main)
        self.windows['win3'].bind('<Button-3>', lambda e: self.on_drag_start(e)) if self.sub_mode == 1 else None
        self.windows['win3'].bind('<B3-Motion>', lambda e: self.on_drag_motion(e)) if self.sub_mode == 1 else None
        self.windows['win3'].bind('<ButtonRelease-3>', lambda e: self.on_drag_end(e)) if self.sub_mode == 1 else None
        self.windows['win4'].bind('<Button-1>', lambda e: self.hide_controls(animate=True))
        self.windows['win5'].bind('<Button-1>', lambda e: os._exit(0))
        self.windows['win6'].bind('<Button-1>', self.create_desktop)
        self.windows['win7'].bind('<Button-1>', self.close_desktop)
        self.windows['win8'].bind('<Button-1>', self.show_all)
        self.windows['win9'].bind('<Button-1>',self.launch_config_tool)

    def on_press(self, num):
        """主按钮点击事件"""
        hwnd = user32.GetForegroundWindow()

        if self.windows['win4'].winfo_viewable():
            self.hide_controls()
            return

        shortcuts = self.read_shortcuts()
        key_map = {
            "Ctrl": "ctrl", "Alt": "alt", "Shift": "shift", "Win": "win",
            "Enter": "enter", "Space": "space", "Backspace": "backspace",
            "Tab": "tab", "Esc": "esc", "Left": "left", "Right": "right", "Up": "up", "Down": "down",
        }
        py_keys = [key_map.get(key, key.lower()) for key in shortcuts]

        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            line13 = lines[13].strip().split(',')
            if line13[0] == '1':
                if line13[1] == '1':
                    win = self.windows[f'win{num}']
                    win.wm_attributes('-alpha', 0.5)
                    if py_keys:
                        user32.ShowWindow(hwnd, 6)
                        pyautogui.hotkey(*py_keys, presses=1, interval=0.05)
                        user32.ShowWindow(hwnd, 9)
                    self.go_left(None) if num==1 else self.go_right(None)
                    for w in ['win1','win2']:
                        self.windows[w].withdraw()
                    self.windows['win3'].deiconify()
                    return
                else:
                    win = self.windows[f'win{num}']
                    win.wm_attributes('-alpha', 0.5)
                    if py_keys:
                        user32.ShowWindow(hwnd, 6)
                        pyautogui.hotkey(*py_keys, presses=1, interval=0.05)
                        user32.ShowWindow(hwnd, 9)
                    self.go_left(None) if num==1 else self.go_right(None)
                    self.root.destroy()
                    return

        win = self.windows[f'win{num}']
        win.wm_attributes('-alpha', 0.5)
        if py_keys:
            user32.ShowWindow(hwnd, 6)
            pyautogui.hotkey(*py_keys, presses=1, interval=0.05)
            user32.ShowWindow(hwnd, 9)
        self.go_left(None) if num==1 else self.go_right(None)
        self.update_appearance()
        self.check_main(None)
        self.lock_screen(None) if self.judge_lock_screen(None) == 1 else None

    def go_left(self, num):
        """win1事件"""
        pyautogui.hotkey('ctrl', 'win', 'left')
        if self.judge_close_audio(None) == 1:
            self.close_audio(None)

    def go_right(self, num):
        """win2事件"""
        desktops = get_virtual_desktops()
        desktop_count = len(desktops)
        current_desktop = VirtualDesktop.current()
        if current_desktop.number == desktop_count:
            self.create_desktop(None)
        else:
            pyautogui.hotkey('ctrl', 'win', 'right')
        if self.judge_close_audio(None) == 1:
            self.close_audio(None)

    def on_release(self, num):
        """主按钮释放事件"""
        win = self.windows[f'win{num}']
        win.wm_attributes('-alpha', 0.3)

    def show_controls(self, event):
        """主按钮右击事件"""
        for w in ['win4','win5','win6','win7','win8','win9']:
            self.windows[w].deiconify()

    def judge_lock_screen(self, num):
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            return int(lines[13].split(',')[2])

    def lock_screen(self, num):
        HWND_BROADCAST = 0xffff
        WM_SYSCOMMAND = 0x0112
        SC_MONITORPOWER = 0xF170
        MonitorPowerOff = 2
        SW_SHOW = 5

        windll.user32.PostMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MonitorPowerOff)
        shell32 = windll.LoadLibrary("shell32.dll")
        shell32.ShellExecuteW(None,'open', 'rundll32.exe', 'USER32,LockWorkStation','',SW_SHOW)

    def close_audio(self, num):
        """静音操作"""
        if self.is_system_muted(None) == 0:
            VK_VOLUME_MUTE = 0xAD  # 静音键虚拟键码
            ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)  # 按下静音键
            ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)  # 释放静音键

    def is_system_muted(self, num):
        devices = AudioUtilities.GetSpeakers()  # 获取默认音频设备
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)  # 激活音量控制接口
        volume = cast(interface, POINTER(IAudioEndpointVolume))  # 获取音量控制对象
        return volume.GetMute()  # 获取并返回静音状态

    def judge_close_audio(self, num):
        """读取设置静音操作的数据"""
        with open(r'data\data.csv', 'r') as f:
            lines = f.readlines()
            return int(lines[15].split(',')[0])

    def read_shortcuts(self):
        """读取快捷键配置"""
        with open(r'data\data.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        shortcut_line = lines[16].strip()
        shortcuts = shortcut_line.split(',') if shortcut_line else []

        # 过滤无效按键
        valid_keys = [
            key for key in shortcuts 
            if key in [
                "Ctrl", "Alt", "Shift", "Win",
                "Enter", "Space", "Backspace", "Tab", "Esc", "Left", "Right", "Up", "Down",
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            ]
        ]
        return valid_keys

    def hide_controls(self, event=None, animate=False):
        """win4事件"""
        for w in ['win4','win5','win6','win7','win8','win9']:
            self.windows[w].withdraw()
        if animate:
            self.animate_move_out()

    def close_desktop(self, event):
        """win7事件"""
        pyautogui.hotkey('ctrl', 'win', 'f4')
        self.hide_controls(animate=False)
        self.check_main(None)
        self.update_appearance()

    def create_desktop(self, event):
        """win6事件"""
        pyautogui.hotkey('ctrl', 'win', 'd')
        self.hide_controls(animate=False)
        self.check_main(None)
        self.update_appearance()

    def show_all(self, event):
        """win8事件"""
        pyautogui.hotkey('win', 'tab')
        self.hide_controls(animate=False)

        win = self.windows['win2']
        alpha = 0.3
        img_path = f'img/vdt/R1.png'

        w, h = self.win_sizes['win2']
        img = self.load_scaled_image(img_path, (w, h))

        for child in win.winfo_children():
            child.destroy()

        label = tk.Label(win, image=img, bg='white')
        label.pack(fill="both", expand=True)
        label.image = img

        win.wm_attributes('-alpha', alpha) 
        self.orig_pos['win2'] = (win.winfo_x(), win.winfo_y())

        base_size = int(SCREEN_HEIGHT / 12)
        y_position = int(SCREEN_HEIGHT * (1 - WIN_HEIGHT_1))

        # 更新窗口1、2的几何属性
        self.windows['win1'].geometry(f"{base_size}x{base_size}+{int(SCREEN_WIDTH * WIN_POSITIONS['win1_x'])}+{y_position}")
        self.windows['win1'].deiconify()
        self.windows['win2'].geometry(f"{base_size}x{base_size}+{int(SCREEN_WIDTH * WIN_POSITIONS['win2_x'])}+{y_position}")
        self.windows['win2'].deiconify()

    def launch_config_tool(self, event):
        """win9事件"""
        for w in self.windows.values():
            w.withdraw()
        self.root.withdraw()

        # 启动配置工具并监控进程
        try:
            process = subprocess.Popen("VDT_cfg.exe")
        except:
            process = subprocess.Popen(["python", "VDT_cfg2.2.0.py"])

        def check_process():
            if process.poll() is None:
                self.root.after(500, check_process)
            else:
                # 重新加载配置文件
                global config, WIN_HEIGHT_1, WIN_POSITIONS
                config = load_config()
                WIN_HEIGHT_1 = config['WIN_HEIGHT_1']
                WIN_POSITIONS = config['WIN_POSITIONS']

                # 更新模式状态
                self.mode = int(open(r'data\data.csv', 'r', encoding='utf-8').readline().strip().split(',')[0]) if os.path.exists(r'data\data.csv') else 1
                self.sub_mode = int(open(r'data\data.csv', 'r', encoding='utf-8').readline().strip().split(',')[1]) if os.path.exists(r'data\data.csv') else 0

                # 重新设置UI
                self.setup_ui()
                self.update_appearance()

                # 恢复主窗口
                self.restore_main(None)

        self.root.after(500, check_process)

    def animate_move_out(self):
        """主按钮隐藏"""
        def move_step():
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()
                multiplier = float(lines[14].split(',')[1]) if len(lines) >=15 else 0.1

            win1_x = self.windows['win1'].winfo_x()
            win2_x = self.windows['win2'].winfo_x()

            current_desktop = VirtualDesktop.current()
            if (hasattr(self, 'mode') and self.mode == 2 and ((win1_x > -100 or win2_x > -100) if current_desktop.number != 1 else win2_x > -100)) or \
               (not hasattr(self, 'mode') or self.mode == 1 and ((win1_x < SCREEN_WIDTH or win2_x < SCREEN_WIDTH) if current_desktop.number != 1 else win2_x < SCREEN_WIDTH)):
                base_delta = -50 if hasattr(self, 'mode') and self.mode == 2 else 50
                delta = int(base_delta * multiplier)
                new_x1 = win1_x + delta
                new_x2 = win2_x + delta
                self.windows['win1'].geometry(f"+{new_x1}+{self.windows['win1'].winfo_y()}")
                self.windows['win2'].geometry(f"+{new_x2}+{self.windows['win2'].winfo_y()}")
                self.root.after(10, move_step)

            else:
                self.windows['win1'].withdraw()
                self.windows['win2'].withdraw()
                self.windows['win3'].deiconify()
        move_step()

    def restore_main(self, event):
        """win3/win9执行后事件"""
        for w in ['win3','win4','win5','win6','win7','win8','win9']:
            self.windows[w].withdraw()

        base_size = int(SCREEN_HEIGHT / 12)
        y_position = int(SCREEN_HEIGHT * (1 - WIN_HEIGHT_1))

        self.update_appearance()
        current_desktop = VirtualDesktop.current()
        if current_desktop.number != 1:
            self.windows['win1'].geometry(f"{base_size}x{base_size}+{int(SCREEN_WIDTH * WIN_POSITIONS['win1_x'])}+{y_position}")
            self.windows['win1'].deiconify()

        self.windows['win2'].geometry(f"{base_size}x{base_size}+{int(SCREEN_WIDTH * WIN_POSITIONS['win2_x'])}+{y_position}")
        self.windows['win2'].deiconify()

        self.check_main(None)

    def on_drag_start(self, event):
        """win3拖动开始的处理"""
        widget = event.widget.master 
        self.dragging = widget
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.drag_orig_pos = (widget.winfo_x(), widget.winfo_y())

    def on_drag_motion(self, event):
        """win3拖动过程的处理"""
        if not self.dragging:
            return
        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y
        new_x = self.drag_orig_pos[0] + delta_x
        new_y = self.drag_orig_pos[1] + delta_y

        # 更新被拖动窗口的位置
        self.dragging.geometry(f"+{new_x}+{new_y}")

    def on_drag_end(self, event):
        """win3拖动结束的处理"""
        if self.dragging and self.sub_mode == 1:
            with open(r'data\data.csv', 'r', encoding='utf-8') as f:
                lines = f.readlines()

            mode_line = lines[0].strip().split(',') if len(lines) > 0 else ['1', '1']
            current_mode = int(mode_line[0]) if len(mode_line) > 0 else 1
            col_idx = 1 if current_mode == 1 else 2

            win3_x_rel = round(self.windows['win3'].winfo_x() / SCREEN_WIDTH, 4)
            win3_y_rel = round(self.windows['win3'].winfo_y() / SCREEN_HEIGHT, 4)

            win3_x_parts = lines[4].strip().split(',')
            win3_x_parts[col_idx] = str(win3_x_rel)
            lines[4] = ','.join(win3_x_parts) + '\n'

            win3_y_parts = lines[12].strip().split(',')
            win3_y_parts[col_idx] = str(win3_y_rel)
            lines[12] = ','.join(win3_y_parts) + '\n'

            with open(r'data\data.csv', 'w', encoding='utf-8') as f:
                f.writelines(lines)

            self.dragging = None

    def check_main(self, event):
        for w in ['win1','win2']:
            self.windows[w].withdraw()

        base_size = int(SCREEN_HEIGHT / 12)
        y_position = int(SCREEN_HEIGHT * (1 - WIN_HEIGHT_1))

        current_desktop = VirtualDesktop.current()
        if current_desktop.number != 1:
            self.windows['win1'].geometry(f"{base_size}x{base_size}+{int(SCREEN_WIDTH * WIN_POSITIONS['win1_x'])}+{y_position}")
            self.windows['win1'].deiconify()

        self.windows['win2'].geometry(f"{base_size}x{base_size}+{int(SCREEN_WIDTH * WIN_POSITIONS['win2_x'])}+{y_position}")
        self.windows['win2'].deiconify()

if __name__ == '__main__':
    app = VirtualDesktopToggler()
    app.root.mainloop()
