import 'dart:async';
import 'dart:typed_data';

import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/providers/speech_to_text_provider.dart';
import 'package:karakuri_agent/providers/voice_activity_detection_provider.dart';
import 'package:karakuri_agent/repositories/voice_activity_detection_repository.dart';
import 'package:karakuri_agent/services/speech_to_text/openai_speech_to_text_service.dart';
import 'package:karakuri_agent/services/speech_to_text/speech_to_text_service.dart';
import 'package:karakuri_agent/utils/exception.dart';

class SpeechToTextRepository {
  final AutoDisposeFutureProviderRef _ref;
  final AgentConfig _agentConfig;
  Function(String)? _speechToTextResult;
  late final VoiceActivityDetectionRepository _voiceActivityDetectionRepository;
  late final SpeechToTextService _service;
  final _initializedCompleter = Completer<void>();

  SpeechToTextRepository(this._ref, SpeechToTextProviderParam param)
      : _agentConfig = param.agentConfig,
        _speechToTextResult = param.onResult;

  Future<void> init() async {
    _voiceActivityDetectionRepository = await _ref.watch(
        voiceActivityDetectionProvider((audio) => _createTranscription(audio))
            .future);
    switch (_agentConfig.speechToTextServiceConfig.type) {
      case ServiceType.openAI:
        _service = OpenaiSpeechToTextService(_agentConfig);
        break;
      default:
        throw Exception(
            'Unsupported Speech to Text service type: ${_agentConfig.speechToTextServiceConfig.type}');
    }
    _initializedCompleter.complete();
  }

  Future<void> dispose() async {
    _speechToTextResult = null;
  }

  Future<void> startRecognition() async {
    await _ensureInitialized();
    _voiceActivityDetectionRepository.start();
  }

  Future<void> pauseRecognition() async {
    await _ensureInitialized();
    _voiceActivityDetectionRepository.pause();
  }

  Future<void> _createTranscription(Uint8List audio) async {
    pauseRecognition();
    final text = await _service.createTranscription(audio);
    _speechToTextResult?.call(text);
  }

  Future<void> _ensureInitialized() async {
    try {
      await _initializedCompleter.future.timeout(Duration(seconds: 5));
    } on TimeoutException {
      throw UninitializedException(runtimeType.toString());
    }
  }
}
