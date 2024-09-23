enum ServiceType { openAI, voiceVox, styleBertVITS2 }

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
        return 'OpenAI';
      case ServiceType.voiceVox:
        return 'VoiceVox';
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
      case ServiceType.voiceVox:
        return const ServiceCapabilities(
          supportsTextToSpeech: true,
        );
      case ServiceType.styleBertVITS2:
        return const ServiceCapabilities(
          supportsTextToSpeech: true,
        );
    }
  }
}
