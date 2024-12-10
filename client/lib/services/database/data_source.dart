// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:karakuri_agent/models/agent_config.dart';

abstract class DataSource {
  Future<int> insertAgentConfig(AgentConfig config);
  Future<bool> updateAgentConfig(AgentConfig config);
  Future<bool> deleteAgentConfig(int configId);
  Future<List<AgentConfig>> queryAllAgentConfig();
  Future<void> close();
}
