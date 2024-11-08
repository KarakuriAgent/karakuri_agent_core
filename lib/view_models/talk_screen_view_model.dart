import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/karakuri_image.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/providers/image_storage_provider.dart';
import 'package:karakuri_agent/providers/speech_to_text_provider.dart';
import 'package:karakuri_agent/providers/text_provider.dart';
import 'package:karakuri_agent/providers/text_to_speech_provider.dart';
import 'package:karakuri_agent/repositories/image_storage_repository.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';
import 'package:karakuri_agent/repositories/text_repository.dart';
import 'package:karakuri_agent/repositories/text_to_speech_repository.dart';
import 'package:karakuri_agent/utils/exception.dart';

class TalkScreenViewModel extends ChangeNotifier {
  final AutoDisposeRef _ref;
  final AgentConfig _agentConfig;
  late final List<KarakuriImage> _karakuriImages;
  late final SpeechToTextRepository _speechToTextRepository;
  late final TextRepository _textRepository;
  late final TextToSpeechRepository _textToSpeechRepository;
  late final ImageStorageRepository _imageStorageRepository;
  final List<TextMessage> _messages = [];
  TalkScreenViewModelState _state = TalkScreenViewModelState.loading;
  String _speechToText = '';
  String _textToSpeech = '';
  String _emotion = '';
  KarakuriImage? _karakuriImage;

  TalkScreenViewModelState get state => _state;
  String get speechToText => _speechToText;
  String get textToSpeech => _textToSpeech;
  String get emotion => _emotion;
  KarakuriImage? get karakuriImage => _karakuriImage;

  TalkScreenViewModel(this._ref, this._agentConfig);

  Future<void> initialize() async {
    _speechToTextRepository = await _ref.watch(speechToTextProvider(
            SpeechToTextProviderParam(
                agentConfig: _agentConfig, onResult: _onResult))
        .future);
    _textRepository = _ref.watch(textProvider(_agentConfig));
    _textToSpeechRepository = _ref.watch(textToSpeechProvider(_agentConfig));
    _imageStorageRepository = await _ref.watch(imageStorageProvider.future);
    _karakuriImages =
        await _imageStorageRepository.getKarakuriImages(_agentConfig.imageKey);
    _karakuriImage = _karakuriImages.firstWhere(
        (element) => element.emotion == Emotion.normal);
    _state = TalkScreenViewModelState.initialized;
    notifyListeners();
  }

  @override
  void dispose() {
    if (state == TalkScreenViewModelState.disposed) return;
    _state = TalkScreenViewModelState.disposed;
    pause().then((_) {
      super.dispose();
    });
  }

  Future<void> start() async {
    if (state == TalkScreenViewModelState.disposed) return;
    _state = TalkScreenViewModelState.listening;
    notifyListeners();
    await _speechToTextRepository.startRecognition();
  }

  Future<void> pause() async {
    if (state == TalkScreenViewModelState.disposed) return;
    try {
      _textRepository.cancel();
      await Future.wait([
        _speechToTextRepository.pauseRecognition(),
        _textToSpeechRepository.stop(),
      ]);
      _state = TalkScreenViewModelState.initialized;
      notifyListeners();
    } catch (e) {
      debugPrint('Error during pause: $e');
    }
  }

  void _onResult(String speechToTextResult) async {
    if (state == TalkScreenViewModelState.disposed) return;
    if (speechToTextResult.isEmpty ||
        state != TalkScreenViewModelState.listening) {
      return;
    }
    _state = TalkScreenViewModelState.thinking;
    _speechToText = speechToTextResult;
    notifyListeners();
    _messages.add(TextMessage(
        role: Role.user,
        emotion: Emotion.neutral,
        message: speechToTextResult));
    final List<TextMessage> messages;
    try {
      messages = await _textRepository.completions(_messages);
    } on CancellationException {
      _messages.removeLast();
      _state = TalkScreenViewModelState.initialized;
      notifyListeners();
      return;
    }
    if (state == TalkScreenViewModelState.disposed) return;

    if (messages.isEmpty) {
      _messages.removeLast();
      _state = TalkScreenViewModelState.initialized;
      return;
    }
    for (var message in messages) {
      _messages.add(message);
      _state = TalkScreenViewModelState.speaking;
      _textToSpeech = message.message;
      _emotion = message.emotion.name;
      _karakuriImage = _karakuriImages.firstWhere(
          (element) => element.emotion == message.emotion);
      notifyListeners();
      try {
        await _textToSpeechRepository.speech(message.message);
      } on CancellationException {
        _state = TalkScreenViewModelState.initialized;
        notifyListeners();
        return;
      }
    }
    if (state == TalkScreenViewModelState.disposed) return;

    await start();
  }
}

enum TalkScreenViewModelState {
  loading,
  initialized,
  listening,
  thinking,
  speaking,
  disposed
}
