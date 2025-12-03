using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace VD_Toggler_3
{
    public partial class MainWindow : Window, INotifyPropertyChanged
    {
        private HwndSource? _hwndSource;
        private const int WM_NCHITTEST = 0x0084;
        private const int HTTRANSPARENT = -1;
        private const int HTCLIENT = 1;

        // 导入设置窗口样式的API
        [DllImport("user32.dll")]
        private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern int GetWindowLong(IntPtr hWnd, int nIndex);

        // 窗口样式常量
        private const int GWL_EXSTYLE = -20; // 扩展样式索引
        private const int WS_EX_TOOLWINDOW = 0x00000080; // 工具窗口样式（不显示在任务栏）
        private const int WS_EX_APPWINDOW = 0x00040000;  // 应用窗口样式（显示在任务栏）

        // Button3 在正常模式下的拖动状态
        private bool _button3DragPending;     // 按下后，等待判断是否进入拖动
        private bool _button3DragInitiated;   // 已超过阈值，进入拖动
        private bool _button3WasDragged;      // 本次按下-抬起过程中发生过拖动（用于抑制点击）
        private Point _button3DownPoint;      // 鼠标按下时在 Canvas 内的位置
        private double _button3StartLeft;     // 拖动起始 Left
        private double _button3StartTop;      // 拖动起始 Top

        public MainWindow()
        {
            InitializeComponent();
            Loaded += Window_Loaded;
        }

        public event PropertyChangedEventHandler? PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string? name = null) =>
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));

        private bool _isOnLastDesktop;
        public bool IsOnLastDesktop
        {
            get => _isOnLastDesktop;
            private set
            {
                if (_isOnLastDesktop != value)
                {
                    _isOnLastDesktop = value;
                    OnPropertyChanged();
                }
            }
        }

        // 编辑模式:按钮1-9全部可见、带边框、可拖动，原功能取消
        private bool _isLayoutEditMode;
        private UIElement? _draggingElement;
        private Canvas? _dragCanvas;
        private Point _dragStartPoint;
        private double _dragStartLeft;
        private double _dragStartTop;
        private ConfigWindow? _configWindow;

        // 编辑模式下忽略事件处理
        private bool IgnoreIfEditMode(RoutedEventArgs e)
        {
            if (_isLayoutEditMode)
            {
                e.Handled = true;
                return true;
            }
            return false;
        }

        // 进入布局编辑模式
        private void EnterLayoutEditMode()
        {
            _isLayoutEditMode = true;

            // 显示按钮1-9
            ResetAndShowButton(Button1);
            ResetAndShowButton(Button2);
            ResetAndShowButton(Button3);
            ResetAndShowButton(Button4);
            ResetAndShowButton(Button5);
            ResetAndShowButton(Button6);
            ResetAndShowButton(Button7);
            ResetAndShowButton(Button8);
            ResetAndShowButton(Button9);

            // 视觉高亮
            var border = (Brush)new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FFFC00FF")!);
            ApplyEditVisual(Button1, true, border);
            ApplyEditVisual(Button2, true, border);
            ApplyEditVisual(Button3, true, border);
            ApplyEditVisual(Button4, true, border);
            ApplyEditVisual(Button5, true, border);
            ApplyEditVisual(Button6, true, border);
            ApplyEditVisual(Button7, true, border);
            ApplyEditVisual(Button8, true, border);
            ApplyEditVisual(Button9, true, border);

            // 强制显示按钮1
            Button1.Visibility = Visibility.Visible;
        }

        // 退出布局编辑模式
        private void ExitLayoutEditMode()
        {
            _isLayoutEditMode = false;

            // 清除高亮，恢复默认
            ApplyEditVisual(Button1, false, Brushes.Transparent);
            ApplyEditVisual(Button2, false, Brushes.Transparent);
            ApplyEditVisual(Button3, false, Brushes.Transparent);
            ApplyEditVisual(Button4, false, Brushes.Transparent);
            ApplyEditVisual(Button5, false, Brushes.Transparent);
            ApplyEditVisual(Button6, false, Brushes.Transparent);
            ApplyEditVisual(Button7, false, Brushes.Transparent);
            ApplyEditVisual(Button8, false, Brushes.Transparent);
            ApplyEditVisual(Button9, false, Brushes.Transparent);

            // 刷新按钮1可见性
            UpdateButton1VisibilityByDesktop();
        }

        // 应用编辑模式视觉效果
        private void ApplyEditVisual(Button btn, bool enable, Brush borderBrush)
        {
            if (enable)
            {
                // 仍设置 Button 自身的边框
                btn.BorderBrush = borderBrush;
                btn.BorderThickness = new Thickness(2);
                btn.Cursor = Cursors.SizeAll;

                // 始终添加 Adorner
                ShowEditAdorner(btn, borderBrush, 2);
            }
            else
            {
                // 还原 Button 自身属性
                btn.ClearValue(Button.BorderBrushProperty);
                btn.ClearValue(Button.BorderThicknessProperty);
                btn.Cursor = Cursors.Arrow;

                // 移除描边 Adorner
                HideEditAdorner(btn);
            }
        }

        // 为按钮附加拖拽事件处理程序
        private void AttachDragHandlers(Button btn)
        {
            btn.PreviewMouseLeftButtonDown += Button_PreviewMouseLeftButtonDown;
            btn.PreviewMouseMove += Button_PreviewMouseMove;
            btn.PreviewMouseLeftButtonUp += Button_PreviewMouseLeftButtonUp;
        }

        // 按钮拖拽事件处理程序
        private void Button_PreviewMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            // 配置模式
            if (_isLayoutEditMode)
            {
                if (sender is not UIElement el) return;

                var canvas = FindParentCanvas(el);
                if (canvas == null) return;

                _dragCanvas = canvas;
                _draggingElement = el;
                _dragStartPoint = e.GetPosition(canvas);

                _dragStartLeft = Canvas.GetLeft(el);
                if (double.IsNaN(_dragStartLeft)) _dragStartLeft = 0;

                _dragStartTop = Canvas.GetTop(el);
                if (double.IsNaN(_dragStartTop)) _dragStartTop = 0;

                el.CaptureMouse();
                e.Handled = true;
            }

            // Button3
            if (ReferenceEquals(sender, Button3))
            {
                var canvas = FindParentCanvas(Button3);
                if (canvas == null) return;

                _dragCanvas = canvas;
                _draggingElement = Button3;
                _button3DownPoint = e.GetPosition(canvas);
                _button3StartLeft = Canvas.GetLeft(Button3);
                if (double.IsNaN(_button3StartLeft)) _button3StartLeft = 0;
                _button3StartTop = Canvas.GetTop(Button3);
                if (double.IsNaN(_button3StartTop)) _button3StartTop = 0;

                _button3WasDragged = false;
                _button3DragPending = true;
                _button3DragInitiated = false;
            }
        }

        // 按钮拖拽移动事件处理程序
        private void Button_PreviewMouseMove(object sender, MouseEventArgs e)
        {
            // 配置模式
            if (_isLayoutEditMode)
            {
                if (_draggingElement == null || _dragCanvas == null) return;
                if (e.LeftButton != MouseButtonState.Pressed) return;

                var pos = e.GetPosition(_dragCanvas);
                var delta = pos - _dragStartPoint;

                var fe = (FrameworkElement)_draggingElement;
                double canvasW = _dragCanvas.ActualWidth > 0 ? _dragCanvas.ActualWidth : this.ActualWidth;
                double canvasH = _dragCanvas.ActualHeight > 0 ? _dragCanvas.ActualHeight : this.ActualHeight;
                double maxLeft = Math.Max(0, canvasW - fe.ActualWidth);
                double maxTop = Math.Max(0, canvasH - fe.ActualHeight);

                double newLeft = Clamp(_dragStartLeft + delta.X, 0, maxLeft);
                double newTop = Clamp(_dragStartTop + delta.Y, 0, maxTop);

                // Button3 按模式拖拽
                if (ReferenceEquals(_draggingElement, Button3))
                {
                    int mode = PositionSettings.Current.Button3Mode;
                    switch (mode)
                    {
                        case 1: // 贴右
                            fe.SetCurrentValue(Canvas.LeftProperty, maxLeft);
                            fe.SetCurrentValue(Canvas.TopProperty, newTop);
                            break;
                        case 2: // 贴左
                            fe.SetCurrentValue(Canvas.LeftProperty, 0.0);
                            fe.SetCurrentValue(Canvas.TopProperty, newTop);
                            break;
                        default: // 自由
                            fe.SetCurrentValue(Canvas.LeftProperty, newLeft);
                            fe.SetCurrentValue(Canvas.TopProperty, newTop);
                            break;
                    }
                    e.Handled = true;
                        return;
                }

                // 默认更新被拖拽元素的位置
                fe.SetCurrentValue(Canvas.LeftProperty, newLeft);
                fe.SetCurrentValue(Canvas.TopProperty, newTop);

                // 组同步逻辑
                if (ReferenceEquals(_draggingElement, Button1) || ReferenceEquals(_draggingElement, Button2))
                {
                    Button1.SetCurrentValue(Canvas.TopProperty, newTop);
                    Button2.SetCurrentValue(Canvas.TopProperty, newTop);
                }
                else if (IsButtons4To9(_draggingElement))
                {
                    foreach (var b in new[] { Button4, Button5, Button6, Button7, Button8, Button9 })
                        b.SetCurrentValue(Canvas.LeftProperty, newLeft);
                }
                e.Handled = true;
            }

            // Button3
            if (!ReferenceEquals(sender, Button3)) return;
            if (!_button3DragPending || _dragCanvas == null) return;
            if (e.LeftButton != MouseButtonState.Pressed) return;

            var pos2 = e.GetPosition(_dragCanvas);

            // 进入拖动的阈值判
            if (!_button3DragInitiated)
            {
                double dx = Math.Abs(pos2.X - _button3DownPoint.X);
                double dy = Math.Abs(pos2.Y - _button3DownPoint.Y);
                if (dx < SystemParameters.MinimumHorizontalDragDistance &&
                    dy < SystemParameters.MinimumVerticalDragDistance)
                {
                    return; // 未进入正式拖动
                }

                // 开始拖动
                _button3DragInitiated = true;
                _button3WasDragged = true;
                Button3.CaptureMouse();
            }

            // 正式拖动：按各模式限制
            var delta2 = pos2 - _button3DownPoint;

            double canvasW2 = _dragCanvas.ActualWidth > 0 ? _dragCanvas.ActualWidth : this.ActualWidth;
            double canvasH2 = _dragCanvas.ActualHeight > 0 ? _dragCanvas.ActualHeight : this.ActualHeight;

            // Button3 实际宽高
            double h = GetSize12Scaled();
            int modeNow = PositionSettings.Current.Button3Mode;
            double w = (modeNow == 0) ? h : GetSize24Scaled();

            double maxLeft2 = Math.Max(0, canvasW2 - w);
            double maxTop2 = Math.Max(0, canvasH2 - h);

            double newLeft2 = Clamp(_button3StartLeft + delta2.X, 0, maxLeft2);
            double newTop2 = Clamp(_button3StartTop + delta2.Y, 0, maxTop2);

            switch (modeNow)
            {
                case 1: // 贴右
                    Button3.SetCurrentValue(Canvas.LeftProperty, maxLeft2);
                    Button3.SetCurrentValue(Canvas.TopProperty, newTop2);
                    break;
                case 2: // 贴左
                    Button3.SetCurrentValue(Canvas.LeftProperty, 0.0);
                    Button3.SetCurrentValue(Canvas.TopProperty, newTop2);
                    break;
                default: // 自由
                    Button3.SetCurrentValue(Canvas.LeftProperty, newLeft2);
                    Button3.SetCurrentValue(Canvas.TopProperty, newTop2);
                    break;
            }
            e.Handled = true;
        }

        // 按钮拖拽释放事件处理程序
        private void Button_PreviewMouseLeftButtonUp(object sender, RoutedEventArgs e)
        {
            if (_isLayoutEditMode)
            {
                // 配置模式
                if (_draggingElement != null)
                {
                    if (ReferenceEquals(_draggingElement, Button3) && _dragCanvas != null)
                    {
                        var fe = (FrameworkElement)_draggingElement;
                        double canvasW = _dragCanvas.ActualWidth > 0 ? _dragCanvas.ActualWidth : this.ActualWidth;
                        double canvasH = _dragCanvas.ActualHeight > 0 ? _dragCanvas.ActualHeight : this.ActualHeight;
                        double maxLeft = Math.Max(0, canvasW - fe.ActualWidth);
                        double maxTop = Math.Max(0, canvasH - fe.ActualHeight);

                        double left = Canvas.GetLeft(fe);
                        double top = Canvas.GetTop(fe);
                        if (double.IsNaN(left)) left = 0;
                        if (double.IsNaN(top)) top = 0;

                        top = Clamp(top, 0, maxTop);

                        int mode = PositionSettings.Current.Button3Mode;
                        switch (mode)
                        {
                            case 1: // 贴右
                                left = maxLeft;
                                break;
                            case 2: // 贴左
                                left = 0.0;
                                break;
                            default: // 自由
                                left = Clamp(left, 0, maxLeft);
                                break;
                        }

                        fe.SetCurrentValue(Canvas.LeftProperty, left);
                        fe.SetCurrentValue(Canvas.TopProperty, top);
                    }

                    _draggingElement.ReleaseMouseCapture();
                    _draggingElement = null;
                    _dragCanvas = null;
                    e.Handled = true;

                    // 通知配置窗口位置已改动
                    if (_configWindow != null)
                    {
                        _configWindow.MarkPositionsDirty();
                    }
                }
                return;
            }

            // Button3
            if (!ReferenceEquals(sender, Button3)) return;
            if (!_button3DragPending) return;

            if (_button3DragInitiated)
            {
                // 已发生拖动
                Button3.ReleaseMouseCapture();

                double left = Canvas.GetLeft(Button3);
                double top = Canvas.GetTop(Button3);
                if (double.IsNaN(left)) left = 0;
                if (double.IsNaN(top)) top = 0;

                // 再次按模式校正 Left
                double canvasW = _dragCanvas?.ActualWidth > 0 ? _dragCanvas!.ActualWidth : this.ActualWidth;
                double canvasH = _dragCanvas?.ActualHeight > 0 ? _dragCanvas!.ActualHeight : this.ActualHeight;

                double h = GetSize12Scaled();
                int modeNow = PositionSettings.Current.Button3Mode;
                double w = (modeNow == 0) ? h : GetSize24Scaled();

                double maxLeft = Math.Max(0, canvasW - w);
                double maxTop = Math.Max(0, canvasH - h);

                top = Clamp(top, 0, maxTop);
                if (modeNow == 1) left = maxLeft;
                else if (modeNow == 2) left = 0.0;
                else left = Clamp(left, 0, maxLeft);

                Button3.SetCurrentValue(Canvas.LeftProperty, left);
                Button3.SetCurrentValue(Canvas.TopProperty, top);

                // 保存到配置
                SaveButton3RatiosByMode(left, top);

                // 抑制点击
                _button3WasDragged = true;
                e.Handled = true;
            }

            // 清理状态
            _button3DragPending = false;
            _button3DragInitiated = false;
        }

        private static Canvas? FindParentCanvas(DependencyObject d)
        {
            var cur = d;
            while (cur != null)
            {
                if (cur is Canvas c) return c;
                cur = VisualTreeHelper.GetParent(cur);
            }
            return null;
        }

        private static double Clamp(double value, double min, double max)
            => value < min ? min : (value > max ? max : value);

        // 判断是否为按钮4到9之一
        private bool IsButtons4To9(UIElement el)
            => ReferenceEquals(el, Button4) || ReferenceEquals(el, Button5) ||
               ReferenceEquals(el, Button6) || ReferenceEquals(el, Button7) ||
               ReferenceEquals(el, Button8) || ReferenceEquals(el, Button9);

        // 导入Windows API用于模拟键盘输入
        [DllImport("user32.dll", SetLastError = true)]
        private static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);

        // 虚拟键码定义
        private const byte VK_LWIN = 0x5B;    // 左Win键
        private const byte VK_CONTROL = 0x11; // Ctrl键
        private const byte VK_LEFT = 0x25;    // 左箭头
        private const byte VK_RIGHT = 0x27;   // 右箭头
        private const byte VK_D = 0x44;      // D键
        private const byte VK_F4 = 0x73;     // F4键
        private const byte VK_TAB = 0x09;   // Tab键

        private const uint KEYEVENTF_KEYDOWN = 0x0000; // 按键按下
        private const uint KEYEVENTF_KEYUP = 0x0002;   // 按键释放

        // 为按钮添加淡出并折叠动画
        private Task FadeOutAndCollapse(Button button)
        {
            if (button.Visibility != Visibility.Visible)
            {
                button.Visibility = Visibility.Collapsed;
                return Task.CompletedTask;
            }

            var tcs = new TaskCompletionSource<bool>();
            var storyboard = ((Storyboard)FindResource("FadeOutAnimation")).Clone();

            // 关键：让动画从“当前不透明度”开始
            foreach (var tl in storyboard.Children)
            {
                if (tl is DoubleAnimation da)
                {
                    da.From = button.Opacity;
                    da.To = 0.0;
                }
            }

            EventHandler? completedHandler = null;
            completedHandler = (s, e) =>
            {
                storyboard.Completed -= completedHandler;
                button.Visibility = Visibility.Collapsed;
                tcs.TrySetResult(true);
            };

            Storyboard.SetTarget(storyboard, button);
            storyboard.Completed += completedHandler;
            storyboard.Begin();

            return tcs.Task;
        }

        // 为按钮添加缩小动画
        private void AddShrinkAnimation(Storyboard storyboard, Button button, TimeSpan duration)
        {
            var scaleXAnim = new DoubleAnimation(1, 0, duration);
            var scaleYAnim = new DoubleAnimation(1, 0, duration);

            // 绑定到按钮的缩放变换属性
            Storyboard.SetTarget(scaleXAnim, button);
            Storyboard.SetTarget(scaleYAnim, button);
            Storyboard.SetTargetProperty(scaleXAnim, new PropertyPath("RenderTransform.ScaleX"));
            Storyboard.SetTargetProperty(scaleYAnim, new PropertyPath("RenderTransform.ScaleY"));

            storyboard.Children.Add(scaleXAnim);
            storyboard.Children.Add(scaleYAnim);
        }

        // 重置并显示按钮
        private void ResetAndShowButton(Button button)
        {
            button.BeginAnimation(UIElement.OpacityProperty, null);

            if (button.RenderTransform is ScaleTransform st)
            {
                if (st.IsFrozen) button.RenderTransform = new ScaleTransform(1, 1);
                else
                {
                    st.BeginAnimation(ScaleTransform.ScaleXProperty, null);
                    st.BeginAnimation(ScaleTransform.ScaleYProperty, null);
                    st.ScaleX = 1; st.ScaleY = 1;
                }
            }
            else button.RenderTransform = new ScaleTransform(1, 1);

            bool isButtons1To3 = ReferenceEquals(button, Button1) || ReferenceEquals(button, Button2) || ReferenceEquals(button, Button3);
            bool isButtons4To9 = ReferenceEquals(button, Button4) || ReferenceEquals(button, Button5) ||
                                 ReferenceEquals(button, Button6) || ReferenceEquals(button, Button7) ||
                                 ReferenceEquals(button, Button8) || ReferenceEquals(button, Button9);

            double targetOpacity =
                isButtons1To3 ? PositionSettings.Current.Buttons1To3Opacity :
                isButtons4To9 ? PositionSettings.Current.Buttons4To9Opacity : 1.0;

            button.SetCurrentValue(UIElement.OpacityProperty, targetOpacity);
            button.Visibility = Visibility.Visible;
            button.UpdateLayout();
        }

        // 切换虚拟桌面的通用方法
        private async Task SwitchVirtualDesktop(byte directionKey)
        {
            // 按下Win键
            keybd_event(VK_LWIN, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            // 按下Ctrl键
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            // 按下方向键（左/右）
            keybd_event(directionKey, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);

            // 短暂延迟
            await Task.Delay(50);

            // 释放方向键
            keybd_event(directionKey, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            // 释放Ctrl键
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            // 释放Win键
            keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);

            // 刷新按钮状态
            await Task.Delay(150);
            UpdateButton1VisibilityByDesktop();
        }

        // 按钮1点击事件：向左切换虚拟桌面（Win+Ctrl+左箭头）
        private async void HandleButton1Click(object sender, RoutedEventArgs e)
        {
            if (IgnoreIfEditMode(e)) return;
            // 若按钮4-9当前可见，收起
            if (Button4.Visibility == Visibility.Visible)
            {
                await HideButtons4To9Core();
            }
            else
            {
                await RunPreSwitchKeysWithMinimizeAsync();
                await SwitchVirtualDesktop(VK_LEFT);
                MaybeAutoMuteAfterVDChange();
                MaybeAutoTurnOffScreen();
                TriggerButtons12PostAction();
            }
        }

        // 按钮2点击事件：向右切换虚拟桌面（Win+Ctrl+右箭头）
        private async void HandleButton2Click(object sender, RoutedEventArgs e)
        {
            if (IgnoreIfEditMode(e)) return;
            // 若按钮4-9当前可见，收起
            if (Button4.Visibility == Visibility.Visible)
            {
                await HideButtons4To9Core();
                return;
            }
            // 计算是否处于最后一个桌面
            var all = GetAllVirtualDesktopIdsFromRegistry();
            int currentIndex = GetCurrentVirtualDesktopIndexOrDefault(1);
            bool isLast = all.Count > 0 && currentIndex >= all.Count;

            await RunPreSwitchKeysWithMinimizeAsync();
            if (isLast)
                await CreateNewVirtualDesktopAsync();
            else
                await SwitchVirtualDesktop(VK_RIGHT);
            MaybeAutoMuteAfterVDChange();
            MaybeAutoTurnOffScreen();
            TriggerButtons12PostAction();
        }

        // 通用的新建虚拟桌面方法（Win+Ctrl+D）
        private async Task CreateNewVirtualDesktopAsync()
        {
            keybd_event(VK_LWIN, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            keybd_event(VK_D, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);

            await Task.Delay(50);

            keybd_event(VK_D, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);

            // 刷新可见性
            await Task.Delay(200);
            UpdateButton1VisibilityByDesktop();
        }

        // 右键点击按钮1/2时显示按钮4-9
        private void ShowButtons_MouseRightButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (_isLayoutEditMode)
            {
                e.Handled = true;
                return;
            }

            ResetAndShowButton(Button4);
            ResetAndShowButton(Button5);
            ResetAndShowButton(Button6);
            ResetAndShowButton(Button7);
            ResetAndShowButton(Button8);
            ResetAndShowButton(Button9);

            e.Handled = true;
        }

        // 按钮4-9核心逻辑方法
        private async Task HideButtons4To9Core()
        {
            await Task.WhenAll(
                FadeOutAndCollapse(Button4),
                FadeOutAndCollapse(Button5),
                FadeOutAndCollapse(Button6),
                FadeOutAndCollapse(Button7),
                FadeOutAndCollapse(Button8),
                FadeOutAndCollapse(Button9)
            );
        }

        // 按钮4-9事件处理程序
        private async void HideButtons4To9(object sender, RoutedEventArgs e)
        {
            if (IgnoreIfEditMode(e)) return;
            await HideButtons4To9Core(); 
        }

        

        // 计算 Button3 尺寸相关基数（与 XAML 转换器保持一致）
        private static double GetSize12Scaled() =>
            (SystemParameters.PrimaryScreenHeight / 12.0) * Math.Max(0.01, PositionSettings.Current.Buttons1To3Scale);
        private static double GetSize24Scaled() =>
            (SystemParameters.PrimaryScreenHeight / 24.0) * Math.Max(0.01, PositionSettings.Current.Buttons1To3Scale);

        // 保存 Button3 的位置到配置（按模式落到对应的 Ratio 字段）
        private void SaveButton3RatiosByMode(double left, double top)
        {
            double screenW = SystemParameters.PrimaryScreenWidth;
            double screenH = SystemParameters.PrimaryScreenHeight;

            // Button3 高度与自由模式宽度 = H/12*scale
            double size12 = GetSize12Scaled();

            var cfg = PositionSettings.Current;
            int mode = cfg.Button3Mode;

            // 将像素位置转换为中心点比例
            double centerX = (left + size12 / 2.0) / screenW;
            double centerY = (top + size12 / 2.0) / screenH;
            static double Clamp01(double v) => v < 0 ? 0 : (v > 1 ? 1 : v);

            centerX = Clamp01(centerX);
            centerY = Clamp01(centerY);

            if (mode == 0)
            {
                // 自由模式：保存左右、上下
                cfg.Button3LeftRatio_Free = centerX;
                cfg.Button3TopRatio_Free = centerY;
            }
            else if (mode == 1)
            {
                // 贴右：仅保存纵向比例
                cfg.Button3TopRatio_RightEdge = centerY;
            }
            else if (mode == 2)
            {
                // 贴左：仅保存纵向比例
                cfg.Button3TopRatio_LeftEdge = centerY;
            }

            PositionSettings.Save();
            // 由于配置对象不发通知，强制刷新绑定重新计算
            ForceReapplyPositionBindings();
        }

       

        

        

        // 按钮3点击事件
        private async void HandleButton3Click(object sender, RoutedEventArgs e)
        {
            if (_button3WasDragged)
            {
                _button3WasDragged = false;
                e.Handled = true;
                return;
            }

            if (IgnoreIfEditMode(e))  return;

            // 按钮3渐隐后显示按钮1和2
            await FadeOutAndCollapse(Button3);

            ResetAndShowButton(Button1);
            ResetAndShowButton(Button2);

            // 淡入到配置的不透明度
            double toOpacity = PositionSettings.Current.Buttons1To3Opacity;
            Button1.Opacity = 0;
            Button2.Opacity = 0;
            var fadeInStoryboard = new Storyboard();
            var fadeIn1 = new DoubleAnimation(0, toOpacity, TimeSpan.FromSeconds(0.2));
            var fadeIn2 = new DoubleAnimation(0, toOpacity, TimeSpan.FromSeconds(0.2));
            Storyboard.SetTarget(fadeIn1, Button1);
            Storyboard.SetTarget(fadeIn2, Button2);
            Storyboard.SetTargetProperty(fadeIn1, new PropertyPath("Opacity"));
            Storyboard.SetTargetProperty(fadeIn2, new PropertyPath("Opacity"));
            fadeInStoryboard.Children.Add(fadeIn1);
            fadeInStoryboard.Children.Add(fadeIn2);
            fadeInStoryboard.Begin();

            UpdateButton1VisibilityByDesktop();
        }

        // 按钮4点击事件（退出）
        private async void HandleButton4Click(object sender, RoutedEventArgs e)
        {
            if (IgnoreIfEditMode(e)) return;

            await HideButtons4To9Core();
            this.Close();
        }


        // 按钮5点击事件（隐藏）
        private async void HandleButton5Click(object sender, RoutedEventArgs e)
        {
            if (IgnoreIfEditMode(e)) return;

            await HideButtons4To9Core();

            var shrinkStoryboard = new Storyboard();
            var animationDuration = TimeSpan.FromSeconds(0.15);
            if (Button1.Visibility == Visibility.Visible)
                AddShrinkAnimation(shrinkStoryboard, Button1, animationDuration);
            AddShrinkAnimation(shrinkStoryboard, Button2, animationDuration);

            var shrinkTcs = new TaskCompletionSource<bool>();
            shrinkStoryboard.Completed += (s, _) => shrinkTcs.TrySetResult(true);
            shrinkStoryboard.Begin();

            var tasks = new List<Task> { shrinkTcs.Task, FadeOutAndCollapse(Button2) };
            if (Button1.Visibility == Visibility.Visible)
                tasks.Add(FadeOutAndCollapse(Button1));

            await Task.WhenAll(tasks);

            // 显示按钮3：淡入到配置的不透明度
            double toOpacity = PositionSettings.Current.Buttons1To3Opacity;
            Button3.Opacity = 0;
            Button3.Visibility = Visibility.Visible;
            var fadeInStoryboard = new Storyboard();
            var fadeIn = new DoubleAnimation(0, toOpacity, TimeSpan.FromSeconds(0.2));
            Storyboard.SetTarget(fadeIn, Button3);
            Storyboard.SetTargetProperty(fadeIn, new PropertyPath("Opacity"));
            fadeInStoryboard.Children.Add(fadeIn);
            fadeInStoryboard.Begin();
        }

        // 按钮6点击事件：关闭当前虚拟桌面（Win+Ctrl+F4）
        private async void HandleButton6Click(object sender, RoutedEventArgs e)
        {
            if (IgnoreIfEditMode(e)) return;
            // 隐藏按钮4-9
            await HideButtons4To9Core();
            // 模拟Win+Ctrl+F4快捷键
            keybd_event(VK_LWIN, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            keybd_event(VK_F4, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            await Task.Delay(50);
            keybd_event(VK_F4, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            await Task.Delay(150);
            UpdateButton1VisibilityByDesktop();
        }

        // 按钮7点击事件：新建虚拟桌面（Win+Ctrl+D）
        private async void HandleButton7Click(object sender, RoutedEventArgs e)
        {
            if (IgnoreIfEditMode(e)) return;
            await HideButtons4To9Core();
            await CreateNewVirtualDesktopAsync();
        }

        // 按钮8点击事件：Win+Tab打开任务视图
        private async void HandleButton8Click(object sender, RoutedEventArgs e)
        {
            if (IgnoreIfEditMode(e)) return;
            await HideButtons4To9Core();

            // 模拟Win+Tab快捷键
            keybd_event(VK_LWIN, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            keybd_event(VK_TAB, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            await Task.Delay(50);
            keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
        }

        // 按钮9点击事件：进入配置模式
        private async void HandleButton9Click(object sender, RoutedEventArgs e)
        {
            // 进入布局编辑模式
            EnterLayoutEditMode();

            // 打开配置窗口
            if (_configWindow == null || !_configWindow.IsVisible)
            {
                _configWindow = new ConfigWindow
                {
                    Owner = this,
                    WindowStartupLocation = WindowStartupLocation.CenterOwner
                };
                _configWindow.Closed += (_, __) =>
                {
                    _configWindow = null;
                    ExitLayoutEditMode();
                };
                _configWindow.Show();
            }
            else
            {
                _configWindow.Activate();
            }

            await Task.CompletedTask;
        }

        // 确保窗口覆盖整个屏幕
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            // 置顶并覆盖整个主屏幕
            this.Left = 0;
            this.Top = 0;
            this.Width = SystemParameters.PrimaryScreenWidth;
            this.Height = SystemParameters.PrimaryScreenHeight;
            this.Topmost = true;
            this.WindowStyle = WindowStyle.None;
            this.ResizeMode = ResizeMode.NoResize;

            // 安装窗口消息钩子以实现透明背景可穿透、控件可交互
            _hwndSource = (HwndSource)PresentationSource.FromVisual(this)!;
            _hwndSource.AddHook(WndProc);
            IntPtr hWnd = new WindowInteropHelper(this).Handle;

            // 修改扩展样式为工具窗口
            int exStyle = GetWindowLong(hWnd, GWL_EXSTYLE);
            exStyle &= ~WS_EX_APPWINDOW;
            exStyle |= WS_EX_TOOLWINDOW;
            SetWindowLong(hWnd, GWL_EXSTYLE, exStyle);

            // 为按钮挂载拖拽事件（编辑模式）
            AttachDragHandlers(Button1);
            AttachDragHandlers(Button2);
            AttachDragHandlers(Button3);
            AttachDragHandlers(Button4);
            AttachDragHandlers(Button5);
            AttachDragHandlers(Button6);
            AttachDragHandlers(Button7);
            AttachDragHandlers(Button8);
            AttachDragHandlers(Button9);

            // 窗口加载完成后检测虚拟桌面序号并更新按钮状态
            UpdateButton1VisibilityByDesktop();

            StartVirtualDesktopRegistryWatchers();
        }

        // 注册表监听器，用于检测虚拟桌面切换
        private void StartVirtualDesktopRegistryWatchers()
        {
            try
            {
                _vdGlobalWatcher = RegistryMonitor.TryCreateHKCU(@"Software\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops");
                if (_vdGlobalWatcher != null)
                    _vdGlobalWatcher.Changed += OnVirtualDesktopRegistryChanged;

                int sessionId = Process.GetCurrentProcess().SessionId;
                string sessionPath = $@"Software\Microsoft\Windows\CurrentVersion\Explorer\SessionInfo\{sessionId}\VirtualDesktops";
                _vdSessionWatcher = RegistryMonitor.TryCreateHKCU(sessionPath);
                if (_vdSessionWatcher != null)
                    _vdSessionWatcher.Changed += OnVirtualDesktopRegistryChanged;
            }
            catch { /* 安静失败，不影响主流程 */ }
        }

        // 注册表变更事件处理（虚拟桌面切换时触发）
        private void OnVirtualDesktopRegistryChanged()
        {
            // 防抖：合并突发的多次通知（0.12秒内仅刷新一次）
            var prev = Interlocked.Exchange(ref _vdDebounceCts, new CancellationTokenSource());
            prev?.Cancel();
            var token = _vdDebounceCts!.Token;

            _ = Task.Delay(120, token).ContinueWith(t =>
            {
                if (t.IsCanceled) return;
                Dispatcher.Invoke(UpdateButton1VisibilityByDesktop);
            }, TaskScheduler.Default);
        }

        // 清理资源
        protected override void OnClosed(EventArgs e)
        {
            base.OnClosed(e);
            _vdDebounceCts?.Cancel();
            _vdGlobalWatcher?.Dispose();
            _vdSessionWatcher?.Dispose();
        }

        // 窗口消息处理：实现透明背景穿透、控件可交互
        private IntPtr WndProc(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
        {
            if (msg == WM_NCHITTEST)
            {
                // lParam: low-order = x, high-order = y (screen coords, signed)
                int x = (short)(lParam.ToInt32() & 0xFFFF);
                int y = (short)((lParam.ToInt32() >> 16) & 0xFFFF);
                var screenPoint = new System.Windows.Point(x, y);
                // 转为 WPF 坐标，并在视觉树上进行命中测试
                var wpfPoint = this.PointFromScreen(screenPoint);
                var hit = VisualTreeHelper.HitTest(this, wpfPoint);

                // 如果未命中任何交互控件，则让事件穿透（返回 HTTRANSPARENT）
                if (hit == null || !IsInteractiveAncestor(hit.VisualHit))
                {
                    handled = true;
                    return new IntPtr(HTTRANSPARENT);
                }

                // 否则视为客户端区域（允许控件接收点击）
                handled = true;
                return new IntPtr(HTCLIENT);
            }

            return IntPtr.Zero;
        }

        // 判断命中元素或其祖先是否为可交互控件
        private bool IsInteractiveAncestor(DependencyObject? d)
        {
            while (d != null)
            {
                if (d is ButtonBase) return true;
                if (d is System.Windows.Controls.Control ctrl && ctrl.IsEnabled && ctrl.IsHitTestVisible)
                    return true;
                d = VisualTreeHelper.GetParent(d);
            }
            return false;
        }

        // 虚拟桌面检测
        private static Guid? TryParseGuidFromRegistryValue(object? value)
        {
            try
            {
                if (value is byte[] bytes && bytes.Length == 16)
                    return new Guid(bytes);
                if (value is string s && Guid.TryParse(s, out var g))
                    return g;
            }
            catch { }
            return null;
        }

        // 获取当前虚拟桌面ID
        private static Guid? GetCurrentVirtualDesktopIdFromRegistry()
        {
            try
            {
                // 优先从 SessionInfo\<SessionId>\VirtualDesktops 读取（较新系统常用）
                int sessionId = Process.GetCurrentProcess().SessionId;
                string sessionPath = $@"Software\Microsoft\Windows\CurrentVersion\Explorer\SessionInfo\{sessionId}\VirtualDesktops";
                using (var k = Registry.CurrentUser.OpenSubKey(sessionPath))
                {
                    var g =
                        TryParseGuidFromRegistryValue(k?.GetValue("CurrentVirtualDesktop")) ??
                        TryParseGuidFromRegistryValue(k?.GetValue("CurrentVirtualDesktopId")) ??
                        TryParseGuidFromRegistryValue(k?.GetValue("CurrentDesktop"));
                    if (g.HasValue) return g;
                }

                // 回退到全局 VirtualDesktops 键
                const string vdPath = @"Software\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops";
                using (var k = Registry.CurrentUser.OpenSubKey(vdPath))
                {
                    var g =
                        TryParseGuidFromRegistryValue(k?.GetValue("CurrentVirtualDesktop")) ??
                        TryParseGuidFromRegistryValue(k?.GetValue("CurrentVirtualDesktopId")) ??
                        TryParseGuidFromRegistryValue(k?.GetValue("LastActiveVirtualDesktop"));
                    return g;
                }
            }
            catch
            {
                return null;
            }
        }

        // 获取所有虚拟桌面ID列表
        private static List<Guid> GetAllVirtualDesktopIdsFromRegistry()
        {
            var result = new List<Guid>();
            try
            {
                const string vdPath = @"Software\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops";
                using (var k = Registry.CurrentUser.OpenSubKey(vdPath))
                {
                    if (k == null) return result;
                    var val = k.GetValue("VirtualDesktopIDs") ?? k.GetValue("VirtualDesktopIdList");
                    if (val is byte[] bytes && bytes.Length >= 16 && bytes.Length % 16 == 0)
                    {
                        for (int i = 0; i < bytes.Length; i += 16)
                        {
                            var buf = new byte[16];
                            Buffer.BlockCopy(bytes, i, buf, 0, 16);
                            result.Add(new Guid(buf));
                        }
                    }
                    // 某些系统可能是 REG_MULTI_SZ/REG_SZ，尝试解析
                    else if (val is string s)
                    {
                        foreach (var part in s.Split(new[] { ',', ';', ' ', '\t', '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                        {
                            if (Guid.TryParse(part, out var g)) result.Add(g);
                        }
                    }
                    else if (val is string[] arr)
                    {
                        foreach (var item in arr)
                        {
                            if (Guid.TryParse(item, out var g)) result.Add(g);
                        }
                    }
                }
            }
            catch
            {
                // 忽略读取失败
            }
            return result;
        }

        // 获取当前虚拟桌面序号（1-based），失败时返回默认值
        private int GetCurrentVirtualDesktopIndexOrDefault(int defaultIndex = 1)
        {
            var current = GetCurrentVirtualDesktopIdFromRegistry();
            var all = GetAllVirtualDesktopIdsFromRegistry();
            if (current.HasValue && all.Count > 0)
            {
                int idx = all.IndexOf(current.Value);
                if (idx >= 0) return idx + 1; // 转为 1-based
            }
            return defaultIndex;
        }

        // 根据当前虚拟桌面状态更新按钮1的可见性
        private void UpdateButton1VisibilityByDesktop()
        {
            // 编辑模式下强制显示按钮1，避免被正常逻辑隐藏
            if (_isLayoutEditMode)
            {
                Button1.Visibility = Visibility.Visible;
                return;
            }

            try
            {
                var all = GetAllVirtualDesktopIdsFromRegistry();
                int desktopIndex = 1;

                var current = GetCurrentVirtualDesktopIdFromRegistry();
                if (current.HasValue && all.Count > 0)
                {
                    int idx0 = all.IndexOf(current.Value);
                    if (idx0 >= 0) desktopIndex = idx0 + 1;
                }

                Button1.Visibility = desktopIndex <= 1 ? Visibility.Collapsed : Visibility.Visible;
                IsOnLastDesktop = all.Count > 0 && desktopIndex >= all.Count;
            }
            catch
            {
                // 读取失败时，保底不隐藏且认为不是最后一个
                Button1.Visibility = Visibility.Visible;
                IsOnLastDesktop = false;
            }
        }

        // 用于在编辑模式时为按钮绘制可见边框
        private readonly Dictionary<UIElement, Adorner> _layoutEditAdorners = new();

        // 显示编辑边框
        private void ShowEditAdorner(UIElement element, Brush brush, double thickness)
        {
            var layer = AdornerLayer.GetAdornerLayer(element);
            if (layer == null) return;

            if (_layoutEditAdorners.TryGetValue(element, out var exist))
            {
                if (exist is OutlineAdorner oa)
                {
                    oa.BorderBrush = brush;
                    oa.BorderThickness = thickness;
                    layer.Update();
                }
                return;
            }

            var adorner = new OutlineAdorner(element)
            {
                BorderBrush = brush,
                BorderThickness = thickness
            };
            layer.Add(adorner);
            _layoutEditAdorners[element] = adorner;
        }

        // 隐藏编辑边框
        private void HideEditAdorner(UIElement element)
        {
            if (!_layoutEditAdorners.TryGetValue(element, out var adorner)) return;
            var layer = AdornerLayer.GetAdornerLayer(element);
            layer?.Remove(adorner);
            _layoutEditAdorners.Remove(element);
        }

        // 内部 Adorner 类型
        private sealed class OutlineAdorner : Adorner
        {
            public Brush BorderBrush { get; set; } = Brushes.Magenta;
            public double BorderThickness { get; set; } = 0.01; // 原为 2.0

            public OutlineAdorner(UIElement adornedElement) : base(adornedElement)
            {
                IsHitTestVisible = false;
                SnapsToDevicePixels = true;
            }

            protected override void OnRender(DrawingContext dc)
            {
                var size = AdornedElement.RenderSize;
                if (size.Width <= 0 || size.Height <= 0) return;

                // 仍保留最小 0.1，避免过细不可见
                double t = Math.Max(0.01, BorderThickness);
                var rect = new Rect(0, 0, size.Width, size.Height);
                rect.Inflate(-t / 2, -t / 2);

                var pen = new Pen(BorderBrush, t) { LineJoin = PenLineJoin.Round };
                dc.DrawRectangle(null, pen, rect);
            }
        }

        // 强制让绑定从源重新计算一次（因为 PositionsConfig 没有通知）
        private void ForceReapplyPositionBindings()
        {
            void Update(FrameworkElement el, DependencyProperty dp)
            {
                var be = BindingOperations.GetBindingExpressionBase(el, dp);
                be?.UpdateTarget();
            }

            foreach (var btn in new FrameworkElement[] { Button1, Button2, Button3, Button4, Button5, Button6, Button7, Button8, Button9 })
            {
                Update(btn, Canvas.LeftProperty);
                Update(btn, Canvas.TopProperty);
            }

            // 1/2/3 尺寸
            Update(Button1, FrameworkElement.WidthProperty);
            Update(Button1, FrameworkElement.HeightProperty);
            Update(Button2, FrameworkElement.WidthProperty);
            Update(Button2, FrameworkElement.HeightProperty);
            Update(Button3, FrameworkElement.WidthProperty);
            Update(Button3, FrameworkElement.HeightProperty);

            // 4-9 尺寸
            foreach (var b in new[] { Button4, Button5, Button6, Button7, Button8, Button9 })
            {
                Update(b, FrameworkElement.WidthProperty);
                Update(b, FrameworkElement.HeightProperty);
            }

            // 不透明度
            Update(Button1, UIElement.OpacityProperty);
            Update(Button2, UIElement.OpacityProperty);
            Update(Button3, UIElement.OpacityProperty);
            foreach (var b in new[] { Button4, Button5, Button6, Button7, Button8, Button9 })
                Update(b, UIElement.OpacityProperty);

            // 重新应用 Button3 Style 触发器
            var style = Button3.Style;
            Button3.ClearValue(FrameworkElement.StyleProperty);
            Button3.Style = style;
        }

        // 保存当前拖拽后的可视位置为比例到配置文件
        private void ApplyEditedPositionsToSettingsAndSave()
        {
            double screenW = SystemParameters.PrimaryScreenWidth;
            double screenH = SystemParameters.PrimaryScreenHeight;

            double base12 = screenH / 12.0;
            double size12 = base12 * Math.Max(0.01, PositionSettings.Current.Buttons1To3Scale);

            double btnW49 = (screenW / 9.0) * Math.Max(0.01, PositionSettings.Current.Buttons4To9Scale);
            double btnH49 = (screenH / 20.0) * Math.Max(0.01, PositionSettings.Current.Buttons4To9Scale);

            static double Clamp01(double v) => v < 0 ? 0 : (v > 1 ? 1 : v);

            double L(FrameworkElement el) { var v = Canvas.GetLeft(el); return double.IsNaN(v) ? 0.0 : v; }
            double T(FrameworkElement el) { var v = Canvas.GetTop(el);  return double.IsNaN(v) ? 0.0 : v; }

            var cfg = PositionSettings.Current;

            cfg.Button1LeftRatio = Clamp01((L(Button1) + size12 / 2.0) / screenW);
            cfg.Button2LeftRatio = Clamp01((L(Button2) + size12 / 2.0) / screenW);
            cfg.Buttons12TopRatio = Clamp01((T(Button1) + size12 / 2.0) / screenH);

            int mode = cfg.Button3Mode;
            if (mode == 0)
            {
                cfg.Button3LeftRatio_Free = Clamp01((L(Button3) + size12 / 2.0) / screenW);
                cfg.Button3TopRatio_Free  = Clamp01((T(Button3) + size12 / 2.0) / screenH);
            }
            else if (mode == 1)
            {
                cfg.Button3TopRatio_RightEdge = Clamp01((T(Button3) + size12 / 2.0) / screenH);
            }
            else if (mode == 2)
            {
                cfg.Button3TopRatio_LeftEdge = Clamp01((T(Button3) + size12 / 2.0) / screenH);
            }

            cfg.Buttons4to9LeftRatio = Clamp01((L(Button4) + btnW49 / 2.0) / screenW);
            cfg.Button4TopRatio = Clamp01((T(Button4) + btnH49 / 2.0) / screenH);
            cfg.Button5TopRatio = Clamp01((T(Button5) + btnH49 / 2.0) / screenH);
            cfg.Button6TopRatio = Clamp01((T(Button6) + btnH49 / 2.0) / screenH);
            cfg.Button7TopRatio = Clamp01((T(Button7) + btnH49 / 2.0) / screenH);
            cfg.Button8TopRatio = Clamp01((T(Button8) + btnH49 / 2.0) / screenH);
            cfg.Button9TopRatio = Clamp01((T(Button9) + btnH49 / 2.0) / screenH);

            PositionSettings.Save();
        }

        // 恢复 UI
        private void RestoreUiAfterConfigClose()
        {
            // 隐藏扩展按钮
            Button4.Visibility = Visibility.Collapsed;
            Button5.Visibility = Visibility.Collapsed;
            Button6.Visibility = Visibility.Collapsed;
            Button7.Visibility = Visibility.Collapsed;
            Button8.Visibility = Visibility.Collapsed;
            Button9.Visibility = Visibility.Collapsed;

            // 恢复主按钮
            ResetAndShowButton(Button2);
            ResetAndShowButton(Button1);
            Button3.Visibility = Visibility.Collapsed;

            // 按桌面状态更新按钮1可见性
            UpdateButton1VisibilityByDesktop();
        }

        // 供 ConfigWindow 调用：取消
        public void CancelConfigAndRefresh()
        {
            ForceReapplyPositionBindings(); 
            RestoreUiAfterConfigClose();
        }

        // 供 ConfigWindow 调用：确定
        public void ConfirmConfigAndSaveAndRefresh()
        {
            ApplyEditedPositionsToSettingsAndSave(); 
            ForceReapplyPositionBindings();
            RestoreUiAfterConfigClose();
        }

        // 供 ConfigWindow 调用：复原
        public void RefreshFromSettingsAfterRestore()
        {
            ForceReapplyPositionBindings();
            RestoreUiAfterConfigClose();
        }

        // 按钮1/2切换后触发的后续操作
        private void TriggerButtons12PostAction()
        {
            switch (PositionSettings.Current.Buttons12PostAction)
            {
                case 1:
                    // 执行按钮5的隐藏操作（与点击按钮5一致）
                    HandleButton5Click(Button5, new RoutedEventArgs());
                    break;
                case 2:
                    // 执行按钮4的退出操作（与点击按钮4一致）
                    HandleButton4Click(Button4, new RoutedEventArgs());
                    break;
                default:
                    // 0：无特别操作
                    break;
            }
        }

        // 虚拟桌面注册表监听相关
        private RegistryMonitor? _vdGlobalWatcher;
        private RegistryMonitor? _vdSessionWatcher;
        private CancellationTokenSource? _vdDebounceCts;

        // 根据配置切换后自动静音
        private void MaybeAutoMuteAfterVDChange()
        {
            if (PositionSettings.Current.AutoMuteOnVDChange == 1)
            {
                // 放到线程池，避免阻塞UI
                _ = Task.Run(() => AudioHelper.TrySetMasterMute(true));
            }
        }

        // 根据配置切换后自动熄屏
        private void MaybeAutoTurnOffScreen()
        {
            if (PositionSettings.Current.AutoTurnOffScreen == 1)
            {
                // 放到线程池，避免阻塞UI
                _ = Task.Run(() => DisplayHelper.TurnOffDisplays());
            }
        }

        // 先最小化，再执行预按键，最后恢复
        private async Task RunPreSwitchKeysWithMinimizeAsync()
        {
            var cfg = PositionSettings.Current;
            bool hasAny =
                cfg.PreSwitchKey1.HasValue ||
                cfg.PreSwitchKey2.HasValue ||
                cfg.PreSwitchKey3.HasValue ||
                cfg.PreSwitchKey4.HasValue;

            if (!hasAny)
            {
                // 没有配置则不最小化，直接返回
                return;
            }

            var prevState = this.WindowState;
            bool prevTopmost = this.Topmost;

            try
            {
                // 先取消顶置，最小化，给系统一点时间切换前台窗口
                this.Topmost = false;
                this.WindowState = WindowState.Minimized;
                await Task.Delay(120);

                // 执行预按键序列
                await ExecutePreSwitchKeysAsync();
            }
            finally
            {
                // 恢复窗口状态与顶置
                this.WindowState = prevState;
                this.Topmost = prevTopmost;
            }
        }

        // 切换前执行配置的预按键（最多4个，按顺序）
        private async Task ExecutePreSwitchKeysAsync()
        {
            var cfg = PositionSettings.Current;
            var seq = new List<Key>(4);
            if (cfg.PreSwitchKey1.HasValue) seq.Add(cfg.PreSwitchKey1.Value);
            if (cfg.PreSwitchKey2.HasValue) seq.Add(cfg.PreSwitchKey2.Value);
            if (cfg.PreSwitchKey3.HasValue) seq.Add(cfg.PreSwitchKey3.Value);
            if (cfg.PreSwitchKey4.HasValue) seq.Add(cfg.PreSwitchKey4.Value);

            if (seq.Count == 0) return;

            bool any = false;

            // 小工具函数
            static byte VK(Key k) => (byte)KeyInterop.VirtualKeyFromKey(k);
            static void Down(byte vk) => keybd_event(vk, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            static void Up(byte vk) => keybd_event(vk, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);

            // 当前按下的粘滞修饰键集合
            var currentMods = new List<byte>();

            int i = 0;

            // 如果序列一开始就是修饰键：全部按下并保持
            while (i < seq.Count && IsModifierKey(seq[i]))
            {
                var vk = VK(seq[i]);
                if (!currentMods.Contains(vk)) { Down(vk); await Task.Delay(10); }
                currentMods.Add(vk);
                i++;
            }

            // 依次处理剩余按键；遇到修饰键表示切换修饰集合；非修饰键在当前修饰集合下点按
            while (i < seq.Count)
            {
                var k = seq[i];

                if (IsModifierKey(k))
                {
                    // 收集连续的一组新修饰键
                    var newMods = new List<byte>();
                    int j = i;
                    while (j < seq.Count && IsModifierKey(seq[j]))
                    {
                        var vk = VK(seq[j]);
                        if (!newMods.Contains(vk)) newMods.Add(vk);
                        j++;
                    }

                    // 释放旧集合中不需要的
                    for (int m = currentMods.Count - 1; m >= 0; m--)
                    {
                        if (!newMods.Contains(currentMods[m]))
                        {
                            await Task.Delay(10);
                            Up(currentMods[m]);
                            currentMods.RemoveAt(m);
                        }
                    }
                    // 按下新集合中新增的
                    foreach (var vk in newMods)
                    {
                        if (!currentMods.Contains(vk))
                        {
                            Down(vk);
                            await Task.Delay(10);
                            currentMods.Add(vk);
                        }
                    }

                    i = j; // 继续处理后面的键
                    continue;
                }

                // 非修饰键：在当前修饰集合下点按一次
                var mainVk = VK(k);
                Down(mainVk);
                await Task.Delay(30);
                Up(mainVk);
                any = true;

                await Task.Delay(40);
                i++;
            }

            // 释放仍然按着的修饰键
            for (int m = currentMods.Count - 1; m >= 0; m--)
            {
                await Task.Delay(10);
                Up(currentMods[m]);
            }

            if (any)
                await Task.Delay(80);
        }

        // 判断是否为修饰键
        private static bool IsModifierKey(Key k) =>
            k == Key.LeftCtrl || k == Key.RightCtrl ||
            k == Key.LeftShift || k == Key.RightShift ||
            k == Key.LeftAlt || k == Key.RightAlt ||
            k == Key.LWin || k == Key.RWin;
    }
}