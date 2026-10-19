using System;
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

        /// <summary>
        /// When true: scoped keys show Irish with [English]. When false: vanilla English for those keys.
        /// </summary>
        internal static bool IrishLearnerModeEnabled { get; private set; }

        private Harmony? _harmony;
        private ConfigEntry<KeyCode> _toggleKey = null!;
        private ConfigEntry<bool> _irishModeDefault = null!;

        private void Awake()
        {
            Log = Logger;

            _toggleKey = Config.Bind(
                "Display",
                "ToggleIrishKey",
                KeyCode.F7,
                "Key to toggle Irish learner display (Irish + [English]) vs vanilla English for wired keys.");

            _irishModeDefault = Config.Bind(
                "Display",
                "IrishLearnerModeOnStart",
                false,
                "If true, wired UI starts in Irish + [English] mode; if false, vanilla English until you press the toggle key.");

            IrishLearnerModeEnabled = _irishModeDefault.Value;

            IrishTranslationCache.LoadFromPluginFolder(Log);

            _harmony = new Harmony(PluginInfo.PLUGIN_GUID);
            _harmony.PatchAll(typeof(Plugin).Assembly);

            Log.LogInfo(
                $"{PluginInfo.PLUGIN_NAME} {PluginInfo.PLUGIN_VERSION} loaded. Wired keys: {IrishTranslationCache.LoadedCount}. " +
                $"Irish mode: {(IrishLearnerModeEnabled ? "on" : "off")}. Toggle: {_toggleKey.Value}.");
        }

        private void Update()
        {
            if (!Input.GetKeyDown(_toggleKey.Value))
                return;

            IrishLearnerModeEnabled = !IrishLearnerModeEnabled;
            Log.LogInfo($"Irish learner mode: {(IrishLearnerModeEnabled ? "ON (Irish + [English])" : "OFF (English)")}.");

            TryRefreshMainMenuLocalization();
        }

        private static void TryRefreshMainMenuLocalization()
        {
            if (Localization.instance == null)
                return;

            var startup = UnityEngine.Object.FindObjectOfType<FejdStartup>();
            if (startup == null)
                return;

            Localization.instance.ReLocalizeAll(startup.transform);
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
        public const string PLUGIN_VERSION = "0.3.0";
    }
}
