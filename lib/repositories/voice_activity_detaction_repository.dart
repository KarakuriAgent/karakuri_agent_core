import 'dart:typed_data';

import 'package:karakuri_agent/services/silero_vad/export_silero_vad_service.dart';

class VoiceActivityDetectionRepository {
  final SileroVadServce _service;

  VoiceActivityDetectionRepository(this._service);
  Future<void> init(Function(Uint8List) end) async {
    if (_service.isCreated()) return;
    await _service.create(((audio) => end(audio)));
  }

  void start() => _service.start();

  bool listening() => _service.listening();

  void pause() => _service.pause();

  void destroy() => _service.destroy();
}
