import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/providers/speech_to_text_provider.dart';
import 'package:karakuri_agent/providers/text_provider.dart';
import 'package:karakuri_agent/providers/text_to_speech_provider.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';
import 'package:karakuri_agent/repositories/text_repository.dart';
import 'package:karakuri_agent/repositories/text_to_speech_repository.dart';

class TalkScreenViewModel extends ChangeNotifier {
  final AutoDisposeRef _ref;
  final AgentConfig _agentConfig;
  late final SpeechToTextRepository _speechToTextRepository;
  late final TextRepository _textRepository;
  late final TextToSpeechRepository _textToSpeechRepository;
  TalkScreenViewModelState state = TalkScreenViewModelState.loading;
  final List<TextMessage> _messages = [];
  String speechToText = '';
  String textToSpeech = '';

  TalkScreenViewModel(this._ref, this._agentConfig);

  Future<void> initialize() async {
    _speechToTextRepository =
        await _ref.watch(speechToTextProvider((_agentConfig, _onResult)).future);
    _textRepository = _ref.watch(textProvider(_agentConfig));
    _textToSpeechRepository = _ref.watch(textToSpeechProvider(_agentConfig));
    state = TalkScreenViewModelState.initialized;
    notifyListeners();
  }

  Future<void> start() async {
    state = TalkScreenViewModelState.listening;
    notifyListeners();
    await _speechToTextRepository.startRecognition();
  }

  Future<void> pause() async {
    // TODO cancel the text and text to speech
    await _speechToTextRepository.pauseRecognition();
    state = TalkScreenViewModelState.initialized;
    notifyListeners();
  }

  void _onResult(String speechToTextResult) async {
      if (speechToTextResult.isEmpty ||
          state != TalkScreenViewModelState.listening) {
        return;
      }
      state = TalkScreenViewModelState.thinking;
      speechToText = speechToTextResult;
      notifyListeners();
      _messages.add(TextMessage(role: Role.user, message: speechToTextResult));
      final message = await _textRepository.completions(_messages);
      _messages.add(message);
      state = TalkScreenViewModelState.speaking;
      textToSpeech = message.message;
      notifyListeners();
      await _textToSpeechRepository.speech(message.message);
      await start();
    }
}

enum TalkScreenViewModelState {
  loading,
  initialized,
  listening,
  thinking,
  speaking
}
