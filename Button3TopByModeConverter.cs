using System;
using System.Globalization;
using System.Windows.Data;

namespace VD_Toggler_3
{
    // values[0]=screenW, values[1]=screenH, values[2]=mode,
    // values[3]=leftEdgeTopRatio, values[4]=rightEdgeTopRatio, values[5]=freeTopRatio, values[6]=scale
    public class Button3TopByModeConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            if (values.Length < 6) return 0.0;
            if (!double.TryParse(values[1]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double screenH))
                return 0.0;

            int mode = 1;
            _ = int.TryParse(values[2]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out mode);

            double leftEdge = 0.88, rightEdge = 0.88, freeTop = 0.88;
            _ = double.TryParse(values[3]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out leftEdge);
            _ = double.TryParse(values[4]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out rightEdge);
            _ = double.TryParse(values[5]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out freeTop);

            double scale = 1.0;
            if (values.Length >= 7)
                _ = double.TryParse(values[6]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out scale);

            double ratio = mode == 0 ? freeTop : (mode == 2 ? leftEdge : rightEdge);
            double height = (screenH / 12.0) * scale; // Button3 高度 = H/12 * scale
            double top = screenH * ratio - height / 2.0;
            return top < 0 ? 0.0 : top;
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}