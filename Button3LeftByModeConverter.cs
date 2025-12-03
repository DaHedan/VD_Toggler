using System;
using System.Globalization;
using System.Windows.Data;

namespace VD_Toggler_3
{
    // values[0]=screenW, values[1]=screenH, values[2]=mode, values[3]=freeLeftRatio, values[4](可选)=scale
    public class Button3LeftByModeConverter : IMultiValueConverter
    {
        private static double Clamp(double v, double min, double max) => v < min ? min : (v > max ? max : v);

        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            if (values.Length < 4) return 0.0;
            if (!double.TryParse(values[0]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double screenW)) return 0.0;
            if (!double.TryParse(values[1]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out double screenH)) return 0.0;

            int mode = 1;
            _ = int.TryParse(values[2]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out mode);

            double freeLeftRatio = 0.90;
            _ = double.TryParse(values[3]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out freeLeftRatio);

            double scale = 1.0;
            if (values.Length >= 5)
                _ = double.TryParse(values[4]?.ToString(), NumberStyles.Any, CultureInfo.InvariantCulture, out scale);

            if (mode == 1)
            {
                // 贴右：Left = screenW - width；width = (H/24)*scale
                double w = (screenH / 24.0) * scale;
                return Clamp(screenW - w, 0, Math.Max(0, screenW - w));
            }
            if (mode == 2)
            {
                // 贴左
                return 0.0;
            }

            // 自由：Left = screenW * ratio - (width/2)，width = (H/12)*scale
            double freeW = (screenH / 12.0) * scale;
            double left = screenW * freeLeftRatio - freeW / 2.0;
            return left < 0 ? 0.0 : left;
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
            => throw new NotImplementedException();
    }
}