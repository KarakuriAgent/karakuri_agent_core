enum ServiceType { openAI, voicevox, voicevoxNemo, styleBertVITS2 }

class ServiceCapabilities {
  final bool supportsText;
  final bool supportsTextToSpeech;
  final bool supportsSpeechToText;

  const ServiceCapabilities({
    this.supportsText = false,
    this.supportsTextToSpeech = false,
    this.supportsSpeechToText = false,
  });
}

extension ServiceTypeExtension on ServiceType {
  String get name {
    switch (this) {
      case ServiceType.openAI:
        return 'openAI';
      case ServiceType.voicevox:
        return 'voicevox';
      case ServiceType.voicevoxNemo:
        return 'voicevoxNemo';
      case ServiceType.styleBertVITS2:
        return 'styleBertVITS2';
    }
  }

  String get displayName {
    switch (this) {
      case ServiceType.openAI:
        return 'OpenAI';
      case ServiceType.voicevox:
        return 'Voicevox';
      case ServiceType.voicevoxNemo:
        return 'VoicevoxNemo';
      case ServiceType.styleBertVITS2:
        return 'StyleBertVITS2';
    }
  }

  ServiceCapabilities get capabilities {
    switch (this) {
      case ServiceType.openAI:
        return const ServiceCapabilities(
          supportsText: true,
          supportsTextToSpeech: true,
          supportsSpeechToText: true,
        );
      case ServiceType.voicevox:
        return const ServiceCapabilities(
          supportsTextToSpeech: true,
        );
      case ServiceType.voicevoxNemo:
        return const ServiceCapabilities(
          supportsTextToSpeech: true,
        );
      case ServiceType.styleBertVITS2:
        return const ServiceCapabilities(
          supportsTextToSpeech: true,
        );
    }
  }

  static ServiceType fromString(String value) {
    return ServiceType.values.firstWhere(
      (type) => type.name == value,
    );
  }
}
