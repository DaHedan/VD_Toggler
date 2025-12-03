using System;
using System.Globalization;
using System.Windows.Data;

namespace VD_Toggler_3
{
    // values[0]=screenW(未用), values[1]=screenH, values[2]=ratio, values[3](可选)=scale
    public class CenterTopConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            if (values == null || values.Length < 2) return 0.0;
            if (!double.TryParse(values[1]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double screenH)) return 0.0;

            double ratio = 0.0;
            if (values.Length >= 3)
                _ = double.TryParse(values[2]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out ratio);
            else if (parameter != null)
                _ = double.TryParse(parameter.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out ratio);

            double scale = 1.0;
            if (values.Length >= 4)
                _ = double.TryParse(values[3]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out scale);

            double size = (screenH / 12.0) * scale;
            double top = screenH * ratio - size / 2.0;
            return top < 0 ? 0.0 : top;
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}