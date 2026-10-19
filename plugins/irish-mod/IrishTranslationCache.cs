using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using BepInEx.Logging;

namespace IrishMod
{
    [DataContract]
    internal sealed class ScopeTranslationFile
    {
        [DataMember(Name = "screen_id")]
        public string? ScreenId { get; set; }

        [DataMember(Name = "entries")]
        public ScopeTranslationEntryDto[]? Entries { get; set; }

        [DataMember(Name = "pendingApiKey")]
        public bool PendingApiKey { get; set; }
    }

    [DataContract]
    internal sealed class ScopeTranslationEntryDto
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

    internal sealed class ScopeTranslationEntry
    {
        public string Key { get; set; } = "";
        public string English { get; set; } = "";
        public string Irish { get; set; } = "";
        public string TranslationMethod { get; set; } = "manual";
    }

    /// <summary>
    /// Merges all scoped translation JSON files under Translations/*.ga.json.
    /// </summary>
    internal static class IrishTranslationCache
    {
        private static readonly Dictionary<string, ScopeTranslationEntry> ByKey =
            new Dictionary<string, ScopeTranslationEntry>(StringComparer.Ordinal);

        internal static int LoadedCount => ByKey.Count;

        internal static bool TryGet(string key, out ScopeTranslationEntry entry) =>
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

            var translationsDir = Path.Combine(pluginDir, "Translations");
            if (!Directory.Exists(translationsDir))
            {
                log.LogError($"Translations folder not found: {translationsDir}");
                return;
            }

            var files = Directory
                .EnumerateFiles(translationsDir, "*.ga.json", SearchOption.TopDirectoryOnly)
                .OrderBy(f => f, StringComparer.OrdinalIgnoreCase)
                .ToArray();

            if (files.Length == 0)
            {
                log.LogError($"No *.ga.json files in {translationsDir}");
                return;
            }

            foreach (var jsonPath in files)
            {
                LoadFile(log, jsonPath);
            }

            log.LogInfo($"Loaded {ByKey.Count} Irish strings from {files.Length} scope file(s) in {translationsDir}.");
        }

        private static void LoadFile(ManualLogSource log, string jsonPath)
        {
            try
            {
                ScopeTranslationFile? file;
                using (var stream = File.OpenRead(jsonPath))
                {
                    var serializer = new DataContractJsonSerializer(typeof(ScopeTranslationFile));
                    file = serializer.ReadObject(stream) as ScopeTranslationFile;
                }

                if (file?.Entries == null)
                {
                    log.LogError($"Translation JSON missing 'entries' array: {jsonPath}");
                    return;
                }

                var scopeLabel = string.IsNullOrEmpty(file.ScreenId)
                    ? Path.GetFileName(jsonPath)
                    : file.ScreenId;
                var added = 0;

                foreach (var dto in file.Entries)
                {
                    if (string.IsNullOrEmpty(dto.Key))
                        continue;

                    if (string.IsNullOrEmpty(dto.Irish))
                    {
                        log.LogWarning($"Skipping key '{dto.Key}' in {scopeLabel}: empty Irish string.");
                        continue;
                    }

                    if (ByKey.ContainsKey(dto.Key))
                    {
                        log.LogWarning($"Duplicate key '{dto.Key}' in {scopeLabel}; keeping first loaded entry.");
                        continue;
                    }

                    ByKey[dto.Key] = new ScopeTranslationEntry
                    {
                        Key = dto.Key,
                        English = dto.English,
                        Irish = dto.Irish,
                        TranslationMethod = dto.TranslationMethod,
                    };
                    added++;
                }

                log.LogInfo(
                    $"Scope '{scopeLabel}': {added} keys from {Path.GetFileName(jsonPath)} (pendingApiKey={file.PendingApiKey}).");
            }
            catch (Exception ex)
            {
                log.LogError($"Failed to load {jsonPath}: {ex.Message}");
            }
        }
    }
}
