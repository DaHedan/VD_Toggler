using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace VD_Toggler_3
{
    internal sealed class DisplayMonitorInfo
    {
        public required string DeviceName { get; init; }
        public bool IsPrimary { get; init; }
        public int Left { get; init; }
        public int Top { get; init; }
        public int Width { get; init; }
        public int Height { get; init; }
    }

    internal static class DisplayMonitorHelper
    {
        public static IReadOnlyList<DisplayMonitorInfo> GetMonitors()
        {
            var list = new List<DisplayMonitorInfo>();
            EnumDisplayMonitors(IntPtr.Zero, IntPtr.Zero, (hMon, _, _, __) =>
            {
                var info = new MONITORINFOEX();
                info.cbSize = Marshal.SizeOf<MONITORINFOEX>();
                if (GetMonitorInfo(hMon, ref info))
                {
                    int width = info.rcMonitor.Right - info.rcMonitor.Left;
                    int height = info.rcMonitor.Bottom - info.rcMonitor.Top;
                    list.Add(new DisplayMonitorInfo
                    {
                        DeviceName = info.szDevice,
                        IsPrimary = (info.dwFlags & MONITORINFOF_PRIMARY) != 0,
                        Left = info.rcMonitor.Left,
                        Top = info.rcMonitor.Top,
                        Width = width,
                        Height = height
                    });
                }
                return true;
            }, IntPtr.Zero);

            return list;
        }

        public static DisplayMonitorInfo? FindByDeviceName(string? deviceName)
        {
            if (string.IsNullOrWhiteSpace(deviceName)) return null;
            foreach (var m in GetMonitors())
            {
                if (string.Equals(m.DeviceName, deviceName, StringComparison.OrdinalIgnoreCase))
                    return m;
            }
            return null;
        }

        public static DisplayMonitorInfo GetPrimary()
        {
            foreach (var m in GetMonitors())
            {
                if (m.IsPrimary) return m;
            }
            var list = GetMonitors();
            return list.Count > 0 ? list[0] : new DisplayMonitorInfo
            {
                DeviceName = "Unknown",
                IsPrimary = true,
                Left = 0,
                Top = 0,
                Width = 1920,
                Height = 1080
            };
        }

        private const int MONITORINFOF_PRIMARY = 0x00000001;

        private delegate bool MonitorEnumProc(IntPtr hMonitor, IntPtr hdcMonitor, IntPtr lprcMonitor, IntPtr dwData);

        [DllImport("user32.dll")]
        private static extern bool EnumDisplayMonitors(IntPtr hdc, IntPtr lprcClip, MonitorEnumProc lpfnEnum, IntPtr dwData);

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        private static extern bool GetMonitorInfo(IntPtr hMonitor, ref MONITORINFOEX lpmi);

        [StructLayout(LayoutKind.Sequential)]
        private struct RECT
        {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;
        }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        private struct MONITORINFOEX
        {
            public int cbSize;
            public RECT rcMonitor;
            public RECT rcWork;
            public int dwFlags;

            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string szDevice;
        }
    }
}