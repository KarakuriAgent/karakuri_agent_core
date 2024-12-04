import 'package:freezed_annotation/freezed_annotation.dart';

part 'agent_responce.freezed.dart';
part 'agent_responce.g.dart';

@freezed
class AgentResponce with _$AgentResponce {
  const AgentResponce._();
  const factory AgentResponce({
    @JsonKey(name: "audio_url") required String audioUrl,
    @JsonKey(name: "dulation") required int duration,
    @JsonKey(name: "user_message") required String userMessage,
    @JsonKey(name: "agent_message") required String agentMessage,
    @JsonKey(name: "emotion") required Emotion emotion,
  }) = _AgentResponce;
  factory AgentResponce.fromJson(Map<String, dynamic> json) =>
      _$AgentResponceFromJson(json);
}

enum Emotion {
  noticed,
  progress,
  // Basic emotions
  happy,
  sad,
  angry,
  scared,
  surprised,
  disgusted,

  // Positive emotions
  excited,
  joyful,
  peaceful,
  grateful,
  proud,
  confident,
  amused,
  loving,

  // Negative emotions
  anxious,
  frustrated,
  disappointed,
  embarrassed,
  guilty,
  jealous,
  lonely,

  // Other emotional states
  neutral,
  confused,
  curious,
  determined,
  tired,
  energetic,
  hopeful,
  nostalgic,
  satisfied,
  bored,
  thoughtful,
  enthusiastic,
  relaxed,
  impressed,
  skeptical;

  String get key => toString().split('.').last;

  static Emotion fromString(String value) {
    return Emotion.values.firstWhere(
      (e) => e.key == value,
      orElse: () => Emotion.neutral,
    );
  }

  static List<String> toRequestValues() {
    return Emotion.values
        .where((e) => e != Emotion.noticed && e != Emotion.progress)
        .map((e) => e.key)
        .toList();
  }
}
