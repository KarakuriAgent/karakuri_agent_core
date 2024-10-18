import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/providers/speech_to_text_provider.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';

class TalkScreenViewModel extends ChangeNotifier {
  final AutoDisposeRef _ref;
  final AgentConfig _agentConfig;
  bool initialized = false;
  bool isListening = false;
  String speechToTextResultText = '';
  late SpeechToTextRepository? speechToTextRepository;

  TalkScreenViewModel(this._ref, this._agentConfig);

  Future<void> build() async {
    speechToTextRepository =
        await _ref.watch(speechToTextProvider(_agentConfig).future);
    initialized = true;
    notifyListeners();
  }

  void start() {
    isListening = true;
    speechToTextRepository?.startRecognition((String speechToTextResult) {
      speechToTextResultText = speechToTextResult;
      notifyListeners();
    });
    notifyListeners();
  }

  void pause() {
    speechToTextRepository?.pauseRecognition();
    isListening = false;
    notifyListeners();
  }
}
