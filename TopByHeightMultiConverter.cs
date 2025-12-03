using System;
using System.Globalization;
using System.Windows.Data;

namespace VD_Toggler_3
{
    // MultiBinding版本：values[0]=screenHeight, values[1]=ratio
    // top = screenHeight * ratio - (buttonHeight / 2), buttonHeight = screenHeight / 20
    public class TopByHeightMultiConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            if (values == null || values.Length < 2) return 0.0;
            if (!double.TryParse(values[0]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double screenH))
                return 0.0;
            if (!double.TryParse(values[1]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double ratio))
                ratio = 0.0;

            double buttonHeight = screenH / 20.0;
            double top = screenH * ratio - buttonHeight / 2.0;
            return top < 0 ? 0.0 : top;
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}