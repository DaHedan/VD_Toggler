import tkinter as tk
import os
import pyautogui
import ctypes
from PIL import Image, ImageTk
import subprocess

# pyinstaller打包关闭启动画面
try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

# 基础设置
user32 = ctypes.windll.user32
SCREEN_WIDTH = user32.GetSystemMetrics(0)
SCREEN_HEIGHT = user32.GetSystemMetrics(1)

def load_config():
    """基础高度比例和预设坐标"""
    try:
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
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        raise RuntimeError("配置文件加载失败，请检查data/data.csv文件格式") from e

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
        self.mode = int(open(r'data\data.csv', 'r', encoding='utf-8').readline().strip().split(',')[0]) if os.path.exists(r'data\data.csv') else 1
        self.sub_mode = int(open(r'data\data.csv', 'r', encoding='utf-8').readline().strip().split(',')[1]) if os.path.exists(r'data\data.csv') else 0
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
        for i in range(1,11):
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
            (10, *control_size, SCREEN_WIDTH*WIN_POSITIONS['col_x'], SCREEN_HEIGHT*WIN_POSITIONS['y_y'])
        ]

        for num, w, h, x, y in pos_settings:
            win = self.windows[f'win{num}']
            win.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
            self.win_sizes[f'win{num}'] = (w, h)

        self.update_appearance()
        self.bind_events()
        self.root.withdraw()

    def update_appearance(self):
        """设置按钮的显示方案"""
        alpha_config = {
            1: ('L1', 0.3),
            2: ('R1', 0.3),
            3: ('B3', 0.3) if self.sub_mode == 1 else ('B2', 0.3) if self.mode == 2 else ('B1', 0.3),
            4: ('H', 0.8),
            5: ('C', 0.8),
            6: ('A', 0.8),
            7: ('X', 0.8),
            8: ('W', 0.8),
            9: ('S', 0.8),
            10: (('YC',0.8) if self.get_csv_state() == 0 else ('YO', 0.9))
        }

        for num in range(1,11):
            win = self.windows[f'win{num}']
            img_file, alpha = alpha_config[num]
            img_path = f'img/vdt/{img_file}.png'

            try:
                w, h = self.win_sizes[f'win{num}']
                img = self.load_scaled_image(img_path, (w, h))
            except Exception as e:
                print(f"Error loading {img_path}: {str(e)}")
                continue

            for child in win.winfo_children():
                child.destroy()

            label = tk.Label(win, image=img, bg='white')
            label.pack(fill="both", expand=True)
            label.image = img

            win.wm_attributes('-alpha', alpha) 
            self.orig_pos[f'win{num}'] = (win.winfo_x(), win.winfo_y())

        # 隐藏控件
        for w in ['win3','win4','win5','win6','win7','win8','win9','win10']:
            self.windows[w].withdraw()

    def bind_events(self):
        """按钮事件绑定"""
        for num in [1, 2]:
            # 主按钮事件绑定
            self.windows[f'win{num}'].bind('<Button-1>', lambda e,n=num: self.on_press(n))
            self.windows[f'win{num}'].bind('<ButtonRelease-1>', lambda e,n=num: self.on_release(n))
            self.windows[f'win{num}'].bind('<Button-3>', self.show_controls)

        # 添加win3-10的事件绑定
        self.windows['win3'].bind('<Button-1>', self.restore_main)
        self.windows['win4'].bind('<Button-1>', lambda e: self.hide_controls(animate=True))
        self.windows['win5'].bind('<Button-1>', lambda e: os._exit(0))
        self.windows['win6'].bind('<Button-1>', self.create_desktop)
        self.windows['win7'].bind('<Button-1>', self.close_desktop)
        self.windows['win8'].bind('<Button-1>', self.show_all)
        self.windows['win9'].bind('<Button-1>',self.launch_config_tool)
        self.windows['win10'].bind('<Button-1>',self.toggle_win10_state)

    def on_press(self, num):
        """主按钮点击事件"""
        if self.windows['win4'].winfo_viewable():
            self.hide_controls()
            return
        try:
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()
                if len(lines) >= 14:
                    line13 = lines[13].strip().split(',')
                    if line13[0] == '1':
                        if line13[1] == '1':
                            win = self.windows[f'win{num}']
                            win.wm_attributes('-alpha', 0.5)
                            pyautogui.hotkey('ctrl', 'win', 'left' if num==1 else 'right')
                            self.animate_move_out()
                            return
                        else:
                            win = self.windows[f'win{num}']
                            win.wm_attributes('-alpha', 0.5)
                            pyautogui.hotkey('ctrl', 'win', 'left' if num==1 else 'right')
                            self.root.destroy()
                            return
        except Exception as e:
            print(f"读取配置文件异常: {str(e)}")

        win = self.windows[f'win{num}']
        win.wm_attributes('-alpha', 0.5)

        pyautogui.hotkey('ctrl', 'win', 'left' if num==1 else 'right')

    def on_release(self, num):
        """主按钮释放事件"""
        win = self.windows[f'win{num}']
        win.wm_attributes('-alpha', 0.3)

    def create_desktop(self, event):
        """win6事件"""
        pyautogui.hotkey('ctrl', 'win', 'd')
        self.hide_controls(animate=False)

    def close_desktop(self, event):
        """win7事件"""
        pyautogui.hotkey('ctrl', 'win', 'f4')
        self.hide_controls(animate=False)

    def show_all(self, event):
        """win8事件"""
        pyautogui.hotkey('win', 'tab')
        self.hide_controls(animate=False)

    def show_controls(self, event):
        """主按钮右击事件"""
        for w in ['win4','win5','win6','win7','win8','win9','win10']:
            self.windows[w].deiconify()
            self.windows[w].deiconify()

    def hide_controls(self, event=None, animate=False):
        """win4事件"""
        for w in ['win4','win5','win6','win7','win8','win9','win10']:
            self.windows[w].withdraw()
        if animate:
            self.animate_move_out()

    def get_csv_state(self):
        """win10图片决策"""
        try:
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()
                if len(lines) >= 14:
                    return int(lines[13].split(',')[0])
        except:
            return 0

    def toggle_win10_state(self, event):
        """win10事件"""
        try:
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()

            if len(lines) >= 14:
                parts = lines[13].strip().split(',')
                parts[0] = '1' if parts[0] == '0' else '0'
                lines[13] = ','.join(parts) + '\n'

                with open(r'data\data.csv', 'w') as f:
                    f.writelines(lines)

                self.update_appearance()
        except Exception as e:
            print(f"切换状态失败: {str(e)}")

    def launch_config_tool(self, event):
        """win9事件"""
        try:
            # 隐藏所有窗口
            for w in self.windows.values():
                w.withdraw()
            self.root.withdraw()

            # 启动配置工具并监控进程
            process = subprocess.Popen("VDT_cfg.exe")

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

        except Exception as e:
            print(f"配置工具异常: {str(e)}")
            self.restore_main(None)

    def animate_move_out(self):
        """主按钮隐藏"""
        def move_step():
            try:
                with open(r'data\data.csv', 'r') as f:
                    lines = f.readlines()
                    multiplier = float(lines[14].split(',')[1]) if len(lines) >=15 else 0.1
            except Exception as e:
                print(f"读取配置文件失败: {str(e)}，使用默认值0.1")
                multiplier = 0.1

            win1_x = self.windows['win1'].winfo_x()
            win2_x = self.windows['win2'].winfo_x()

            # 判断是否完全移出屏幕
            if (hasattr(self, 'mode') and self.mode == 2 and (win1_x > -100 or win2_x > -100)) or \
               (not hasattr(self, 'mode') or self.mode == 1 and (win1_x < SCREEN_WIDTH or win2_x < SCREEN_WIDTH)):

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
        for w in ['win3','win4','win5','win6','win7','win8','win9','win10']:
            self.windows[w].withdraw()

        base_size = int(SCREEN_HEIGHT / 12)
        y_position = int(SCREEN_HEIGHT * (1 - WIN_HEIGHT_1))

        # 更新窗口1的几何属性
        self.windows['win1'].geometry(f"{base_size}x{base_size}+{int(SCREEN_WIDTH * WIN_POSITIONS['win1_x'])}+{y_position}")
        self.windows['win1'].deiconify()
    
        # 更新窗口2的几何属性
        self.windows['win2'].geometry(f"{base_size}x{base_size}+{int(SCREEN_WIDTH * WIN_POSITIONS['win2_x'])}+{y_position}")
        self.windows['win2'].deiconify()

if __name__ == '__main__':
    app = VirtualDesktopToggler()
    app.root.mainloop()
