using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;

namespace VD_Toggler_3
{
    [Flags]
    internal enum RegChangeNotifyFilter : uint
    {
        Name = 0x1,
        Attributes = 0x2,
        LastSet = 0x4,
        Security = 0x8
    }

    // 监视注册表项变化的类
    internal sealed class RegistryMonitor : IDisposable
    {
        private const int KEY_NOTIFY = 0x0010;
        private static readonly UIntPtr HKEY_CURRENT_USER = new UIntPtr(0x80000001u);

        [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern int RegOpenKeyEx(UIntPtr hKey, string lpSubKey, uint ulOptions, int samDesired, out IntPtr phkResult);

        [DllImport("advapi32.dll", SetLastError = true)]
        private static extern int RegNotifyChangeKeyValue(IntPtr hKey, bool bWatchSubtree, RegChangeNotifyFilter dwNotifyFilter, IntPtr hEvent, bool fAsynchronous);

        [DllImport("advapi32.dll")]
        private static extern int RegCloseKey(IntPtr hKey);

        private readonly string _subKey;
        private IntPtr _hKey;
        private readonly AutoResetEvent _event = new(false);
        private RegisteredWaitHandle? _waitHandle;
        private bool _disposed;

        public event Action? Changed;

        // 私有构造函数，外部通过 TryCreateHKCU 创建实例
        private RegistryMonitor(string subKey, IntPtr handle)
        {
            _subKey = subKey;
            _hKey = handle;

            Arm();
            _waitHandle = ThreadPool.RegisterWaitForSingleObject(_event, OnSignaled, null, -1, false);
        }

        // 静态方法：尝试创建监视 HKCU 子键变化的实例
        public static RegistryMonitor? TryCreateHKCU(string subKey)
        {
            try
            {
                if (RegOpenKeyEx(HKEY_CURRENT_USER, subKey, 0, KEY_NOTIFY, out var handle) == 0 && handle != IntPtr.Zero)
                {
                    return new RegistryMonitor(subKey, handle);
                }
            }
            catch { }
            return null;
        }

        // 布防监视注册表项变化
        private void Arm()
        {
            // 关注键名/键值最后一次写入（某些系统会先更新列表再更新当前值）
            RegNotifyChangeKeyValue(_hKey, true, RegChangeNotifyFilter.Name | RegChangeNotifyFilter.LastSet, _event.SafeWaitHandle.DangerousGetHandle(), true);
        }

        // 回调：注册表项变化时触发
        private void OnSignaled(object? state, bool timedOut)
        {
            if (_disposed) return;

            try { Changed?.Invoke(); }
            catch (Exception ex) { Debug.WriteLine($"RegistryMonitor '{_subKey}' callback error: {ex}"); }
            finally
            {
                if (!_disposed)
                    Arm(); // 重新布防，继续下一次通知
            }
        }

        // 实现 IDisposable 接口，释放资源
        public void Dispose()
        {
            if (_disposed) return;
            _disposed = true;

            try { _waitHandle?.Unregister(null); } catch { }
            try { _event.Dispose(); } catch { }
            try { if (_hKey != IntPtr.Zero) RegCloseKey(_hKey); } catch { }
            _hKey = IntPtr.Zero;
        }
    }
}