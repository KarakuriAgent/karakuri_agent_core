import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/text_message.dart';
import 'package:karakuri_agent/models/text_result.dart';
import 'package:karakuri_agent/providers/speech_to_text_provider.dart';
import 'package:karakuri_agent/providers/text_provider.dart';
import 'package:karakuri_agent/providers/text_to_speech_provider.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';
import 'package:karakuri_agent/repositories/text_repository.dart';
import 'package:karakuri_agent/repositories/text_to_speech_repository.dart';
import 'package:karakuri_agent/utils/exception.dart';

class TalkScreenViewModel extends ChangeNotifier {
  final AutoDisposeRef _ref;
  final AgentConfig _agentConfig;
  late final SpeechToTextRepository _speechToTextRepository;
  late final TextRepository _textRepository;
  late final TextToSpeechRepository _textToSpeechRepository;
  final List<TextMessage> _messages = [];
  TalkScreenViewModelState _state = TalkScreenViewModelState.loading;
  StreamSubscription? _completionsSubscription;
  int _currentMessageId = 0;
  final Map<int, _QueuedAudio> _pendingAudio = {};
  final List<String> _pendingMessages = [];
  int _nextPlayMessageId = 0;
  bool _isPlaying = false;
  String _speechToText = '';
  String _textToSpeech = '';
  String _emotion = '';

  TalkScreenViewModelState get state => _state;
  String get speechToText => _speechToText;
  String get textToSpeech => _textToSpeech;
  String get emotion => _emotion;

  TalkScreenViewModel(this._ref, this._agentConfig);

  Future<void> initialize() async {
    _speechToTextRepository = await _ref.watch(speechToTextProvider(
            SpeechToTextProviderParam(
                agentConfig: _agentConfig, onResult: _onResult))
        .future);
    _textRepository = _ref.watch(textProvider(_agentConfig));
    _textToSpeechRepository = _ref.watch(textToSpeechProvider(_agentConfig));
    _state = TalkScreenViewModelState.initialized;
    notifyListeners();
  }

  @override
  void dispose() {
    if (state == TalkScreenViewModelState.disposed) return;
    _state = TalkScreenViewModelState.disposed;
    _completionsSubscription?.cancel();
    _pendingAudio.clear();
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
      _completionsSubscription?.cancel();
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

    _messages.add(TextMessage(role: Role.user, message: speechToTextResult));

    try {
      _completionsSubscription?.cancel();
      _pendingMessages.clear();
      _completionsSubscription =
          _textRepository.completionsStream(_messages).listen((message) async {
        if (state == TalkScreenViewModelState.disposed) return;

        _pendingMessages.add(message.message);
        _state = TalkScreenViewModelState.speaking;

        try {
          final messageId = _currentMessageId++;
          _textToSpeechRepository.synthesize(message.message).then((audioData) {
            if (state == TalkScreenViewModelState.disposed) return;
            _pendingAudio[messageId] = _QueuedAudio(audioData, message);
            _processAudioQueue();
          });
        } on CancellationException {
          _state = TalkScreenViewModelState.initialized;
          notifyListeners();
          return;
        }
      }, onError: (error) {
        _messages.removeLast();
        _state = TalkScreenViewModelState.initialized;
        notifyListeners();
      }, onDone: () async {
        if (state == TalkScreenViewModelState.disposed) return;
        _messages.add(TextMessage(
            role: Role.assistant,
            message: _pendingMessages.map((e) => e).join()));
        _pendingMessages.clear();

        while (_pendingAudio.isNotEmpty || _isPlaying) {
          await Future.delayed(const Duration(milliseconds: 100));
        }
        await start();
      });
    } on CancellationException {
      _messages.removeLast();
      _state = TalkScreenViewModelState.initialized;
      notifyListeners();
    }
  }

  Future<void> _processAudioQueue() async {
    if (_isPlaying) return;

    _isPlaying = true;
    while (_pendingAudio.isNotEmpty) {
      if (state == TalkScreenViewModelState.disposed) break;

      if (!_pendingAudio.containsKey(_nextPlayMessageId)) {
        _isPlaying = false;
        return;
      }

      final audio = _pendingAudio.remove(_nextPlayMessageId)!;
      _nextPlayMessageId++;

      try {
        _textToSpeech = audio.message.message;
        _emotion = audio.message.emotion.name;
        notifyListeners();
        await _textToSpeechRepository.play(audio.audioData);
      } catch (e) {
        debugPrint('Error playing audio: $e');
      }
    }
    _isPlaying = false;
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

class _QueuedAudio {
  final Uint8List audioData;
  final TextResult message;

  _QueuedAudio(this.audioData, this.message);
}
