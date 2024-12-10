// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'dart:async';

abstract class SpeechToTextService {
  Future<void> init();
  Future<String> start();
  Future<void> stop();
  Future<void> dispose();
}
