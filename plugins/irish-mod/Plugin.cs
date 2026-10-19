using BepInEx;
using BepInEx.Logging;

namespace IrishMod
{
    [BepInPlugin(PluginInfo.PLUGIN_GUID, PluginInfo.PLUGIN_NAME, PluginInfo.PLUGIN_VERSION)]
    public class Plugin : BaseUnityPlugin
    {
        internal static ManualLogSource Log { get; private set; } = null!;

        private void Awake()
        {
            Log = Logger;
            Log.LogInfo($"{PluginInfo.PLUGIN_NAME} {PluginInfo.PLUGIN_VERSION} loaded.");
        }
    }

    internal static class PluginInfo
    {
        public const string PLUGIN_GUID = "com.dennehy95.valheim.irishmod";
        public const string PLUGIN_NAME = "Valheim Irish Mod";
        public const string PLUGIN_VERSION = "0.1.0";
    }
}
