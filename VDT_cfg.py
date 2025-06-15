import tkinter as tk
import os
import sys
import pyautogui
import ctypes
from PIL import Image, ImageTk
import subprocess
import shutil

# pyinstaller打包关闭启动画面
try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

# pyinstaller打包调用嵌入的资源
def get_path(relative_path):
    try:
        base_path = sys._MEIPASS  # pyinstaller打包后的路径
    except AttributeError:
        base_path = os.path.abspath(".")  # 当前工作目录的路径

    return os.path.normpath(os.path.join(base_path, relative_path))

def backup_config_file():
    """备份数据文件"""
    original_path = r'data\data.csv'
    backup_dir = r'data'

    if not os.path.exists(backup_dir):
        try:
            os.makedirs(backup_dir)
        except OSError:
            return

    if not os.path.exists(original_path):
        return

    max_backup_num = 0
    for filename in os.listdir(backup_dir):
        if filename.startswith('data.csv.'):
            try:
                backup_num = int(filename.split('.')[-1])
                if backup_num > max_backup_num:
                    max_backup_num = backup_num
            except ValueError:
                continue

    new_backup_num = 1
    backup_path = os.path.join(backup_dir, f'data.csv.{new_backup_num:03d}')

    try:
        shutil.copy2(original_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"备份配置文件失败: {str(e)}")
        return None

backup_file = backup_config_file()

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

class ConfigTool:
    """设置主窗口"""
    def __init__(self, backup_file, main_app):
        self.backup_file = backup_file
        self.main_app = main_app
        self.root = tk.Toplevel()
        self.root.title("VD_Toggler配置工具")
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.root.bind("<Unmap>", self.on_minimize)


        icon_path = 'img/els/cfg.png'
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon_photo)

        # 窗口大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        with open(r'data\vdtcfg.csv', 'r') as f:
            lines = f.readlines()
        window_width = int(lines[0].strip())
        window_height = int(lines[1].strip())
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(True, True)

        # 计算基础字体大小
        self.base_font_size = int(lines[2].strip())

        # 创建字体对象
        font_family = ["Microsoft YaHei", "sans-serif"]
        self.default_font = (font_family[0], self.base_font_size)
        self.title_font = (font_family[0], self.base_font_size, 'bold')
        
        # 将窗口居中显示
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.setup_ui()

    def get_system_scaling(self):
        """通过注册表获取系统缩放比例"""
        import ctypes
        shcore = ctypes.windll.shcore
        monitor = ctypes.windll.user32.MonitorFromWindow(ctypes.windll.user32.GetDesktopWindow(), 2)
        dpi = ctypes.c_uint()
        shcore.GetDpiForMonitor(monitor, 0, ctypes.byref(dpi), ctypes.byref(dpi))
        return dpi.value / 96.0

    def setup_ui(self):
        """设置窗口内容"""
        self.root.configure(bg='white')
        self.root.bind("<Configure>", self.on_window_resize)
        
        # 主容器，使用网格布局
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 配置网格权重
        main_frame.grid_rowconfigure(0, weight=0)  # 提示文本
        main_frame.grid_rowconfigure(1, weight=0)  # 模式选择
        main_frame.grid_rowconfigure(2, weight=0)  # 瞬匿模式
        main_frame.grid_rowconfigure(3, weight=0)  # 按钮大小
        main_frame.grid_rowconfigure(4, weight=0)  # 隐藏移速
        main_frame.grid_rowconfigure(5, weight=1)  # 按钮区域（占用剩余空间）
        main_frame.grid_columnconfigure(0, weight=1)  # 单列布局
        
        # 提示文本
        label = tk.Label(main_frame, 
                        text="你可以通过拖动按钮来自定义布局。\n若想保留更改，请点击“确定”；若想放弃更改，请点击“取消”。",
                        wraplength=0.16, 
                        font=self.default_font,
                        justify="left", 
                        bg='white')
        label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 7))

        # 模式选择 - 使用网格布局
        mode_frame = tk.LabelFrame(main_frame, text=" 模式选择 ", font=self.title_font, bg='white', padx=10, pady=5)
        mode_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # 获取当前模式
        try:
            with open(r'data\data.csv', 'r') as f:
                first_line = f.readline().strip()
                current_mode = int(first_line.split(',')[0]) if first_line else 1
        except:
            current_mode = 1

        self.switch_var = tk.IntVar(value=current_mode)
        
        tk.Label(mode_frame, text="悬浮球位置:", font=self.default_font, bg='white').pack(side="left", padx=(0, 10))
        
        tk.Radiobutton(mode_frame, text="左侧", font=self.default_font, variable=self.switch_var, 
                      value=2, command=self.update_switch, bg='white').pack(side="left")
        tk.Radiobutton(mode_frame, text="右侧", font=self.default_font, variable=self.switch_var, 
                      value=1, command=self.update_switch, bg='white').pack(side="left", padx=(0, 10))

        # 瞬匿模式 - 使用网格布局
        hide_frame = tk.LabelFrame(main_frame, text=" 瞬匿模式 ", font=self.title_font, bg='white', padx=10, pady=5)
        hide_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        try:
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()
                if len(lines) >= 14:
                    current_hide_mode = int(lines[13].split(',')[1]) if len(lines[13].split(',')) > 1 else 1
                else:
                    current_hide_mode = 1
        except:
            current_hide_mode = 1

        self.hide_mode_var = tk.IntVar(value=current_hide_mode)
        
        tk.Label(hide_frame, text="瞬匿效果:", font=self.default_font, bg='white').pack(side="left", padx=(0, 10))
        
        tk.Radiobutton(hide_frame, text="隐藏", font=self.default_font, variable=self.hide_mode_var, 
                      value=1, command=self.update_hide_mode, bg='white').pack(side="left", padx=(0, 10))
        tk.Radiobutton(hide_frame, text="退出", font=self.default_font, variable=self.hide_mode_var, 
                      value=2, command=self.update_hide_mode, bg='white').pack(side="left")

        # 按钮大小设置
        size_frame = tk.LabelFrame(main_frame, text=" 按钮大小 ", font=self.title_font, bg='white', padx=10, pady=10)
        size_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        try:
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()
                if len(lines) >= 15:
                    current_size = float(lines[14].split(',')[0]) if lines[14].strip() else 1.0
                else:
                    current_size = 1.0
        except:
            current_size = 1.0

        self.size_var = tk.DoubleVar(value=current_size)
        
        tk.Label(size_frame, text="大小倍数:", font=self.default_font, bg='white').pack(side="left", padx=(0, 10))
        
        size_slider = tk.Scale(size_frame, from_=0.1, to=3.0, resolution=0.1, font=self.default_font,
                              orient=tk.HORIZONTAL, variable=self.size_var,
                              command=self.update_size_setting, 
                              length=380, showvalue=0, bg='white')
        size_slider.pack(side="left")
        
        self.size_value_label = tk.Label(size_frame, text=f"{current_size:.1f}", font=self.default_font, bg='white')
        self.size_value_label.pack(side="left", padx=(10, 0))

        # 隐藏移速设置
        speed_frame = tk.LabelFrame(main_frame, text=" 隐藏移速 ", font=self.title_font, bg='white', padx=10, pady=10)
        speed_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        try:
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()
                if len(lines) >= 15:
                    parts = lines[14].strip().split(',')
                    current_speed = float(parts[1]) if len(parts) > 1 else 1.0
                else:
                    current_speed = 1.0
        except:
            current_speed = 1.0

        self.speed_var = tk.DoubleVar(value=current_speed)
        
        tk.Label(speed_frame, text="移动速度:", font=self.default_font, bg='white').pack(side="left", padx=(0, 10))
        
        speed_slider = tk.Scale(speed_frame, from_=0.25, to=3.0, resolution=0.25, font=self.default_font,
                               orient=tk.HORIZONTAL, variable=self.speed_var,
                               command=self.update_speed_setting,
                               length=380, showvalue=0, bg='white')
        speed_slider.pack(side="left")
        
        self.speed_value_label = tk.Label(speed_frame, text=f"{current_speed:.2f}", font=self.default_font, bg='white')
        self.speed_value_label.pack(side="left", padx=(10, 0))

        # 按钮区域
        button_frame1 = tk.Frame(main_frame, bg='white')
        button_frame1.grid(row=5, column=0, sticky="w", pady=(10, 0))
        button_frame2 = tk.Frame(main_frame, bg='white')
        button_frame2.grid(row=5, column=0, sticky="e", pady=(10, 0))
        
        # 复原按钮
        reset_btn = tk.Button(button_frame1, text="复原", font=self.default_font, width=7, 
                            command=self.show_reset_confirm, bg='white')
        reset_btn.grid(row=0, column=0, padx=(0, 280))
        
        # 确定按钮
        ok_btn = tk.Button(button_frame2, text="确定", font=self.default_font, width=7, 
                          command=self.on_ok, bg='white')
        ok_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 取消按钮
        cancel_btn = tk.Button(button_frame2, text="取消", font=self.default_font, width=7, 
                             command=self.on_cancel, bg='white')
        cancel_btn.grid(row=0, column=2)

        # 配置网格权重使内容居中
        main_frame.columnconfigure(0, weight=1)

    def update_switch(self):
        """更新左右模式状态到配置文件"""
        selected_mode = self.switch_var.get()
        try:
            # 读取现有配置文件
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()

            if not lines:
                lines = ["1,\n"]

            parts = lines[0].strip().split(',')
            if len(parts) < 2:
                parts = ['1', '0']  # 默认值
            parts[0] = str(selected_mode)
            lines[0] = ','.join(parts) + '\n'

            # 写回文件
            with open(r'data\data.csv', 'w') as f:
                f.writelines(lines)

            # 更新主程序模式并重新加载
            self.main_app.mode = selected_mode
            self.main_app.reload_windows()

        except Exception as e:
            print(f"更新悬浮球位置失败: {str(e)}")

    def on_ok(self):
        """点击确定按钮的处理"""
        if self.backup_file and os.path.exists(self.backup_file):
            try:
                os.remove(self.backup_file)  # 删除备份文件
            except Exception as e:
                print(f"删除备份文件失败: {str(e)}")
        self.root.destroy()
        self.main_app.root.quit()

    def on_cancel(self):
        """点击取消按钮的处理"""
        original_file = r'data\data.csv'
        if self.backup_file and os.path.exists(self.backup_file):
            try:
                if os.path.exists(original_file):
                    os.remove(original_file)  # 删除当前配置文件
                shutil.move(self.backup_file, original_file)
            except Exception as e:
                print(f"恢复配置文件失败: {str(e)}")
        self.root.destroy()
        self.main_app.root.quit()  # 结束主程序

    def on_minimize(self, event):
        """窗口最小化时隐藏主程序窗口"""
        if event.widget != self.root:
            return

        # 隐藏所有VirtualDesktopToggler窗口
        for win in self.main_app.windows.values():
            win.withdraw()

        # 当窗口恢复时显示
        self.root.bind("<Map>", self.on_restore)

    def on_restore(self, event):
        """窗口从最小化恢复时显示主程序窗口"""
        if event.widget != self.root:
            return

        # 显示所有VirtualDesktopToggler窗口
        for win in self.main_app.windows.values():
            win.deiconify()
        self.main_app.windows['win3'].withdraw()

        # 移除绑定
        self.root.unbind("<Map>")

    def on_window_resize(self, event):
        """处理窗口大小改变事件"""
        if event.widget == self.root:  # 确保是主窗口的大小改变
            new_width = event.width
            new_height = event.height
        
            # 更新窗口大小变量
            self.window_width = new_width
            self.window_height = new_height
        
            with open(r'data\vdtcfg.csv', 'w') as f:
                f.write(f"{self.window_width}\n")
                f.write(f"{self.window_height}\n")
                f.write(f"{self.base_font_size}\n")

    def update_hide_mode(self):
        """更新瞬匿模式到配置文件"""
        selected_mode = self.hide_mode_var.get()
        try:
            # 读取现有配置文件
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()

            while len(lines) < 14:
                lines.append("0\n")

            parts = lines[13].strip().split(',')
            if len(parts) < 2:
                parts = ['0', '1']
            parts[1] = str(selected_mode)
            lines[13] = ','.join(parts) + '\n'

            # 写回文件
            with open(r'data\data.csv', 'w') as f:
                f.writelines(lines)

        except Exception as e:
            print(f"更新瞬匿模式失败: {str(e)}")

    def update_size_setting(self, value):
        """更新按钮大小设置到配置文件"""
        try:
            self.size_value_label.config(text=f"{float(value):.1f}")

            # 读取现有配置文件
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()

            while len(lines) < 15:
                lines.append("1.0\n")

            parts = lines[14].strip().split(',')
            if len(parts) < 1:
                parts = ['1.0']
            parts[0] = str(float(value))
            lines[14] = ','.join(parts) + '\n'

            # 写回文件
            with open(r'data\data.csv', 'w') as f:
                f.writelines(lines)

            # 通知主程序重新加载窗口
            self.main_app.reload_windows()

        except Exception as e:
            print(f"更新按钮大小失败: {str(e)}")

    def update_speed_setting(self, value):
        """更新移动速度设置到配置文件"""
        try:
            speed_value = float(value)
            self.speed_value_label.config(text=f"{speed_value:.2f}")

            # 读取现有配置文件
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()

            while len(lines) < 15:
                lines.append("1.0\n")

            parts = lines[14].strip().split(',')
            if len(parts) < 2:
                parts = ['1.0', '1.0']
            parts[1] = str(speed_value)
            lines[14] = ','.join(parts) + '\n'

            # 写回文件
            with open(r'data\data.csv', 'w') as f:
                f.writelines(lines)

        except Exception as e:
            print(f"更新移动速度失败: {str(e)}")

    def show_reset_confirm(self):
        """点击复原按钮的处理"""
        self.root.configure(bg='white')
        confirm_win = tk.Toplevel(self.root, bg='white')
        confirm_win.title("VD_Toggler配置工具")

        try:
            icon_path = 'img/els/cfg.png'
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_img)
                confirm_win.tk.call('wm', 'iconphoto', confirm_win._w, icon_photo)
        except Exception as e:
            print(f"无法加载图标: {str(e)}")

        # 设置窗口位置和大小
        window_width = 520
        window_height = 200
        screen_width = confirm_win.winfo_screenwidth()
        screen_height = confirm_win.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        confirm_win.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 添加内容
        label = tk.Label(confirm_win, text="是否要恢复到默认设置？", padx=20, pady=30, bg='white')
        label.pack()

        bottom_frame = tk.Frame(confirm_win, bg='white')
        bottom_frame.pack(side='bottom', fill='x', pady=(5, 15))

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
        try:
            with open(r'data\data.csv', 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                parts = first_line.split(',')
                self.mode = int(parts[0]) if parts else 1
                self.sub_mode = int(parts[1]) if len(parts) > 1 else 0
        except:
            self.mode = 1
            self.sub_mode = 0
        self.setup_ui()
        self.config_tool = ConfigTool(backup_file, self)

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
            win.name = f'win{num}'
            win.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
            self.win_sizes[f'win{num}'] = (w, h)

        self.update_appearance()
        self.bind_events()
        self.root.withdraw()

    def update_appearance(self):
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
            10: ('Y',0.8)
        }

        for num in range(1,11):
            win = self.windows[f'win{num}']
            img_file, alpha = alpha_config[num]
            img_path = f'img/cfg/{img_file}.png'
            self.orig_pos[f'win{num}'] = (win.winfo_x(), win.winfo_y())

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

        for w in ['win3']:
            self.windows[w].withdraw()

    def reload_windows(self):
        """重新加载所有窗口"""
        # 销毁现有窗口
        for win in self.windows.values():
            win.destroy()
        self.windows.clear()
        self.win_sizes.clear()
        self.orig_pos = {}

        # 重新加载配置
        global config, WIN_HEIGHT_1, WIN_POSITIONS
        config = load_config()
        WIN_HEIGHT_1 = config['WIN_HEIGHT_1']
        WIN_POSITIONS = config['WIN_POSITIONS']

        self.setup_ui()

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

        # 同步处理win4-10横向坐标
        elif win_name in ['win4', 'win5', 'win6', 'win7', 'win8', 'win9', 'win10']:
            current_x = new_x

            control_wins = [f'win{i}' for i in range(4, 11)]
            for other_win_name in control_wins:
                if other_win_name != win_name:
                    other_win = self.windows.get(other_win_name)
                    if other_win:
                        current_y = other_win.winfo_y()
                        other_win.geometry(f"+{int(current_x)}+{int(current_y)}")

            # 同步win9和win10的垂直坐标
            if win_name in ['win9', 'win10']:
                target_win_name = 'win10' if win_name == 'win9' else 'win9'
                target_win = self.windows.get(target_win_name)
                if target_win:
                    target_win.geometry(f"+{int(new_x)}+{int(new_y)}")

    def on_drag_end(self, event):
        """拖动结束的处理"""
        if self.dragging:
            self.save_positions()
        self.dragging = None

    def save_positions(self):
        """保存窗口位置到配置文件"""
        try:
            with open(r'data\data.csv', 'r') as f:
                lines = f.readlines()

            while len(lines) < 15:
                lines.append("0\n")

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
                'y_y': self.windows['win10'].winfo_y() / SCREEN_HEIGHT,
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
                positions['y_y']
            ]

            # 更新当前模式对应的值
            for i, value in enumerate(config_lines):
                idx = i + 1  # 第1行是WIN_HEIGHT_1，第2行是win1_x，以此类推
                if idx < len(lines):
                    parts = lines[idx].strip().split(',')
                    if len(parts) < 2:  # 如果只有1个值，补齐
                        parts = ['0', '0']

                    parts[current_mode] = str(value)
                    lines[idx] = ','.join(parts) + '\n'

            # 写回文件
            with open(r'data\data.csv', 'w') as f:
                f.writelines(lines)

        except Exception as e:
            print(f"保存位置失败: {str(e)}")

if __name__ == '__main__':
    app = VirtualDesktopToggler()
    app.root.mainloop()