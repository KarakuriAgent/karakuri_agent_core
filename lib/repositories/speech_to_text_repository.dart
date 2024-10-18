import 'dart:typed_data';

import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/models/service_type.dart';
import 'package:karakuri_agent/providers/voice_activity_detection_provider.dart';
import 'package:karakuri_agent/repositories/voice_activity_detection_repository.dart';
import 'package:karakuri_agent/services/speech_to_text/speech_to_text_openai_service.dart';
import 'package:karakuri_agent/services/speech_to_text/speech_to_text_service.dart';

class SpeechToTextRepository {
  final AutoDisposeFutureProviderRef _ref;
  final AgentConfig _agentConfig;
  Function(String)? _speechToTextResult;
  late final VoiceActivityDetectionRepository _voiceActivityDetectionRepository;
  late final SpeechToTextService _service;
  bool initialized = false;

  SpeechToTextRepository(this._ref, this._agentConfig);

  Future<void> init() async {
    _voiceActivityDetectionRepository = await _ref.watch(
        voiceActivityDetectionProvider((audio) => _createTranscription(audio))
            .future);
    switch (_agentConfig.speechToTextServiceConfig.type) {
      case ServiceType.openAI:
        _service = SpeechToTextOpenaiService(_agentConfig);
        break;
      default:
        throw Exception('Service type not supported');
    }
    initialized = true;
  }

  Future<void> dispose() async {
    _speechToTextResult = null;
  }

  void startRecognition(Function(String) speechToTextResult) {
    if (initialized == false) {
      throw Exception('SpeechToTextRepository not initialized');
    }
    _speechToTextResult = speechToTextResult;
    _speechToTextResult!.call('');
    _voiceActivityDetectionRepository.start();
  }

  void pauseRecognition() {
    if (initialized == false) {
      throw Exception('SpeechToTextRepository not initialized');
    }
    _speechToTextResult?.call('');
    _speechToTextResult = null;
    _voiceActivityDetectionRepository.pause();
  }

  Future<void> _createTranscription(Uint8List audio) async {
    final text = await _service.createTranscription(audio);
    _speechToTextResult?.call(text);
  }
}
