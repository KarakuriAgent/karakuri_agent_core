import 'dart:async';

import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/models/text_result.dart';
import 'package:karakuri_agent/services/text/text_service.dart';
import 'package:karakuri_agent/utils/exception.dart';
import 'package:karakuri_agent/utils/log.dart';
import 'package:openai_dart/openai_dart.dart';

class OpenaiTextService extends TextService {
  final AgentConfig _agentConfig;
  final OpenAIClient _client;
  StreamSubscription? _subscription;
  final RegExp responsePattern = RegExp(
    r'\{"emotion":"([^"]+)","message":"([^"]+)"\}',
    multiLine: true,
  );

  OpenaiTextService(this._agentConfig)
      : _client = OpenAIClient(
          baseUrl: _agentConfig.textServiceConfig.baseUrl,
          apiKey: _agentConfig.textServiceConfig.apiKey,
        );

  @override
  Stream<TextResult> completionsStream(List<TextMessage> messages) async* {
    String accumulatedContent = '';
    final controller = StreamController<TextResult>();

    try {
      final stream = _client.createChatCompletionStream(
        request: CreateChatCompletionRequest(
          model: ChatCompletionModel.modelId(_agentConfig.textModel.key),
          messages: _createOpenAiMessages(messages),
          responseFormat: ResponseFormatJsonSchema(
              jsonSchema: JsonSchemaObject(
                  name: "message_schema", schema: jsonSchema, strict: true)),
        ),
      );

      _subscription = stream.listen(
        (response) {
          final content = response.choices.first.delta.content;
          if (content != null) {
            accumulatedContent += content;

            for (final match in responsePattern.allMatches(accumulatedContent)) {
              final emotion = match.group(1)!;
              final message = match.group(2)!;

              controller.add(TextResult(
                emotion: Emotion.fromString(emotion),
                message: message,
              ));

              accumulatedContent = accumulatedContent.substring(match.end);
            }
          }
        },
        onError: (error, stackTrace) {
          debugPrint(error.toString());
          debugPrint(stackTrace.toString());
          controller.addError(ServiceException(runtimeType.toString(), 'completions'));
        },
        onDone: () {
          controller.close();
        },
        cancelOnError: true,
      );

      yield* controller.stream;
    } catch (e, stackTrace) {
      debugPrint(e.toString());
      debugPrint(stackTrace.toString());
      throw ServiceException(runtimeType.toString(), 'completions');
    }
  }

  @override
  void cancel() {
    _subscription?.cancel();
    _subscription = null;
  }

  @override
  void dispose() {
    cancel();
  }

  List<ChatCompletionMessage> _createOpenAiMessages(List<TextMessage> messages) {
    return messages.map((message) => _createOpenAiMessage(message)).toList();
  }

  ChatCompletionMessage _createOpenAiMessage(TextMessage textMessage) {
    switch (textMessage.role) {
      case Role.system:
        return ChatCompletionMessage.system(content: textMessage.message);
      case Role.user:
        return ChatCompletionMessage.user(
          content: ChatCompletionUserMessageContent.string(textMessage.message),
        );
      case Role.assistant:
        return ChatCompletionMessage.assistant(content: textMessage.message);
      default:
        throw Exception('Unhandled role: ${textMessage.role}');
    }
  }
}
