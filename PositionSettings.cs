using System;
using System.IO;
using System.Text.Json;
using System.Windows.Input;

namespace VD_Toggler_3
{
    public sealed class PositionsConfig
    {
        public double Button1LeftRatio { get; set; } = 0.87;
        public double Button2LeftRatio { get; set; } = 0.93;
        public double Buttons12TopRatio { get; set; } = 0.88;

        // 0=自由，1=贴右，2=贴左
        public int Button3Mode { get; set; } = 1;

        // 按钮1/2后续动作：0=无；1=隐藏（按钮5）；2=退出（按钮4）
        public int Buttons12PostAction { get; set; } = 0;

        // 图形按钮整体缩放（0.2~3.0，默认1.0）
        public double Buttons1To3Scale { get; set; } = 1.0;

        // 图形按钮整体不透明度（0.1~1.0，默认1.0）
        public double Buttons1To3Opacity { get; set; } = 1.0;

        // Button3（分别记录左右贴边/自由）
        public double Button3TopRatio_LeftEdge { get; set; } = 0.88;
        public double Button3TopRatio_RightEdge { get; set; } = 0.88;
        public double Button3LeftRatio_Free { get; set; } = 0.90;
        public double Button3TopRatio_Free { get; set; } = 0.88;

        // 文字按钮整体缩放（0.2~3.0，默认1.0）
        public double Buttons4To9Scale { get; set; } = 1.0;

        // 文字按钮整体不透明度（0.1~1.0，默认1.0）
        public double Buttons4To9Opacity { get; set; } = 0.7;

        // 4-9
        public double Buttons4to9LeftRatio { get; set; } = 0.90;
        public double Button4TopRatio { get; set; } = 0.80;
        public double Button5TopRatio { get; set; } = 0.75;
        public double Button6TopRatio { get; set; } = 0.70;
        public double Button7TopRatio { get; set; } = 0.65;
        public double Button8TopRatio { get; set; } = 0.60;
        public double Button9TopRatio { get; set; } = 0.55;

        // 自动静音
        public int AutoMuteOnVDChange { get; set; } = 0;
        // 自动熄屏
        public int AutoTurnOffScreen { get; set; } = 0;
        // 切换前快捷键
        public Key? PreSwitchKey1 { get; set; }
        public Key? PreSwitchKey2 { get; set; }
        public Key? PreSwitchKey3 { get; set; }
        public Key? PreSwitchKey4 { get; set; }

    }

    // 配置管理
    public static class PositionSettings
    {
        private static readonly Lazy<PositionsConfig> _current = new Lazy<PositionsConfig>(Load);
        public static PositionsConfig Current => _current.Value;

        private static string ConfigPath =>
            Path.Combine(AppContext.BaseDirectory, "positions.json");

        private static PositionsConfig Load()
        {
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,
                ReadCommentHandling = JsonCommentHandling.Skip,
                AllowTrailingCommas = true,
                WriteIndented = true
            };

            if (File.Exists(ConfigPath))
            {
                try
                {
                    var json = File.ReadAllText(ConfigPath);
                    var data = JsonSerializer.Deserialize<PositionsConfig>(json, options);
                    if (data != null) return data;
                }
                catch { }
            }

            var defaults = new PositionsConfig();
            try
            {
                var json = JsonSerializer.Serialize(defaults, options);
                File.WriteAllText(ConfigPath, json);
            }
            catch { }
            return defaults;
        }

        // 保存当前配置到文件
        public static void Save()
        {
            var options = new JsonSerializerOptions { WriteIndented = true };
            var json = JsonSerializer.Serialize(Current, options);
            File.WriteAllText(ConfigPath, json);
        }

        // 生成当前配置的快照（深拷贝）
        public static PositionsConfig Snapshot() => new PositionsConfig
        {
            Button1LeftRatio = Current.Button1LeftRatio,
            Button2LeftRatio = Current.Button2LeftRatio,
            Buttons12TopRatio = Current.Buttons12TopRatio,
            Button3Mode = Current.Button3Mode,
            Buttons12PostAction = Current.Buttons12PostAction,
            Buttons1To3Scale = Current.Buttons1To3Scale,
            Buttons1To3Opacity = Current.Buttons1To3Opacity,
            Button3TopRatio_LeftEdge = Current.Button3TopRatio_LeftEdge,
            Button3TopRatio_RightEdge = Current.Button3TopRatio_RightEdge,
            Button3LeftRatio_Free = Current.Button3LeftRatio_Free,
            Button3TopRatio_Free = Current.Button3TopRatio_Free,
            Buttons4To9Scale = Current.Buttons4To9Scale,
            Buttons4To9Opacity = Current.Buttons4To9Opacity,
            Buttons4to9LeftRatio = Current.Buttons4to9LeftRatio,
            Button4TopRatio = Current.Button4TopRatio,
            Button5TopRatio = Current.Button5TopRatio,
            Button6TopRatio = Current.Button6TopRatio,
            Button7TopRatio = Current.Button7TopRatio,
            Button8TopRatio = Current.Button8TopRatio,
            Button9TopRatio = Current.Button9TopRatio,
            AutoMuteOnVDChange = Current.AutoMuteOnVDChange,
            AutoTurnOffScreen = Current.AutoTurnOffScreen,
            PreSwitchKey1 = Current.PreSwitchKey1,
            PreSwitchKey2 = Current.PreSwitchKey2,
            PreSwitchKey3 = Current.PreSwitchKey3,
            PreSwitchKey4 = Current.PreSwitchKey4
        };

        // 将快照值恢复到 Current（内存回滚）
        public static void Restore(PositionsConfig src)
        {
            if (src is null) return;
            var dst = Current;

            dst.Button1LeftRatio = src.Button1LeftRatio;
            dst.Button2LeftRatio = src.Button2LeftRatio;
            dst.Buttons12TopRatio = src.Buttons12TopRatio;

            dst.Button3Mode = src.Button3Mode;
            dst.Buttons12PostAction = src.Buttons12PostAction;
            dst.Buttons1To3Scale = src.Buttons1To3Scale;
            dst.Buttons1To3Opacity = src.Buttons1To3Opacity;

            dst.Button3TopRatio_LeftEdge = src.Button3TopRatio_LeftEdge;
            dst.Button3TopRatio_RightEdge = src.Button3TopRatio_RightEdge;
            dst.Button3LeftRatio_Free = src.Button3LeftRatio_Free;
            dst.Button3TopRatio_Free = src.Button3TopRatio_Free;

            dst.Buttons4To9Scale = src.Buttons4To9Scale;
            dst.Buttons4To9Opacity = src.Buttons4To9Opacity;

            dst.Buttons4to9LeftRatio = src.Buttons4to9LeftRatio;
            dst.Button4TopRatio = src.Button4TopRatio;
            dst.Button5TopRatio = src.Button5TopRatio;
            dst.Button6TopRatio = src.Button6TopRatio;
            dst.Button7TopRatio = src.Button7TopRatio;
            dst.Button8TopRatio = src.Button8TopRatio;
            dst.Button9TopRatio = src.Button9TopRatio;
            dst.AutoMuteOnVDChange = src.AutoMuteOnVDChange;
            dst.AutoTurnOffScreen = src.AutoTurnOffScreen;
            dst.PreSwitchKey1 = src.PreSwitchKey1;
            dst.PreSwitchKey2 = src.PreSwitchKey2;
            dst.PreSwitchKey3 = src.PreSwitchKey3;
            dst.PreSwitchKey4 = src.PreSwitchKey4;
        }
    }
}