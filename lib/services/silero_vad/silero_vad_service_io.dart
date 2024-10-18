import 'dart:typed_data';

import 'package:karakuri_agent/services/silero_vad/silero_vad_service_interface.dart';

// TODO: Processing for io has not yet been implemented.
class SileroVadService extends SileroVadServiceInterface {
  @override
  Future<void> create(Function(Uint8List) end) async => {};

  @override
  bool isCreated() => false;

  @override
  bool listening() => false;

  @override
  void start() async {}

  @override
  void pause() async {}

  @override
  void destroy() async {}
}
