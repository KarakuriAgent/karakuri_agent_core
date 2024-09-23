import 'package:karakuri_agent/i18n/strings.g.dart';

enum ConfigType { text, tts, stt }

extension ConfigTypeExtension on ConfigType {
  String get name {
    switch (this) {
      case ConfigType.text:
        return t.settings.serviceSettings.serviceConfig.textConfig.configType;
      case ConfigType.tts:
        return t.settings.serviceSettings.serviceConfig.ttsConfig.configType;
      case ConfigType.stt:
        return t.settings.serviceSettings.serviceConfig.sttConfig.configType;
    }
  }

    String get title {
    switch (this) {
      case ConfigType.text:
        return t.settings.serviceSettings.serviceConfig.textConfig.title;
      case ConfigType.tts:
        return t.settings.serviceSettings.serviceConfig.ttsConfig.title;
      case ConfigType.stt:
        return t.settings.serviceSettings.serviceConfig.sttConfig.title;
    }
  }
}
