@JS('vad_web')
import 'dart:typed_data';

import 'package:js/js.dart';
import 'package:js/js_util.dart';
import 'package:karakuri_agent/services/silero_vad/silero_vad_service_interface.dart';
import 'package:karakuri_agent/utils/audio_util.dart';

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
  Future<void> create(Function(Uint8List) end) async =>
      await promiseToFuture(createVad(
          allowInterop((audio) => end(AudioUtil.float32ListToWav(audio)))));

  @override
  bool isCreated() => isVadCreated();

  @override
  void start() => startVad();

  @override
  bool listening() => listeningVad();

  @override
  void pause() => pauseVad();

  @override
  void destroy() => destroyVad();
}
