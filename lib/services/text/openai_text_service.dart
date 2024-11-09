import 'dart:async';
import 'dart:convert';

import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/services/text/text_service.dart';
import 'package:karakuri_agent/utils/exception.dart';
import 'package:karakuri_agent/utils/log.dart';
import 'package:openai_dart/openai_dart.dart';

class OpenaiTextService extends TextService {
  final AgentConfig _agentConfig;
  final OpenAIClient _client;
  Completer<CreateChatCompletionResponse?>? _cancelCompleter;

  OpenaiTextService(this._agentConfig)
      : _client = OpenAIClient(
          baseUrl: _agentConfig.textServiceConfig.baseUrl,
          apiKey: _agentConfig.textServiceConfig.apiKey,
        );

  @override
  Future<List<TextMessage>> completions(List<TextMessage> messages) async {
    try {
      _cancelCompleter = Completer();
      final response = await Future.any([
        _client.createChatCompletion(
          request: CreateChatCompletionRequest(
            model: ChatCompletionModel.modelId(_agentConfig.textModel.key),
            messages: _createOpenAiMessages(messages),
            responseFormat: ResponseFormatJsonSchema(
                jsonSchema: JsonSchemaObject(
                    name: "message_schema", schema: jsonSchema, strict: true)),
          ),
        ),
        _cancelCompleter?.future ??
            Future<CreateChatCompletionResponse?>.value(null),
      ]);
      if (response == null) {
        throw CancellationException('OpenaiTextToSpeech');
      }
      final jsonContent = jsonDecode(response.choices.first.message.content!)
          as Map<String, dynamic>;

      final responsesList = jsonContent['responses'] as List;
      return responsesList
          .map((response) => TextMessage(
                role: Role.assistant,
                emotion: Emotion.fromString(response['emotion'] as String),
                message: response['divided_message'] as String,
              ))
          .toList();
    } on CancellationException {
      rethrow;
    } catch (e, stackTrace) {
      debugPrint(e.toString());
      debugPrint(stackTrace.toString());
      throw ServiceException(runtimeType.toString(), 'completions');
    } finally {
      _cancelCompleter = null;
    }
  }

  @override
  void cancel() {
    _cleanupCancelCompleter();
  }

  @override
  void dispose() {
    _cleanupCancelCompleter();
  }

  List<ChatCompletionMessage> _createOpenAiMessages(
      List<TextMessage> messages) {
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

  void _cleanupCancelCompleter() {
    if (_cancelCompleter?.isCompleted == false) {
      _cancelCompleter?.complete(null);
    }
    _cancelCompleter = null;
  }
}
