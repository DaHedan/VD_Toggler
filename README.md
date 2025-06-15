# <img src="https://github.com/DaHedan/VD_Toggler/blob/main/img/els/VDT.png" alt="VD_Toggler" style="width:6%">  VD_Toggler_2.0 ![GitHub 版本](https://img.shields.io/github/v/release/DaHedan/VD_Toggler) ![许可证](https://img.shields.io/github/license/DaHedan/VD_Toggler) ![总下载量](https://img.shields.io/github/downloads/DaHedan/VD_Toggler/total) ![支持系统](https://img.shields.io/badge/Win7/10/11_x64-✓-green??logo=windows) ![最后提交](https://img.shields.io/github/last-commit/DaHedan/VD_Toggler)
_专为触摸屏优化的虚拟桌面管理工具_ - 无需键盘即可轻松使用 Windows 虚拟桌面（支持 Win7/10/11）
## 🗂️ 文件说明
data/data.csv用于储存主程序的配置信息，data/vdtcfg.csv用于储存配置工具的窗口大小和字体大小。  
img文件夹用于存放代码调用的图片文件。  
VD_Toggler_2.0.py为主程序  
VDT_cfg.py为配置工具  
> 要实现两个程序内的调用，需将代码打包为exe格式的可执行文件。
## 📚 依赖库
此项目用到的Python标准库有：os、sys、tkinter、pyautogui、ctypes、PIL、subprocess、shutil。
## 📜 许可协议
本项目采用[MIT 许可证](https://github.com/DaHedan/VD_Toggler/blob/main/LICENSE)
## 🖥️ 功能介绍
> 鼠标的右键点击操作对应触摸屏的长按操作
### 主程序VD_Toggler_2.0
1.	运行主程序后，会弹出两个半透明图标。点击“__<__” 或“__>__”按钮，可切换虚拟桌面。_(Win + Ctrl + ←/→ 效果)_
2.	右击/长按“__<__”或“__>__”按钮，展开隐藏面板 _(点击“__<__”或“__>__”按钮可收起隐藏面板)_：  
   (1) 点击“__退出__”，关闭此工具。  
   (2) 点击“__隐藏__”，按钮收起到屏幕左/右侧的半圆形悬浮球。点击悬浮球，可恢复按钮。_(配置工具中可选择收起到左侧或右侧)_  
   (3) 点击“__关闭桌面__”，关闭当前桌面。_(Win + Ctrl + F4 效果)_  
   (4) 点击“__添加桌面__”，添加一个桌面。_(Win + Ctrl + D 效果)_  
   (5) 点击“__查看全部__	”按钮，可以显示所有桌面和应用的缩略图。_(Win + Tab 效果)_  
   (6) 打开“__瞬匿__	”按钮，在切换桌面后，会自动触发隐藏或退出。_(配置工具中可选择隐藏或退出)_  
   (7) 点击设置图标⚙️，打开 __配置工具VDT_cfg__。
### 配置工具VDT_cfg
> 如果中央的配置窗口内容显示不全，可拉动改变大小，之后会保持此大小。  
> 若觉得配置窗口的字体大小不合适，请用 __记事本__ 或 __Excel__ 打开data/vdtcfg.csv并手动修改第三行的数据（默认值为8）。
1. 通过拖动桌面上的按钮图标至合适位置，可修改按键布局。
2. 中央的窗口中可修改更多内容：  
   (1) “__模式选择__”，用于选择 __隐藏__ 时按钮收起到左侧或右侧。  
   (2) “__瞬匿模式__”，用于选择 __瞬匿__ 下虚拟桌面切换功能使用一次后自动触发 __隐藏__ 或 __退出__。  
   (3) “__按钮大小__”，用于设置主程序UI按钮的大小。_(数值为默认值的倍数)_  
   (4) “__隐藏移速__”，用于设置 __隐藏__ 时按钮移动到屏幕边缘的动画速度。_(数值为默认值的倍数)_
3. 点击中央窗口底部的“__确定__”按钮，可保留更改。
4. 点击中央窗口底部的“__取消__”按钮，可放弃更改。
5. 点击中央窗口底部的“__复原__”按钮，可恢复默认的配置数据。
## 📦 下载安装包 ![Windows 安装程序](https://img.shields.io/badge/下载-Windows_安装程序-blue?logo=windows)
[VD_Toggler_2.0_x64_Setup.exe](https://github.com/DaHedan/VD_Toggler/releases/download/v2.0.0/VD_Toggler_2.0_x64_Setup.exe)
