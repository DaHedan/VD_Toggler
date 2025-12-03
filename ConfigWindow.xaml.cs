using System.ComponentModel;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Input;
using System.Windows.Media;

namespace VD_Toggler_3
{
    public partial class ConfigWindow : Window
    {
        // 配置快照与确认标记
        private readonly PositionsConfig _snapshot;
        private bool _confirmed;

        // 当前已显示的快捷键数量
        private int _keyComboCount = 0;

        public ConfigWindow()
        {
            InitializeComponent();

            // 创建当前配置快照
            _snapshot = PositionSettings.Snapshot();
            this.Closing += ConfigWindow_Closing;

            // 初始化
            InitKeyCombosFromConfig();
            UpdateKeyCombosVisibility();
        }

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
    }
}