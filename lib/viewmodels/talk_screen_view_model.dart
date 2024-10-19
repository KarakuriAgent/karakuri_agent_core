import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/providers/speech_to_text_provider.dart';
import 'package:karakuri_agent/providers/text_provider.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';
import 'package:karakuri_agent/repositories/text_repository.dart';

class TalkScreenViewModel extends ChangeNotifier {
  final AutoDisposeRef _ref;
  final AgentConfig _agentConfig;
  late final SpeechToTextRepository speechToTextRepository;
  late final TextRepository textRepository;
  bool initialized = false;
  bool isListening = false;
  final List<TextMessage> _messages = [];
  String resultText = '';

  TalkScreenViewModel(this._ref, this._agentConfig);

  Future<void> initialize() async {
    speechToTextRepository =
        await _ref.watch(speechToTextProvider(_agentConfig).future);
    textRepository = _ref.watch(textProvider(_agentConfig));
    initialized = true;
    notifyListeners();
  }

  void start() {
    isListening = true;
    speechToTextRepository.startRecognition((String speechToTextResult) {
      if (speechToTextResult.isEmpty) {
        return;
      }
      textRepository
          .completions(_messages
            ..add(TextMessage(role: Role.user, message: speechToTextResult)))
          .then((TextMessage text) {
        _messages.add(text);
        resultText = text.message;
        notifyListeners();
      });
    });
    notifyListeners();
  }

  void pause() {
    speechToTextRepository.pauseRecognition();
    isListening = false;
    notifyListeners();
  }
}
