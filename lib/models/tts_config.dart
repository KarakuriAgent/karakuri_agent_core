class TTSConfig {
  final List<Map<String, String>> voices;

  TTSConfig({
    required this.voices,
  });

  TTSConfig copyWith({
    List<Map<String, String>>? voices,
  }) {
    return TTSConfig(
      voices: voices ?? this.voices,
    );
  }

  Map<String, dynamic> toJson() => {
        'voices': voices,
      };

  factory TTSConfig.fromJson(Map<String, dynamic> json) {
    var voicesData = json['voices'] as List<dynamic>;
    return TTSConfig(
      voices:
          voicesData.map((voice) => Map<String, String>.from(voice)).toList(),
    );
  }
}
