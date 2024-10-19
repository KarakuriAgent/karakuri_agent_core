import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/services/text/text_service.dart';
import 'package:openai_dart/openai_dart.dart';

class OpenaiTextService extends TextService {
  final AgentConfig _agentConfig;
  final OpenAIClient _client;

  OpenaiTextService(this._agentConfig)
      : _client = OpenAIClient(
          baseUrl: _agentConfig.textServiceConfig.baseUrl,
          apiKey: _agentConfig.textServiceConfig.apiKey,
        );

  @override
  Future<TextMessage> completions(List<TextMessage> messages) async {
    try {
      final response = await _client.createChatCompletion(
        request: CreateChatCompletionRequest(
          model: ChatCompletionModel.modelId(_agentConfig.textModel.key),
          messages: _createOpenAiMessages(messages),
          temperature: 0,
        ),
      );
      return TextMessage(
        role: Role.assistant,
        message: response.choices.first.message.content!,
      );
    } catch (e) {
      throw Exception('An unexpected error occurred during transcription.');
    }
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
    }
  }
}
