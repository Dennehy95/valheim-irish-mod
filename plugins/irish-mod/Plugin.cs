using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;
using UnityEngine;

namespace IrishMod
{
    [BepInPlugin(PluginInfo.PLUGIN_GUID, PluginInfo.PLUGIN_NAME, PluginInfo.PLUGIN_VERSION)]
    public class Plugin : BaseUnityPlugin
    {
        internal static ManualLogSource Log { get; private set; } = null!;

        internal static IrishDisplayMode DisplayMode { get; private set; }

        private Harmony? _harmony;
        private ConfigEntry<KeyCode> _toggleKey = null!;
        private ConfigEntry<int> _displayModeOnStart = null!;

        private void Awake()
        {
            Log = Logger;

            _toggleKey = Config.Bind(
                "Display",
                "ToggleIrishKey",
                KeyCode.F8,
                "Key to cycle Irish display for wired keys: English only → Irish + [English] → Irish only.");

            _displayModeOnStart = Config.Bind(
                "Display",
                "IrishDisplayModeOnStart",
                (int)IrishDisplayMode.EnglishOnly,
                "Starting display mode: 0 = English only, 1 = Irish + [English], 2 = Irish only.");

            DisplayMode = NormalizeDisplayMode(_displayModeOnStart.Value);

            IrishTranslationCache.LoadFromPluginFolder(Log);

            _harmony = new Harmony(PluginInfo.PLUGIN_GUID);
            _harmony.PatchAll(typeof(Plugin).Assembly);

            Log.LogInfo(
                $"{PluginInfo.PLUGIN_NAME} {PluginInfo.PLUGIN_VERSION} loaded. Wired keys: {IrishTranslationCache.LoadedCount}. " +
                $"Display: {DescribeDisplayMode(DisplayMode)}. Cycle key: {_toggleKey.Value}.");
        }

        private void Update()
        {
            if (!Input.GetKeyDown(_toggleKey.Value))
                return;

            DisplayMode = (IrishDisplayMode)(((int)DisplayMode + 1) % 3);
            Log.LogInfo($"Irish display: {DescribeDisplayMode(DisplayMode)}.");

            TryRefreshScopedLocalization();
        }

        internal static string DescribeDisplayMode(IrishDisplayMode mode) =>
            mode switch
            {
                IrishDisplayMode.EnglishOnly => "English only (vanilla)",
                IrishDisplayMode.IrishLearner => "Irish + [English]",
                IrishDisplayMode.IrishOnly => "Irish only",
                _ => mode.ToString(),
            };

        private static IrishDisplayMode NormalizeDisplayMode(int raw)
        {
            if (raw < 0 || raw > 2)
            {
                Log.LogWarning($"IrishDisplayModeOnStart {raw} is out of range; using English only (0).");
                return IrishDisplayMode.EnglishOnly;
            }

            return (IrishDisplayMode)raw;
        }

        private static void TryRefreshScopedLocalization()
        {
            if (Localization.instance == null)
                return;

            var startup = UnityEngine.Object.FindObjectOfType<FejdStartup>();
            if (startup != null)
                Localization.instance.ReLocalizeAll(startup.transform);

            if (InventoryGui.instance != null)
                Localization.instance.ReLocalizeAll(InventoryGui.instance.transform);
        }

        private void OnDestroy()
        {
            _harmony?.UnpatchSelf();
        }
    }

    internal static class PluginInfo
    {
        public const string PLUGIN_GUID = "com.dennehy95.valheim.irishmod";
        public const string PLUGIN_NAME = "Valheim Irish Mod";
        public const string PLUGIN_VERSION = "1.0.0";
    }
}
