using System.Windows;

namespace VD_Toggler_3
{
    public partial class CancelConfirmWindow : Window
    {
        public CancelConfirmWindow()
        {
            InitializeComponent();
        }

        private void OnExit(object sender, RoutedEventArgs e)
        {
            DialogResult = true;   // 选择退出
            Close();
        }

        private void OnKeepEditing(object sender, RoutedEventArgs e)
        {
            DialogResult = false;  // 继续编辑
            Close();
        }
    }
}