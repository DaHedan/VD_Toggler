using System;
using System.Globalization;
using System.Windows.Data;

namespace VD_Toggler_3
{
    // values[0]=screenHeight, values[1]=mode(0/1/2), values[2]=scale
    public class Button3WidthConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            if (values.Length < 2) return 0.0;
            if (!double.TryParse(values[0]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double screenH))
                return 0.0;
            int mode = 1;
            _ = int.TryParse(values[1]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out mode);
            double scale = 1.0;
            if (values.Length >= 3)
                _ = double.TryParse(values[2]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out scale);

            // 0: 宽=高=H/12；1/2: 宽=H/24，然后乘以 scale
            double baseW = (mode == 0) ? (screenH / 12.0) : (screenH / 24.0);
            return baseW * scale;
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}