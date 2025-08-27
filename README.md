# VD_Toggler_2.1 ![许可证](https://img.shields.io/github/license/DaHedan/VD_Toggler) ![GitHub 版本](https://img.shields.io/github/v/release/DaHedan/VD_Toggler) ![支持系统](https://img.shields.io/badge/Windows_10/11-✓-green??logo=windows) ![总下载量](https://img.shields.io/github/downloads/DaHedan/VD_Toggler/total) ![最后提交](https://img.shields.io/github/last-commit/DaHedan/VD_Toggler)
_为触屏制作的虚拟桌面UI工具_ - 无需键盘即可轻松使用 Windows 虚拟桌面（支持 Windows 10/11）
## 🗂️ 文件说明
data/data.csv用于储存主程序的配置信息。
img文件夹用于存放代码调用的图片文件。  
VD_Toggler_2.1.1.py为主程序  
VDT_cfg_2.1.1.py为配置工具  
## 📚 依赖库
此项目用到的Python标准库有：os、sys、tkinter、pyautogui、ctypes、PIL、subprocess、shutil、pyvda、pycaw、comtypes。
## 📜 许可协议
本项目采用[MIT 许可证](https://github.com/DaHedan/VD_Toggler/blob/main/LICENSE)
## 🖥️ 功能介绍
> 鼠标的右键点击操作对应触摸屏的长按操作
### 主程序VD_Toggler_2.1.1
1.	运行主程序后，会弹出两个半透明图标。点击“__<__”或“__>__”按钮，可切换虚拟桌面。_(Win + Ctrl + ←/→ 效果)_
2.	右击/长按“__<__”或“__>__”按钮，展开隐藏面板 _(点击“__<__”或“__>__”按钮可收起隐藏面板)_：  
   (1) 点击“__退出__”，关闭此工具。  
   (2) 点击“__隐藏__”，按钮收起到屏幕左/右侧的半圆形悬浮球。点击悬浮球，可恢复按钮。_(配置工具中可选择收起到左侧或右侧)_  
   (3) 点击“__关闭桌面__”，关闭当前桌面。_(Win + Ctrl + F4 效果)_  
   (4) 点击“__添加桌面__”，添加一个桌面。_(Win + Ctrl + D 效果)_  
   (5) 点击“__查看全部__”，可以显示所有桌面和应用的缩略图。_(Win + Tab 效果)_   
   (6) 点击“__设置⚙️__”，打开 __配置工具VDT_cfg_2.1.1__。
### 配置工具VDT_cfg_2.1.1
1. 通过拖动桌面上的按钮图标至合适位置，可修改按键布局。
2. 中央的窗口中可修改更多内容：  
   (1) “__模式选择__”，用于选择 __隐藏__ 时按钮收起到 _左侧_ 或 _右侧_ 。  
   (2) “__瞬匿模式__”，用于选择是否让“__<__”和“__>__”按钮在切换桌面后立即消失，以及选择消失方式为 _隐藏_ 或 _退出_。  
   (3) “__自动静音__”，用于选择是否在切换桌面时静音。  
   (4) “__按钮大小__”，用于设置主程序UI按钮的大小。_(数值为默认值的倍数)_  
   (5) “__隐藏移速__”，用于设置 __隐藏__ 时按钮移动到屏幕边缘的动画速度。_(数值为默认值的倍数)_  
   (6) “__附加快捷键__”，用于设置切换桌面时自动触发的快捷键。_(最多添加4个快捷键)_  
4. 点击中央窗口底部的“__确定__”按钮，可保留更改。  
5. 点击中央窗口底部的“__取消__”按钮，可放弃更改。  
6. 点击中央窗口底部的“__复原__”按钮，可恢复默认的配置数据。
## ⚠️ 用户须知
1. 此工具仅供非商业使用，用户需自行承担使用过程中的风险（如程序异常、设备问题等），作者不对任何直接或间接损失负责。  
2. 此工具仅在用户本地存储配置数据，不会收集、上传任何用户信息。  
3. 若需二次分发或商用，需提前联系作者获得授权。  
## 📦 获取工具 ![Windows](https://img.shields.io/badge/下载-Windows_应用程序-blue?logo=windows)
### Windows 64位系统：  
压缩包：[VD_Toggler_2.1.1_x64.zip](https://github.com/DaHedan/VD_Toggler/releases/download/v2.1.1/VD_Toggler_2.1.1_x64.zip)  
安装包：[VD_Toggler_2.1.1_x64_set_up.exe](https://github.com/DaHedan/VD_Toggler/releases/download/v2.1.1/VD_Toggler_2.1.1_x64_set_up.exe)
### Windows 32位系统：  
压缩包：[VD_Toggler_2.1.1_x86.zip](https://github.com/DaHedan/VD_Toggler/releases/download/v2.1.1/VD_Toggler_2.1.1_x86.zip)  
安装包：[VD_Toggler_2.1.1_x86_set_up.exe](https://github.com/DaHedan/VD_Toggler/releases/download/v2.1.1/VD_Toggler_2.1.1_x86_set_up.exe)

### 其他版本：  
[VD_Toggler v2.0.0](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.0.0)
