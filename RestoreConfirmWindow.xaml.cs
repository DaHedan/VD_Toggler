using System.Windows;

namespace VD_Toggler_3
{
    public partial class RestoreConfirmWindow : Window
    {
        public RestoreConfirmWindow()
        {
            InitializeComponent();
        }

        private void OnConfirm(object sender, RoutedEventArgs e)
        {
            DialogResult = true;
            Close();
        }

        private void OnCancel(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}