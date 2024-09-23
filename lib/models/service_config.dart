import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/models/stt_config.dart';
import 'package:karakuri_agent/models/text_config.dart';
import 'package:karakuri_agent/models/tts_config.dart';

class ServiceConfig {
  final String? id;
  final String name;
  final ServiceType type;
  final String baseUrl;
  final String apiKey;
  final TextConfig? textConfig;
  final TTSConfig? ttsConfig;
  final STTConfig? sttConfig;

  ServiceConfig({
    required this.id,
    required this.name,
    required this.type,
    required this.baseUrl,
    required this.apiKey,
    this.textConfig,
    this.ttsConfig,
    this.sttConfig,
  });

  ServiceConfig copyWith({
    String? id,
    String? name,
    ServiceType? type,
    String? baseUrl,
    String? apiKey,
    TextConfig? textLLMConfig,
    TTSConfig? ttsConfig,
    STTConfig? sttConfig,
  }) {
    return ServiceConfig(
      id: id ?? this.id,
      name: name ?? this.name,
      type: type ?? this.type,
      baseUrl: baseUrl ?? this.baseUrl,
      apiKey: apiKey ?? this.apiKey,
      textConfig: textLLMConfig ?? this.textConfig,
      ttsConfig: ttsConfig ?? this.ttsConfig,
      sttConfig: sttConfig ?? this.sttConfig,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'type': type.name,
        'base_url': baseUrl,
        'api_key': apiKey,
        'text_llm_config': textConfig?.toJson(),
        'tts_config': ttsConfig?.toJson(),
        'stt_config': sttConfig?.toJson(),
      };

  factory ServiceConfig.fromJson(Map<String, dynamic> json) => ServiceConfig(
        id: json['id'],
        name: json['name'],
        type: ServiceType.values.firstWhere((e) => e.name == json['type']),
        baseUrl: json['base_url'],
        apiKey: json['api_key'],
        textConfig: json['text_llm_config'] != null
            ? TextConfig.fromJson(json['text_llm_config'])
            : null,
        ttsConfig: json['tts_config'] != null
            ? TTSConfig.fromJson(json['tts_config'])
            : null,
        sttConfig: json['stt_config'] != null
            ? STTConfig.fromJson(json['stt_config'])
            : null,
      );
}
