import 'package:karakuri_agent/models/text_message.dart';

abstract class TextService {
  Future<List<TextMessage>> completions(List<TextMessage> messages);
  void cancel();
  void dispose();

  final jsonSchema = {
    "type": "object",
    "properties": {
      "responses": {
        "type": "array",
        "description": "List of messages divided into meaningful units",
        "items": {
          "type": "object",
          "properties": {
            "emotion": {
              "type": "string",
              "description": "Emotion expressed in the divided message",
              "enum": Emotion.toRequestValues(),
            },
            "divided_message": {"type": "string", "description": "The divided message"}
          },
          "required": ["emotion", "divided_message"],
          "additionalProperties": false
        }
      }
    },
    "required": ["responses"],
    "additionalProperties": false
  };
}
