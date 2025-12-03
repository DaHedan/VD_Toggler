using System;
using System.Runtime.InteropServices;

namespace VD_Toggler_3
{
    internal static class DisplayHelper
    {
        // 导入用户32.dll中的系统消息发送函数
        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern IntPtr SendMessage(
            IntPtr hWnd,   // 窗口句柄（广播到所有窗口用0xFFFF）
            uint Msg,      // 消息类型
            IntPtr wParam, // 消息参数1
            IntPtr lParam  // 消息参数2
        );

        // 系统命令消息（控制系统级操作）
        private const uint WM_SYSCOMMAND = 0x0112;
        // 显示器电源控制的命令码
        private const int SC_MONITORPOWER = 0xF170;
        // 关闭显示器的参数（2=关闭，1=开启，-1=节能）
        private const int MONITOR_OFF = 2;
        // 广播消息的目标窗口句柄（所有顶级窗口）
        private static readonly IntPtr HWND_BROADCAST = new IntPtr(0xFFFF);

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern nint PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        public static void TurnOffDisplays()
        {
            // 发送关闭显示器的系统消息
            IntPtr result = PostMessage(HWND_BROADCAST, WM_SYSCOMMAND, (IntPtr)SC_MONITORPOWER, (IntPtr)MONITOR_OFF);
        }
    }
}