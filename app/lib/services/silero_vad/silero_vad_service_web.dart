@JS('vad_web')
import 'dart:typed_data';

import 'package:js/js.dart';
import 'package:js/js_util.dart';
import 'package:karakuri_agent/services/silero_vad/silero_vad_service_interface.dart';
import 'package:karakuri_agent/utils/audio_util.dart';
import 'package:karakuri_agent/utils/exception.dart';

@JS('createVad')
external Object createVad(Function end);

@JS('isVadCreated')
external bool isVadCreated();

@JS('startVad')
external void startVad();

@JS('listeningVad')
external bool listeningVad();

@JS('pauseVad')
external void pauseVad();

@JS('destroyVad')
external void destroyVad();

class SileroVadService extends SileroVadServiceInterface {
  @override
  Future<void> create(Function(Uint8List) onResult) async {
    try {
      await promiseToFuture(createVad(allowInterop(
          (audio) => onResult(AudioUtil.float32ListToWav(audio)))));
    } catch (e) {
      throw ServiceException(runtimeType.toString(), 'create',
          message: 'Failed to create VAD: $e');
    }
  }

  @override
  bool isCreated() => isVadCreated();

  @override
  Future<bool> start() async {
    startVad();
    return true;
  }

  @override
  bool listening() => listeningVad();

  @override
  Future<void> pause() async => pauseVad();

  @override
  Future<void> destroy() async => destroyVad();
}
