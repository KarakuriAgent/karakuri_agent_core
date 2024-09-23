class STTConfig {
  final List<Map<String, String>> models;

  STTConfig({
    required this.models,
  });

  STTConfig copyWith({
    List<Map<String, String>>? models,
  }) {
    return STTConfig(
      models: models ?? this.models,
    );
  }

  Map<String, dynamic> toJson() => {
        'models': models,
      };

  factory STTConfig.fromJson(Map<String, dynamic> json) {
    var modelsData = json['models'] as List<dynamic>;
    return STTConfig(
      models:
          modelsData.map((model) => Map<String, String>.from(model)).toList(),
    );
  }
}
