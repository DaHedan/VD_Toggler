using System.Collections.Generic;
using System.Windows.Input;

namespace VD_Toggler_3
{
    public static class KeysProvider
    {
        public static IReadOnlyList<Key> AllKeys { get; } = Build();

        // 构建常用按键列表
        private static IReadOnlyList<Key> Build()
        {
            var list = new List<Key>();
            var seen = new HashSet<Key>();

            void Add(Key k)
            {
                if (seen.Add(k))
                    list.Add(k);
            }

            // 常用控制键
            var controlKeys = new[]
            {
                Key.Escape, Key.Tab, Key.CapsLock, Key.Return,
                Key.Space, Key.Back, Key.Insert, Key.Delete,
                Key.Left, Key.Up, Key.Right, Key.Down
            };
            foreach (var k in controlKeys) Add(k);

            // 修饰键
            var modifierKeys = new[]
            {
                Key.LeftCtrl, Key.RightCtrl,
                Key.LeftShift, Key.RightShift,
                Key.LeftAlt, Key.RightAlt,
                Key.LWin, Key.RWin
            };
            foreach (var k in modifierKeys) Add(k);

            // 字母 A-Z
            for (var k = Key.A; k <= Key.Z; k++) Add(k);

            // 顶部数字键 0-9
            for (var k = Key.D1; k <= Key.D9; k++) Add(k);
            Add(Key.D0);

            // 功能键 F1-F12
            for (var k = Key.F1; k <= Key.F12; k++) Add(k);

            // 导航键
            var navKeys = new[]
            {
                Key.Home, Key.End, Key.PageUp, Key.PageDown, Key.PrintScreen,
            };
            foreach (var k in navKeys) Add(k);

            // 小键盘
            Add(Key.NumLock);
            for (var k = Key.NumPad0; k <= Key.NumPad9; k++) Add(k);
            var numpadOps = new[]
            {
                Key.Divide, Key.Multiply, Key.Subtract, Key.Add, Key.Decimal,
            };
            foreach (var k in numpadOps) Add(k);

            // 其它常用符号键
            var otherKeys = new[]
            {
                Key.OemTilde, Key.OemMinus, Key.OemPlus, Key.OemOpenBrackets,
                Key.OemCloseBrackets, Key.OemPipe, Key.OemSemicolon, Key.OemQuotes,
                Key.OemComma, Key.OemPeriod, Key.OemQuestion
            };
            foreach (var k in otherKeys) Add(k);

            return list;
        }
    }
}