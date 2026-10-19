using HarmonyLib;

namespace IrishMod
{
    [HarmonyPatch(typeof(Localization), "Translate")]
    internal static class LocalizationTranslatePatch
    {
        private static void Postfix(string word, ref string __result)
        {
            if (!Plugin.IrishLearnerModeEnabled)
                return;

            if (!MainMenuTranslationCache.TryGet(word, out var entry))
                return;

            var english = string.IsNullOrEmpty(__result) ? entry.English : __result;
            __result = $"{entry.Irish} [{english}]";
        }
    }
}
