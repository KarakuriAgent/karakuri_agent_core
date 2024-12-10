import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/agent_image.dart';
import 'package:karakuri_agent/models/agent_response.dart';
import 'package:karakuri_agent/providers/image_storage_provider.dart';
import 'package:karakuri_agent/providers/speech_provider.dart';
import 'package:karakuri_agent/providers/speech_to_text_provider.dart';
import 'package:karakuri_agent/providers/agent_provider.dart';
import 'package:karakuri_agent/repositories/image_storage_repository.dart';
import 'package:karakuri_agent/repositories/speech_repository.dart';
import 'package:karakuri_agent/repositories/speech_to_text_repository.dart';
import 'package:karakuri_agent/repositories/agent_repository.dart';

class TalkScreenViewModel extends ChangeNotifier {
  final Ref _ref;
  final AgentConfig _agentConfig;
  late final List<AgentImage> _agentImages;
  late final SpeechToTextRepository _speechToTextRepository;
  late final AgentRepository _chatRepository;
  late final SpeechRepository _speechRepository;
  late final ImageStorageRepository _imageStorageRepository;
  TalkScreenViewModelState _state = TalkScreenViewModelState.loading;
  AgentImage? _agentImage;
  String? _userMessage;
  String? _agentMessage;
  String? _emotion;

  TalkScreenViewModelState get state => _state;
  AgentImage? get agentImage => _agentImage;
  String? get userMessage => _userMessage;
  String? get agentMessage => _agentMessage;
  String? get emotion => _emotion;

  TalkScreenViewModel(this._ref, this._agentConfig);

  Future<void> initialize() async {
    _speechToTextRepository = await _ref.watch(speechToTextProvider.future);
    _chatRepository = _ref.watch(chatProvider(_agentConfig));
    _speechRepository = _ref.watch(speechProvider);
    _imageStorageRepository = await _ref.watch(imageStorageProvider.future);
    _agentImages =
        await _imageStorageRepository.getAgentImages(_agentConfig.imageKey);
    _agentImage = _agentImages
        .firstWhere((element) => element.emotion == Emotion.neutral);
    _state = TalkScreenViewModelState.initialized;
    notifyListeners();
  }

  @override
  void dispose() {
    if (state == TalkScreenViewModelState.disposed) return;
    _state = TalkScreenViewModelState.disposed;
    stop().then((_) {
      super.dispose();
    });
  }

  Future<void> start() async {
    if (state == TalkScreenViewModelState.disposed) return;

    _changeState(TalkScreenViewModelState.listening, "", "", Emotion.neutral);

    String message = await _speechToTextRepository.start();
    if (message.isEmpty) {
      _changeState(
          TalkScreenViewModelState.initialized, "", "", Emotion.neutral);
      return;
    }

    _changeState(
        TalkScreenViewModelState.thinking, message, "", Emotion.progress);
    final agentResponse = await _chatRepository.sendMessage(message);
    if (agentResponse == null) {
      _changeState(
          TalkScreenViewModelState.initialized, "", "", Emotion.neutral);
      return;
    }
    _agentImage = _agentImages.firstWhere(
        (element) => element.emotion == agentResponse.emotion,
        orElse: () => _agentImages
            .firstWhere((element) => element.emotion == Emotion.neutral));

    _changeState(TalkScreenViewModelState.speaking, message,
        agentResponse.agentMessage, agentResponse.emotion);
    bool isSpeechCompleted =
        await _speechRepository.play(agentResponse.audioUrl);

    _changeState(TalkScreenViewModelState.initialized, "", "", Emotion.neutral);
    if (isSpeechCompleted) {
      await start();
    }
  }

  Future<void> stop() async {
    if (state == TalkScreenViewModelState.disposed) return;
    try {
      await _speechToTextRepository.stop();
      _chatRepository.cancel();
      await _speechRepository.stop();
      _changeState(
          TalkScreenViewModelState.initialized, "", "", Emotion.neutral);
    } catch (e) {
      debugPrint('Error during pause: $e');
    }
  }

  void _changeState(TalkScreenViewModelState state, String userMessage,
      String agentMessage, Emotion emotion) {
    _userMessage = userMessage;
    _agentMessage = agentMessage;
    _emotion = emotion.name;
    _agentImage = _agentImages.firstWhere(
        (element) => element.emotion == emotion,
        orElse: () => _agentImages
            .firstWhere((element) => element.emotion == Emotion.neutral));
    _state = state;
    notifyListeners();
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
