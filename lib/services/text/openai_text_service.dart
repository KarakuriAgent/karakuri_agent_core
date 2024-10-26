import 'dart:async';

import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/services/text/text_service.dart';
import 'package:karakuri_agent/utils/exception.dart';
import 'package:openai_dart/openai_dart.dart';

class OpenaiTextService extends TextService {
  final AgentConfig _agentConfig;
  final OpenAIClient _client;
  Completer<dynamic>? _cancelCompleter;

  OpenaiTextService(this._agentConfig)
      : _client = OpenAIClient(
          baseUrl: _agentConfig.textServiceConfig.baseUrl,
          apiKey: _agentConfig.textServiceConfig.apiKey,
        );

  @override
  Future<TextMessage> completions(List<TextMessage> messages) async {
    try {
      _cancelCompleter = Completer();
      final response = await Future.any([
        _client.createChatCompletion(
          request: CreateChatCompletionRequest(
            model: ChatCompletionModel.modelId(_agentConfig.textModel.key),
            messages: _createOpenAiMessages(messages),
            temperature: 0,
          ),
        ),
        _cancelCompleter?.future ?? Future<dynamic>.value(),
      ]);
      if (response == null) {
        throw CancellationException('OpenaiTextToSpeech');
      }
      return TextMessage(
        role: Role.assistant,
        message: response.choices.first.message.content!,
      );
    } catch (e) {
      if (!(_cancelCompleter?.isCompleted ?? true)) {
        throw ServiceException(runtimeType.toString(), 'completions');
      }
      rethrow;
    } finally {
      _cancelCompleter = null;
    }
  }

  @override
  void cancel() {
    if (_cancelCompleter?.isCompleted == false) {
      _cancelCompleter?.complete(null);
    }
    _cancelCompleter = null;
  }

  @override
  void dispose() {
    cancel();
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
}
