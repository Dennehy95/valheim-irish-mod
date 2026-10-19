using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using BepInEx.Logging;

namespace IrishMod
{
    [DataContract]
    internal sealed class MainMenuTranslationFile
    {
        [DataMember(Name = "entries")]
        public MainMenuTranslationEntryDto[]? Entries { get; set; }

        [DataMember(Name = "pendingApiKey")]
        public bool PendingApiKey { get; set; }
    }

    [DataContract]
    internal sealed class MainMenuTranslationEntryDto
    {
        [DataMember(Name = "key")]
        public string Key { get; set; } = "";

        [DataMember(Name = "english")]
        public string English { get; set; } = "";

        [DataMember(Name = "irish")]
        public string Irish { get; set; } = "";

        [DataMember(Name = "translationMethod")]
        public string TranslationMethod { get; set; } = "manual";
    }

    internal sealed class MainMenuTranslationEntry
    {
        public string Key { get; set; } = "";
        public string English { get; set; } = "";
        public string Irish { get; set; } = "";
        public string TranslationMethod { get; set; } = "manual";
    }

    /// <summary>
    /// In-memory cache for FejdStartup root main menu keys only (14 entries).
    /// </summary>
    internal static class MainMenuTranslationCache
    {
        private static readonly Dictionary<string, MainMenuTranslationEntry> ByKey =
            new Dictionary<string, MainMenuTranslationEntry>(StringComparer.Ordinal);

        internal static int LoadedCount => ByKey.Count;

        internal static bool TryGet(string key, out MainMenuTranslationEntry entry) =>
            ByKey.TryGetValue(key, out entry!);

        internal static void LoadFromPluginFolder(ManualLogSource log)
        {
            ByKey.Clear();

            var pluginDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            if (string.IsNullOrEmpty(pluginDir))
            {
                log.LogError("Could not resolve plugin directory for translation JSON.");
                return;
            }

            var jsonPath = Path.Combine(pluginDir, "Translations", "fejd-root-main-menu.ga.json");
            if (!File.Exists(jsonPath))
            {
                log.LogError($"Main menu translation file not found: {jsonPath}");
                return;
            }

            try
            {
                MainMenuTranslationFile? file;
                using (var stream = File.OpenRead(jsonPath))
                {
                    var serializer = new DataContractJsonSerializer(typeof(MainMenuTranslationFile));
                    file = serializer.ReadObject(stream) as MainMenuTranslationFile;
                }

                if (file?.Entries == null)
                {
                    log.LogError("Translation JSON missing 'entries' array.");
                    return;
                }

                foreach (var dto in file.Entries)
                {
                    if (string.IsNullOrEmpty(dto.Key))
                        continue;

                    if (string.IsNullOrEmpty(dto.Irish))
                    {
                        log.LogWarning($"Skipping key '{dto.Key}': empty Irish string.");
                        continue;
                    }

                    ByKey[dto.Key] = new MainMenuTranslationEntry
                    {
                        Key = dto.Key,
                        English = dto.English,
                        Irish = dto.Irish,
                        TranslationMethod = dto.TranslationMethod,
                    };
                }

                log.LogInfo(
                    $"Loaded {ByKey.Count} main-menu Irish strings from {jsonPath} (pendingApiKey={file.PendingApiKey}).");
            }
            catch (Exception ex)
            {
                log.LogError($"Failed to load main menu translations: {ex.Message}");
            }
        }

    }
}
