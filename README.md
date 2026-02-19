# <img width="32" height="32" alt="VDT" src="https://github.com/user-attachments/assets/65090833-0ba9-41f2-b7b8-3d79ce2b9723" /> VD_Toggler_3.0 ![GitHub 版本](https://img.shields.io/github/v/release/DaHedan/VD_Toggler?include_prereleases) ![许可证](https://img.shields.io/github/license/DaHedan/VD_Toggler) ![支持系统](https://img.shields.io/badge/OS-Windows_10/11-blue??logo=windows) ![总下载量](https://img.shields.io/github/downloads/DaHedan/VD_Toggler/total) ![最后提交](https://img.shields.io/github/last-commit/DaHedan/VD_Toggler)
_为触屏制作的虚拟桌面UI工具_ - 无需键盘即可轻松使用 Windows 虚拟桌面（支持 Windows 10/11）

想要了解关于 VD_Toggler 详细信息请查看 [GitHub Wiki](https://github.com/DaHedan/VD_Toggler/wiki/VD_Toggler-v3.0-wiki)。

## 📜 许可协议
本项目采用 [MIT 许可证](https://github.com/DaHedan/VD_Toggler/blob/main/LICENSE)

## 📦 获取工具 ![Windows](https://img.shields.io/badge/下载-Windows_应用程序-blue?logo=windows)
> 本软件安装包使用 Inno Setup Compiler 制作（旧版本使用 Nuitka 或 PyInstaller 打包）。  
> 本软件依赖 .NET 8.0 运行，您可以通过微软官方渠道下载安装该组件，或者下载自包含该组件的软件包。

如果你的需求是下载这个软件去使用，而不是需要源代码，请到 [**Releases VD_Toggler v3.1**](https://github.com/DaHedan/VD_Toggler/releases/tag/v3.1.0-alpha) 下载对应的文件，不要下载上面的 Code
### 普通用户推荐下载
Windows 64位系统：[VD_Toggler_3.1_alpha_x64_Setup_selfcontained.exe](https://github.com/DaHedan/VD_Toggler/releases/download/v3.1.0-alpha/VD_Toggler_3.1_alpha_x64_selfcontained_Setup.exe)  
Windows 32位系统：[VD_Toggler_3.1_alpha_x86_Setup_selfcontained.exe](https://github.com/DaHedan/VD_Toggler/releases/download/v3.1.0-alpha/VD_Toggler_3.1_alpha_x86_selfcontained_Setup.exe)

### 其他版本：  
  * [VD_Toggler v2.2.0](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.2.0)
  * [VD_Toggler v2.1.1](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.1.1)
  * [VD_Toggler v2.0.1](https://github.com/DaHedan/VD_Toggler/releases/tag/v2.0.1)

## 🖥️ 功能介绍
> 鼠标的右键点击操作对应触摸屏的长按操作
### 主程序
1.	运行主程序后，会弹出两个半透明图标。点击 <img width="16" height="16" alt="L1" src="https://github.com/user-attachments/assets/007ab724-7ac6-469e-8e90-d4c8b9909285" /> 或 <img width="16" height="16" alt="R1" src="https://github.com/user-attachments/assets/987dd230-14f8-4d58-b3bf-6c48e97c1621" /> 按钮，可切换虚拟桌面。_(Win + Ctrl + ←/→ 效果)_
> 当处于第一个桌面时不会出现 <img width="16" height="16" alt="L1" src="https://github.com/user-attachments/assets/007ab724-7ac6-469e-8e90-d4c8b9909285" /> 按钮，当处于最后一个桌面时 <img width="16" height="16" alt="R1" src="https://github.com/user-attachments/assets/987dd230-14f8-4d58-b3bf-6c48e97c1621" /> 按钮会变成 <img width="16" height="16" alt="RA" src="https://github.com/user-attachments/assets/f7db212e-d30f-4479-ba32-6ced64bd0103" /> 按钮。  
2.	右击/长按 <img width="16" height="16" alt="L1" src="https://github.com/user-attachments/assets/007ab724-7ac6-469e-8e90-d4c8b9909285" /> 或 <img width="16" height="16" alt="R1" src="https://github.com/user-attachments/assets/987dd230-14f8-4d58-b3bf-6c48e97c1621" /> 按钮，展开隐藏面板 _(点击 <img width="16" height="16" alt="L1" src="https://github.com/user-attachments/assets/007ab724-7ac6-469e-8e90-d4c8b9909285" /> 或 <img width="16" height="16" alt="R1" src="https://github.com/user-attachments/assets/987dd230-14f8-4d58-b3bf-6c48e97c1621" /> 按钮可收起隐藏面板)_：  
   (1) 点击“__退出__”，关闭此工具。  
   (2) 点击“__隐藏__”，按钮收起到屏幕左/右侧的半圆形悬浮球。点击悬浮球，可恢复按钮。_(配置工具中可选择收起到左侧或右侧)_  
   (3) 点击“__关闭桌面__”，关闭当前桌面。_(Win + Ctrl + F4 效果)_  
   (4) 点击“__添加桌面__”，添加一个桌面。_(Win + Ctrl + D 效果)_  
   (5) 点击“__查看全部__”，可以显示所有桌面和应用的缩略图。_(Win + Tab 效果)_   
   (6) 点击“__设置⚙️__”，打开 __配置工具VDT_cfg__。
### 配置工具
1. 通过拖动桌面上的按钮图标至合适位置，可修改按键布局。
2. 中央的窗口中可修改更多内容：  
  <img width="350" height="264" alt="VDT_Cfg1" src="https://github.com/user-attachments/assets/e08eadfe-4fb2-4af8-87d1-8183f8b36985" /> 
  <img width="350" height="264" alt="VDT_Cfg2" src="https://github.com/user-attachments/assets/ab0d99dc-bcec-499c-be00-18082e65895e" />

4. 点击中央窗口底部的“__确定__”按钮，可保留更改。  
5. 点击中央窗口底部的“__取消__”按钮，可放弃更改。  
6. 点击中央窗口底部的“__复原__”按钮，可恢复默认的配置数据。

## ⚠️ 用户须知
1. 此工具仅供非商业使用，用户需自行承担使用过程中的风险（如程序异常、设备问题等），作者不对任何直接或间接损失负责。  
2. 此工具仅在用户本地存储配置数据，不会收集、上传任何用户信息。  
3. 若需二次分发或商用，需提前联系作者获得授权。  
