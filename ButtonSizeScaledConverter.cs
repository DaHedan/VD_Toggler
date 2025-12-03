using System;
using System.Globalization;
using System.Windows.Data;

namespace VD_Toggler_3
{
    // values[0]=screenHeight, values[1]=scale£»parameter=³ýÊý
    public sealed class ButtonSizeScaledConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            if (values is null || values.Length < 2) return 0.0;
            if (!double.TryParse(values[0]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double screenH)) return 0.0;
            double scale = 1.0;
            _ = double.TryParse(values[1]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out scale);
            double divisor = 1.0;
            if (parameter != null)
            {
                _ = double.TryParse(parameter.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out divisor);
                if (divisor == 0) divisor = 1.0;
            }
            return (screenH / divisor) * scale;
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}