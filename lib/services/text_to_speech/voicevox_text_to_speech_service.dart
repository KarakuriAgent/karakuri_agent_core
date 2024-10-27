import 'dart:async';

import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/services/text_to_speech/text_to_speech_service.dart';

class VoicevoxTextToSpeechService extends TextToSpeechService {
  final AgentConfig _agentConfig;

  VoicevoxTextToSpeechService(this._agentConfig);

  @override
  Future<void> speech(String text) async {}

  @override
  void stop() {}

  @override
  void dispose() {}
}
