// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:karakuri_agent/models/agent_response.dart';

abstract class AgentService {
  Future<AgentResponse?> sendMessage(String message);
  Future<void> cancel();
  Future<void> dispose();
}
