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
        "description": "List of responses with emotions",
        "items": {
          "type": "object",
          "properties": {
            "emotion": {
              "type": "string",
              "description": "Emotion expressed in the message",
              "enum": Emotion.values.map((e) => e.key).toList(),
            },
            "message": {
              "type": "string",
              "description": "The message content"
            }
          },
          "required": ["emotion", "message"],
          "additionalProperties": false
        }
      }
    },
    "required": ["responses"],
    "additionalProperties": false
  };
}
