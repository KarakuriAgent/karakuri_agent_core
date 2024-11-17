import 'dart:typed_data';

import 'package:karakuri_agent/services/silero_vad/export_silero_vad_service.dart';

class VoiceActivityDetectionRepository {
  final SileroVadService _service;

  VoiceActivityDetectionRepository(this._service);
  Future<void> init(Function(Uint8List) end) async {
    if (_service.isCreated()) return;
    await _service.create(((audio) => end(audio)));
  }

  Future<void> start() async => await _service.start();

  bool listening() => _service.listening();

  Future<void> pause() async => await _service.pause();

  Future<void> destroy() async => await _service.destroy();
}
