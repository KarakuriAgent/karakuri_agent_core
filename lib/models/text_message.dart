import 'package:freezed_annotation/freezed_annotation.dart';

part 'text_message.freezed.dart';
part 'text_message.g.dart';

@freezed
class TextMessage with _$TextMessage {
  const TextMessage._();
  const factory TextMessage({
    required Role role,
    required String message,
  }) = _TextMessage;
  factory TextMessage.fromJson(Map<String, dynamic> json) =>
      _$TextMessageFromJson(json);
}

enum Role { system, user, assistant }
