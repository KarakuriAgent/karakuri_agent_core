@JS('vad_web')
import 'package:js/js.dart';
import 'package:js/js_util.dart';

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

class SileroVadServce {
  Future<void> create(Function(List<int>) end) async =>
      await promiseToFuture(createVad(allowInterop((audio) => end(audio))));

  bool isCreated() => isVadCreated();

  void start() => startVad();

  bool listening() => listeningVad();

  void pause() => pauseVad();

  void destroy() => destroyVad();
}
