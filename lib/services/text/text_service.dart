import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/models/text_result.dart';

abstract class TextService {
  Stream<TextResult> completionsStream(List<TextMessage> messages);
  void cancel();
  void dispose();

  final jsonSchema = {
    "type": "object",
    "properties": {
      "responses": {
        "type": "array",
        "description": """
          List of assistant responses.

          ## Core Rules
          1. Segment responses at natural breaks using:
             - Sentence-ending punctuation (.。.!！?？)
             - Meaningful semantic units
             - Appropriate pause points

          ## Language-Specific Guidelines
          ### English
          ```
          Input: "Hello! How are you? I'm doing great today."
          Output segments:
          [1] "Hello!"
          [2] "How are you?"
          [3] "I'm doing great today."
          ```

          ### Japanese
          ```
          Input: "こんにちは！お元気ですか？今日はとても良い天気ですね。"
          Output segments:
          [1] "こんにちは！"
          [2] "お元気ですか？"
          [3] "今日はとても良い天気ですね。"
          ```

          ## Processing Requirements
          1. Maximum segment length: 50 characters
          2. Preserve semantic integrity
          3. Maintain punctuation in output
          4. Handle multi-language content appropriately

          ## Purpose
          - Optimize text-to-speech processing
          - Enable natural speech synthesis
          - Improve processing efficiency
          - Facilitate error handling
          - Support parallel processing

          ## Validation Criteria
          1. Each segment must be semantically complete
          2. Proper handling of punctuation
          3. Context preservation between segments
          4. Appropriate length for TTS processing
        """,
        "items": {
          "type": "object",
          "properties": {
            "emotion": {
              "type": "string",
              "description": "Emotion expressed in the response message",
              "enum": Emotion.values.map((e) => e.key).toList(),
            },
            "message": {
              "type": "string",
              "description":
                  "The response message content representing a single emotional state"
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
