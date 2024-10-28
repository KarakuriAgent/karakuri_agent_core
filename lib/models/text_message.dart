import 'package:freezed_annotation/freezed_annotation.dart';

part 'text_message.freezed.dart';
part 'text_message.g.dart';

@freezed
class TextMessage with _$TextMessage {
  const TextMessage._();
  const factory TextMessage({
    required Role role,
    required Emotion emotion,
    required String message,
  }) = _TextMessage;
  factory TextMessage.fromJson(Map<String, dynamic> json) =>
      _$TextMessageFromJson(json);
}

enum Role { system, user, assistant }

enum Emotion {
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
}
