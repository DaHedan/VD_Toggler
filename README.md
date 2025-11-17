# <img width="32" height="32" alt="VDT" src="https://github.com/user-attachments/assets/65090833-0ba9-41f2-b7b8-3d79ce2b9723" /> VD_Toggler_2.2 ![GitHub 版本](https://img.shields.io/github/v/release/DaHedan/VD_Toggler?include_prereleases) ![许可证](https://img.shields.io/github/license/DaHedan/VD_Toggler) ![支持系统](https://img.shields.io/badge/OS-Windows_10/11-blue??logo=windows) ![总下载量](https://img.shields.io/github/downloads/DaHedan/VD_Toggler/total) ![最后提交](https://img.shields.io/github/last-commit/DaHedan/VD_Toggler)
_为触屏制作的虚拟桌面UI工具_ - 无需键盘即可轻松使用 Windows 虚拟桌面（支持 Windows 10/11）

想要了解关于 VD_Toggler 详细信息请查看 [GitHub Wiki](https://github.com/DaHedan/VD_Toggler/wiki/VD_Toggler-v2.2-wiki)。

## 📜 许可协议
本项目采用 [MIT 许可证](https://github.com/DaHedan/VD_Toggler/blob/main/LICENSE)

## 📦 获取工具 ![Windows](https://img.shields.io/badge/下载-Windows_应用程序-blue?logo=windows)
> 软件使用 Nuitka（旧版本用了 PyInstaller）打包，由于技术原因，可能会被一些杀毒软件误报为病毒。  
如果您从本官方仓库下载，可以放心使用。

* 如果你的需求是下载这个软件去使用，而不是需要源代码，请点击下面的链接或者去 [Github Releases](https://github.com/DaHedan/VD_Toggler/releases) 下载对应的文件，不要下载上面的 Code
### Windows 64位系统：  
压缩包（解压后直接使用）：[VD_Toggler_2.2.0_x64.zip](https://github.com/DaHedan/VD_Toggler/releases/download/v2.2.0/VD_Toggler_2.2.0_x64.zip)  
安装包（安装后使用）：[VD_Toggler_2.2.0_x64_set_up.exe](https://github.com/DaHedan/VD_Toggler/releases/download/v2.2.0/VD_Toggler_2.2.0_x64_set_up.exe)
### Windows 32位系统：  
压缩包（解压后直接使用）：[VD_Toggler_2.2.0_x86.zip](https://github.com/DaHedan/VD_Toggler/releases/download/v2.2.0/VD_Toggler_2.2.0_x86.zip)  
安装包（安装后使用）：[VD_Toggler_2.2.0_x86_set_up.exe](https://github.com/DaHedan/VD_Toggler/releases/download/v2.2.0/VD_Toggler_2.2.0_x86_set_up.exe)

### 其他版本：  
  * [VD_Toggler v2.0.1](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.0.1)
  * [VD_Toggler v2.1.1](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.1.1)

  * 测试版：
    * [VD_Toggler v2.2.0-rc](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.2.0-rc)
    * [VD_Toggler v2.2.0-beta](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.2.0-beta)
    * [VD_Toggler v2.2.0-alpha](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.2.0-alpha)

## 🖥️ 功能介绍
> 鼠标的右键点击操作对应触摸屏的长按操作
### 主程序VD_Toggler_2.2.0
1.	运行主程序后，会弹出两个半透明图标。点击“__<__”或“__>__”按钮，可切换虚拟桌面。_(Win + Ctrl + ←/→ 效果)_
2.	右击/长按“__<__”或“__>__”按钮，展开隐藏面板 _(点击“__<__”或“__>__”按钮可收起隐藏面板)_：  
   (1) 点击“__退出__”，关闭此工具。  
   (2) 点击“__隐藏__”，按钮收起到屏幕左/右侧的半圆形悬浮球。点击悬浮球，可恢复按钮。_(配置工具中可选择收起到左侧或右侧)_  
   (3) 点击“__关闭桌面__”，关闭当前桌面。_(Win + Ctrl + F4 效果)_  
   (4) 点击“__添加桌面__”，添加一个桌面。_(Win + Ctrl + D 效果)_  
   (5) 点击“__查看全部__”，可以显示所有桌面和应用的缩略图。_(Win + Tab 效果)_   
   (6) 点击“__设置⚙️__”，打开 __配置工具VDT_cfg__。
### 配置工具VDT_cfg_2.2.0
1. 通过拖动桌面上的按钮图标至合适位置，可修改按键布局。
2. 中央的窗口中可修改更多内容：  
  * __功能__ 界面：  
    * “__瞬匿模式__”，用于选择是否让“__<__”和“__>__”按钮在切换桌面后立即消失，以及选择消失方式为 _隐藏_ 或 _退出_。  
    * “__自动静音__”，用于选择是否在切换桌面时静音。  
    * “__自动熄屏__”，用于选择切换桌面后是否自动熄屏休眠。  
    * “__附加快捷键__”，用于设置切换桌面时自动触发的快捷键。_(最多添加4个快捷键)_  
  * __UI__ 界面：  
    * “__模式选择__”，用于选择 _左侧_ 或 _右侧_ 的两套按钮布局，以及选择隐藏时的悬浮球是否 _贴边_ 。  
    * “__按钮大小__”，用于设置主程序 UI 按钮的大小。_(数值为默认值的倍数)_  
    * “__按钮不透明度__”，用于分别调整图形按钮和文字的不透明度。_(数值为默认值的倍数)_  
    * “__隐藏移速__”，用于设置 __隐藏__ 时按钮移动到屏幕边缘的动画速度。_(数值为默认值的倍数)_  
4. 点击中央窗口底部的“__确定__”按钮，可保留更改。  
5. 点击中央窗口底部的“__取消__”按钮，可放弃更改。  
6. 点击中央窗口底部的“__复原__”按钮，可恢复默认的配置数据。

## 📺 演示视频
[<img width="405" height="270" alt="视频" src="https://github.com/user-attachments/assets/4abb6b14-413a-451a-8819-00171cb98075" />](https://www.bilibili.com/video/BV1pExjzvEaD/)

## ⚠️ 用户须知
1. 此工具仅供非商业使用，用户需自行承担使用过程中的风险（如程序异常、设备问题等），作者不对任何直接或间接损失负责。  
2. 此工具仅在用户本地存储配置数据，不会收集、上传任何用户信息。  
3. 若需二次分发或商用，需提前联系作者获得授权。  
