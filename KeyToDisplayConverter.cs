using System;
using System.Globalization;
using System.Windows.Data;
using System.Windows.Input;

namespace VD_Toggler_3
{
    public sealed class KeyToDisplayConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is Key k)
            {
                // 友好显示
                switch (k)
                {
                    case Key.Return:    return "Enter(回车)";
                    case Key.Back:      return "Backspace(退格)";
                    case Key.Escape:    return "Esc(退出)";
                    case Key.Tab:       return "Tab(制表)";
                    case Key.CapsLock:  return "CapsLock(大写开关)";
                    case Key.Space:     return "Space(空格)";
                    case Key.Insert:    return "Insert(插入)";
                    case Key.Delete:    return "Delete(删除)";
                    case Key.PageUp:    return "PageUp(上翻)";
                    case Key.PageDown:  return "PageDown(下翻)";
                    case Key.PrintScreen:return "Prt Scr(截屏)";
                    case Key.Home:      return "Home(首页)";
                    case Key.End:       return "End(末尾)";
                    case Key.LeftCtrl:  return "Ctrl(左)";
                    case Key.RightCtrl: return "Ctrl(右)";
                    case Key.LeftShift: return "Shift(左)";
                    case Key.RightShift:return "Shift(右)";
                    case Key.LeftAlt:   return "Alt(左)";
                    case Key.RightAlt:  return "Alt(右)";
                    case Key.LWin:      return "Win(左)";
                    case Key.RWin:      return "Win(右)";
                    case Key.NumLock:   return "Numlk(小键盘开关)";
                    case Key.NumPad0:   return "0(小键盘)";
                    case Key.NumPad1:   return "1(小键盘)";
                    case Key.NumPad2:   return "2(小键盘)";
                    case Key.NumPad3:   return "3(小键盘)";
                    case Key.NumPad4:   return "4(小键盘)";
                    case Key.NumPad5:   return "5(小键盘)";
                    case Key.NumPad6:   return "6(小键盘)";
                    case Key.NumPad7:   return "7(小键盘)";
                    case Key.NumPad8:   return "8(小键盘)";
                    case Key.NumPad9:   return "9(小键盘)";
                    case Key.Divide:    return "/(小键盘)";
                    case Key.Multiply:  return "*(小键盘)";
                    case Key.Subtract:  return "-(小键盘)";
                    case Key.Add:       return "+(小键盘)";
                    case Key.Decimal:   return ".(小键盘)";
                    case Key.Left:      return "←(Left)";
                    case Key.Up:        return "↑(Up)";
                    case Key.Right:     return "→(Right)";
                    case Key.Down:      return "↓(Down)";
                    case Key.OemTilde:        return "` 【~】";
                    case Key.OemMinus:        return "- 【_】";
                    case Key.OemPlus:         return "=【+】";
                    case Key.OemOpenBrackets: return "[ 【{】";
                    case Key.OemCloseBrackets:return "] 【}】";
                    case Key.OemPipe:         return "\\ 【|】";
                    case Key.OemSemicolon:    return "; 【:】";
                    case Key.OemQuotes:       return "' 【\"】";
                    case Key.OemComma:        return ", 【<】";
                    case Key.OemPeriod:       return ". 【>】";
                    case Key.OemQuestion:     return "/ 【?】";
                    case Key.D0: return "0 【)】";
                    case Key.D1: return "1 【!】";
                    case Key.D2: return "2 【@】";
                    case Key.D3: return "3 【#】";
                    case Key.D4: return "4 【$】";
                    case Key.D5: return "5 【%】";
                    case Key.D6: return "6 【^】";
                    case Key.D7: return "7 【&】";
                    case Key.D8: return "8 【*】";
                    case Key.D9: return "9 【(】";
                }

                // 顶部数字键 D0-D9 -> 0-9
                if (k >= Key.D0 && k <= Key.D9)
                    return ((int)(k - Key.D0)).ToString();

                // 其它直接用名称
                return k.ToString();
            }
            return value?.ToString() ?? string.Empty;
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
            => Binding.DoNothing; // 仅用于显示，不需要反向转换
    }
}