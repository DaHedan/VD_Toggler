using System;
using System.Globalization;
using System.Windows.Data;

namespace VD_Toggler_3
{
    public sealed class IntToBoolConverter : IValueConverter
    {
        // 将源（Button3Mode）与参数值比较，相等则返回 true，否则返回 false
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is IConvertible && parameter is IConvertible)
            {
                try
                {
                    int v = System.Convert.ToInt32(value, CultureInfo.InvariantCulture);
                    int p = System.Convert.ToInt32(parameter, CultureInfo.InvariantCulture);
                    return v == p;
                }
                catch { }
            }
            return false;
        }

        // 当 RadioButton 被选中时，返回其参数值写回到源（Button3Mode）
        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is bool b && b && parameter is IConvertible)
            {
                try
                {
                    return System.Convert.ToInt32(parameter, CultureInfo.InvariantCulture);
                }
                catch { }
            }
            return Binding.DoNothing;
        }
    }
}