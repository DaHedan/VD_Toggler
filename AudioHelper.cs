using System;
using System.Runtime.InteropServices;

namespace VD_Toggler_3
{
    internal static class AudioHelper
    {
        // 尝试设置主音量静音状态，失败时返回 false
        public static bool TrySetMasterMute(bool mute)
        {
            try
            {
                SetMasterMute(mute);
                return true;
            }
            catch
            {
                return false;
            }
        }

        // 设置主音量静音状态，失败时抛出异常
        private static void SetMasterMute(bool mute)
        {
            IMMDeviceEnumerator? enumerator = null;
            IMMDevice? device = null;
            IAudioEndpointVolume? endpoint = null;

            try
            {
                enumerator = (IMMDeviceEnumerator)new MMDeviceEnumeratorComObject();
                Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender, ERole.eMultimedia, out device));

                Guid IID_IAudioEndpointVolume = new("5CDF2C82-841E-4546-9722-0CF74078229A");
                Marshal.ThrowExceptionForHR(device.Activate(ref IID_IAudioEndpointVolume, CLSCTX.CLSCTX_INPROC_SERVER, IntPtr.Zero, out endpoint));
                Marshal.ThrowExceptionForHR(endpoint.SetMute(mute, Guid.Empty));
            }
            finally
            {
                if (endpoint != null) Marshal.ReleaseComObject(endpoint);
                if (device != null) Marshal.ReleaseComObject(device);
                if (enumerator != null) Marshal.ReleaseComObject(enumerator);
            }
        }

        [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
        private class MMDeviceEnumeratorComObject { }

        private enum EDataFlow
        {
            eRender = 0,
            eCapture = 1,
            eAll = 2
        }

        private enum ERole
        {
            eConsole = 0,
            eMultimedia = 1,
            eCommunications = 2
        }

        [Flags]
        private enum CLSCTX : uint
        {
            CLSCTX_INPROC_SERVER = 0x1,
            CLSCTX_INPROC_HANDLER = 0x2,
            CLSCTX_LOCAL_SERVER = 0x4,
            CLSCTX_REMOTE_SERVER = 0x10,
            CLSCTX_ALL = CLSCTX_INPROC_SERVER | CLSCTX_INPROC_HANDLER | CLSCTX_LOCAL_SERVER | CLSCTX_REMOTE_SERVER
        }

        [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("A95664D2-9614-4F35-A746-DE8DB63617E6")]
        private interface IMMDeviceEnumerator
        {
            int EnumAudioEndpoints(EDataFlow dataFlow, uint dwStateMask, out object ppDevices);
            int GetDefaultAudioEndpoint(EDataFlow dataFlow, ERole role, out IMMDevice ppEndpoint);
            int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string pwstrId, out IMMDevice ppDevice);
            int RegisterEndpointNotificationCallback(IntPtr pClient);
            int UnregisterEndpointNotificationCallback(IntPtr pClient);
        }

        [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("D666063F-1587-4E43-81F1-B948E807363F")]
        private interface IMMDevice
        {
            int Activate(ref Guid iid, CLSCTX dwClsCtx, IntPtr pActivationParams, out IAudioEndpointVolume ppInterface);
            int OpenPropertyStore(int stgmAccess, out object ppProperties);
            int GetId([MarshalAs(UnmanagedType.LPWStr)] out string ppstrId);
            int GetState(out uint pdwState);
        }

        [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("5CDF2C82-841E-4546-9722-0CF74078229A")]
        private interface IAudioEndpointVolume
        {
            int RegisterControlChangeNotify(IntPtr pNotify);
            int UnregisterControlChangeNotify(IntPtr pNotify);
            int GetChannelCount(out uint pnChannelCount);
            int SetMasterVolumeLevel(float fLevelDB, Guid pguidEventContext);
            int SetMasterVolumeLevelScalar(float fLevel, Guid pguidEventContext);
            int GetMasterVolumeLevel(out float pfLevelDB);
            int GetMasterVolumeLevelScalar(out float pfLevel);
            int SetChannelVolumeLevel(uint nChannel, float fLevelDB, Guid pguidEventContext);
            int SetChannelVolumeLevelScalar(uint nChannel, float fLevel, Guid pguidEventContext);
            int GetChannelVolumeLevel(uint nChannel, out float pfLevelDB);
            int GetChannelVolumeLevelScalar(uint nChannel, out float pfLevel);
            int SetMute([MarshalAs(UnmanagedType.Bool)] bool bMute, Guid pguidEventContext);
            int GetMute(out bool pbMute);
        }
    }
}