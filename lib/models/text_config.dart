class TextConfig {
  final List<Map<String, String>> models;

  TextConfig({
    required this.models,
  });

    TextConfig copyWith({
    List<Map<String, String>>? models,
  }) {
    return TextConfig(
      models: models ?? this.models,
    );
  }

  Map<String, dynamic> toJson() => {
    'models': models,
  };

  factory TextConfig.fromJson(Map<String, dynamic> json) {
    var modelsData = json['models'] as List<dynamic>;
    return TextConfig(
      models:
          modelsData.map((model) => Map<String, String>.from(model)).toList(),
    );
  }
}
