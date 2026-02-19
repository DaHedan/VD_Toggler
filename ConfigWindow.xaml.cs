using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Navigation;

namespace VD_Toggler_3
{
    public partial class ConfigWindow : Window, INotifyPropertyChanged
    {
        // 配置快照与确认标记
        private readonly PositionsConfig _snapshot;
        private bool _confirmed;

        // 当前已显示的快捷键数量
        private int _keyComboCount = 0;

        public ObservableCollection<MonitorOption> MonitorOptions { get; } = new();

        private string? _primaryMonitorDeviceName;

        public event PropertyChangedEventHandler? PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string? name = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));

        public string? SelectedMonitorDeviceName
        {
            get
            {
                var cfg = PositionSettings.Current;
                return string.IsNullOrWhiteSpace(cfg.TargetMonitorDeviceName)
                    ? _primaryMonitorDeviceName
                    : cfg.TargetMonitorDeviceName;
            }
            set
            {
                var cfg = PositionSettings.Current;

                string? newValue;
                if(string.IsNullOrWhiteSpace(value) ||
            string.Equals(value, _primaryMonitorDeviceName, StringComparison.OrdinalIgnoreCase))
        {
                    newValue = null;
                }
        else
                {
                    newValue = value;
                }

                if (string.Equals(cfg.TargetMonitorDeviceName, newValue, StringComparison.OrdinalIgnoreCase))
                    return;

                cfg.TargetMonitorDeviceName = newValue;

                if (Owner is MainWindow mw)
                {
                    mw.ApplyMonitorPlacementFromSettings();
                }
            }
        }

        public ConfigWindow()
        {
            InitializeComponent();

            DataContext = this;

            // 创建当前配置快照
            _snapshot = PositionSettings.Snapshot();
            this.Closing += ConfigWindow_Closing;

            // 初始化
            InitKeyCombosFromConfig();
            UpdateKeyCombosVisibility();

            LoadMonitorOptions();

            Microsoft.Win32.SystemEvents.DisplaySettingsChanged += OnDisplaySettingsChanged;
            SourceInitialized += ConfigWindow_SourceInitialized;
        }

        protected override void OnClosed(EventArgs e)
        {
            // 移除事件处理
            Microsoft.Win32.SystemEvents.DisplaySettingsChanged -= OnDisplaySettingsChanged;
            SourceInitialized -= ConfigWindow_SourceInitialized;
            Closing -= ConfigWindow_Closing;

            ClearAllBindingsAndEvents(this);

            // 清理资源
            DataContext = null;
            MonitorOptions.Clear();
            Owner = null;

            base.OnClosed(e);
        }

        // 全面清理绑定和事件处理器
        private static void ClearAllBindingsAndEvents(DependencyObject root)
        {
            if (root == null) return;

            // 清理当前元素的绑定
            BindingOperations.ClearAllBindings(root);

            // 如果是控件，清理事件处理器
            if (root is FrameworkElement fe)
            {
                // 清理命令绑定
                fe.CommandBindings.Clear();
                fe.InputBindings.Clear();

                // 清理行为（如果有）
                if (fe is ItemsControl itemsControl)
                {
                    // 清理 ItemsSource 绑定（这是一个常见的内存泄漏源）
                    itemsControl.ItemsSource = null;
                    itemsControl.Items.Clear();
                }

                if (fe is ComboBox comboBox)
                {
                    comboBox.ItemsSource = null;
                    comboBox.Items.Clear();
                }
            }

            // 递归清理子元素
            int childCount = VisualTreeHelper.GetChildrenCount(root);
            for (int i = 0; i < childCount; i++)
            {
                var child = VisualTreeHelper.GetChild(root, i);
                ClearAllBindingsAndEvents(child);
            }
        }

        private void ConfigWindow_SourceInitialized(object? sender, EventArgs e)
            => ApplyTitleBarTheme();

        // 位置改动脏标记
        private bool _positionsDirty;

        // 供外部（MainWindow 拖拽结束时）标记位置已改动
        public void MarkPositionsDirty()
        {
            _positionsDirty = true;
        }

        // 根据已有配置初始化快捷键组合的可见性
        private void InitKeyCombosFromConfig()
        {
            var cfg = PositionSettings.Current;
            // 若已存在配置值，则让它们可见
            if (cfg.PreSwitchKey1.HasValue) keyboard1.Visibility = Visibility.Visible;
            if (cfg.PreSwitchKey2.HasValue) keyboard2.Visibility = Visibility.Visible;
            if (cfg.PreSwitchKey3.HasValue) keyboard3.Visibility = Visibility.Visible;
            if (cfg.PreSwitchKey4.HasValue) keyboard4.Visibility = Visibility.Visible;
        }

        // 更新快捷键组合的可见性
        private void UpdateKeyCombosVisibility()
        {
            // 决定可见性：
            var cfg = PositionSettings.Current;

            keyboard1.Visibility =
                (_keyComboCount >= 1) || cfg.PreSwitchKey1.HasValue ? Visibility.Visible : Visibility.Collapsed;

            keyboard2.Visibility =
                (_keyComboCount >= 2) || cfg.PreSwitchKey2.HasValue ? Visibility.Visible : Visibility.Collapsed;

            keyboard3.Visibility =
                (_keyComboCount >= 3) || cfg.PreSwitchKey3.HasValue ? Visibility.Visible : Visibility.Collapsed;

            keyboard4.Visibility =
                (_keyComboCount >= 4) || cfg.PreSwitchKey4.HasValue ? Visibility.Visible : Visibility.Collapsed;
        }

        // 添加快捷键组合
        private void button_add_Click(object sender, RoutedEventArgs e)
        {
            if (_keyComboCount < 4)
            {
                _keyComboCount++;
                UpdateKeyCombosVisibility();
            }
        }

        // 清除快捷键组合
        private void button_clear_Click(object sender, RoutedEventArgs e)
        {
            keyboard1.SelectedIndex = -1;
            keyboard2.SelectedIndex = -1;
            keyboard3.SelectedIndex = -1;
            keyboard4.SelectedIndex = -1;

            var cfg = PositionSettings.Current;
            cfg.PreSwitchKey1 = null;
            cfg.PreSwitchKey2 = null;
            cfg.PreSwitchKey3 = null;
            cfg.PreSwitchKey4 = null;

            _keyComboCount = 0;
            UpdateKeyCombosVisibility();
        }

        // 关闭窗口时的处理
        private void ConfigWindow_Closing(object? sender, CancelEventArgs e)
        {
            // 已确认（确定或复原）直接关闭，不弹窗，不恢复快照
            if (_confirmed)
                return;

            // 是否有改动（拖拽标记 或 配置对象变化）
            bool hasChanges = _positionsDirty || HasPositionChangesCore();

            if (hasChanges)
            {
                var dlg = new CancelConfirmWindow { Owner = this };
                var result = dlg.ShowDialog();

                // 继续编辑：阻止关闭
                if (result != true)
                {
                    e.Cancel = true;
                    return;
                }
            }

            // 放弃更改：恢复进入窗口时的快照
            PositionSettings.Restore(_snapshot);
            if (Owner is MainWindow mw)
            {
                mw.CancelConfigAndRefresh();
            }
        }

        // 原来的序列化比较逻辑拆到私有方法
        private bool HasPositionChangesCore()
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = false,
                PropertyNamingPolicy = null,
                DefaultIgnoreCondition = JsonIgnoreCondition.Never
            };
            var s1 = JsonSerializer.Serialize(_snapshot, options);
            var s2 = JsonSerializer.Serialize(PositionSettings.Current, options);
            return !string.Equals(s1, s2, StringComparison.Ordinal);
        }

        // 按钮事件处理
        private void button_cancel_Click(object sender, RoutedEventArgs e)
        {
            _confirmed = false; // 明确表示未保存
            Close();
        }

        // 确认按钮
        private void button_confirm_Click(object sender, RoutedEventArgs e)
        {
            _confirmed = true;
            if (Owner is MainWindow mw)
            {
                mw.ConfirmConfigAndSaveAndRefresh();
            }
            Close();
        }

        // 复原按钮
        private void button_restore_Click(object sender, RoutedEventArgs e)
        {
            // 弹窗确认
            var dlg = new RestoreConfirmWindow { Owner = this };
            var result = dlg.ShowDialog();
            if (result != true)
                return; // 取消

            // 恢复到默认配置（内存）
            var defaults = new PositionsConfig();
            PositionSettings.Restore(defaults);

            // 立即持久化到文件
            PositionSettings.Save();

            // 通知主窗体按当前配置刷新
            if (Owner is MainWindow mw)
            {
                mw.RefreshFromSettingsAfterRestore();
            }

            // 标记为“确认”，关闭窗口
            _confirmed = true;
            Close();
        }

        // 标题栏拖动/双击/系统菜单
        private void TitleBar_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ClickCount == 2)
            {
                ToggleMaximizeRestore();
            }
            else
            {
                try { DragMove(); } catch { /* 鼠标异常快速点击时可能抛出，忽略 */ }
            }
        }

        // 双击最大化/还原
        private void TitleBar_MouseDoubleClick(object sender, MouseButtonEventArgs e)
        {
            ToggleMaximizeRestore();
        }
        
        // 右键系统菜单
        private void TitleBar_MouseRightButtonUp(object sender, MouseButtonEventArgs e)
        {
            var screen = PointToScreen(e.GetPosition(this));
            SystemCommands.ShowSystemMenu(this, screen);
        }

        // 右上角按钮
        private void MinButton_Click(object sender, RoutedEventArgs e)
            => SystemCommands.MinimizeWindow(this);

        // 最大化/还原按钮
        private void MaxRestoreButton_Click(object sender, RoutedEventArgs e)
            => ToggleMaximizeRestore();

        // 关闭按钮
        private void CloseButton_Click(object sender, RoutedEventArgs e)
            => SystemCommands.CloseWindow(this);

        // 切换最大化/还原
        private void ToggleMaximizeRestore()
        {
            if (WindowState == WindowState.Maximized)
                SystemCommands.RestoreWindow(this);
            else
                SystemCommands.MaximizeWindow(this);
        }

        private const int DwmUseImmersiveDarkMode = 20;
        private const int DwmUseImmersiveDarkModeBefore20H1 = 19;

        [DllImport("dwmapi.dll")]
        private static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize);

        private void ApplyTitleBarTheme()
        {
            var hwnd = new WindowInteropHelper(this).Handle;
            if (hwnd == IntPtr.Zero)
                return;

            int useDark = 1;
            DwmSetWindowAttribute(hwnd, DwmUseImmersiveDarkMode, ref useDark, sizeof(int));
            DwmSetWindowAttribute(hwnd, DwmUseImmersiveDarkModeBefore20H1, ref useDark, sizeof(int));
        }

        public sealed class MonitorOption
        {
            public string? DeviceName { get; init; }
            public string DisplayName { get; init; } = string.Empty;
        }

        // 加载显示器选项
        private void LoadMonitorOptions()
        {
            MonitorOptions.Clear();

            int index = 1;
            var monitors = DisplayMonitorHelper.GetMonitors();
            foreach (var monitor in monitors)
            {
                if (monitor.IsPrimary)
                {
                    _primaryMonitorDeviceName = monitor.DeviceName;
                }

                string label = monitor.IsPrimary ? "主显示器" : $"显示器 {index}";
                string display = $"{label} - {monitor.DeviceName} ({monitor.Width}x{monitor.Height})";
                MonitorOptions.Add(new MonitorOption
                {
                    DeviceName = monitor.DeviceName,
                    DisplayName = display
                });
                index++;
            }

            var cfg = PositionSettings.Current;
            bool exists = monitors.Any(m =>
                string.Equals(m.DeviceName, cfg.TargetMonitorDeviceName, StringComparison.OrdinalIgnoreCase));

            if (!exists)
            {
                cfg.TargetMonitorDeviceName = null;
            }

            OnPropertyChanged(nameof(SelectedMonitorDeviceName));
        }

        // 监听显示设置变化
        private void OnDisplaySettingsChanged(object? sender, EventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                LoadMonitorOptions();
            });
        }

        // 超链接点击事件
        private void Hyperlink_RequestNavigate(object sender, RequestNavigateEventArgs e)
        {
            Process.Start(new ProcessStartInfo(e.Uri.AbsoluteUri) { UseShellExecute = true });
            e.Handled = true;
        }
    }
}
