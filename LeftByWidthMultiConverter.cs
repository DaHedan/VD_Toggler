using System;
using System.Globalization;
using System.Windows.Data;

namespace VD_Toggler_3
{
    // MultiBinding版本：values[0]=screenWidth, values[1]=ratio
    // left = screenWidth * ratio - (buttonWidth / 2), buttonWidth = screenWidth / 9
    public class LeftByWidthMultiConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            if (values == null || values.Length < 2) return 0.0;
            if (!double.TryParse(values[0]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double screenW))
                return 0.0;
            if (!double.TryParse(values[1]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double ratio))
                ratio = 0.0;

            double buttonWidth = screenW / 9.0;
            double left = screenW * ratio - buttonWidth / 2.0;
            return left < 0 ? 0.0 : left;
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}