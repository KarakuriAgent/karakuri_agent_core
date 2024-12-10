// Copyright (c) 0235 Inc.
// This file is licensed under the karakuri_agent Personal Use & No Warranty License.
// Please see the LICENSE file in the project root.
import 'package:flutter/widgets.dart';
import 'package:karakuri_agent/i18n/strings.g.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:karakuri_agent/repositories/image_storage_repository.dart';
import 'package:karakuri_agent/utils/exception.dart';

class AgentConfigScreenViewModel extends ChangeNotifier {
  final int? _id;
  final List<String> _imageKeys = [];
  final TextEditingController nameController;
  final TextEditingController baseUrlController;
  final TextEditingController apiKeyController;
  final TextEditingController agentIdController;

  bool _initialized = false;
  String? _selectImageKey;

  List<String> get imageKeys => _imageKeys;

  bool get initialized => _initialized;
  String? get selectImageKey => _selectImageKey;

  AgentConfigScreenViewModel( {AgentConfig? agentConfig})
      : _id = agentConfig?.id,
        nameController = TextEditingController(text: agentConfig?.name ?? ''),
        baseUrlController =
            TextEditingController(text: agentConfig?.baseUrl ?? ''),
        apiKeyController =
            TextEditingController(text: agentConfig?.apiKey ?? ''),
        agentIdController =
            TextEditingController(text: agentConfig?.agentId ?? ''),
        _selectImageKey = agentConfig?.imageKey;

  Future<void> initialize(ImageStorageRepository imageStorage) async {
    _imageKeys.addAll(await imageStorage.getImageNames());
    _initialized = true;
    notifyListeners();
  }

  @override
  void dispose() {
    nameController.dispose();
    super.dispose();
  }

  void updateImageKey(String? imageKey) {
    _ensureInitialized();
    if (selectImageKey == imageKey) return;
    _selectImageKey = imageKey;
    notifyListeners();
  }

  String? validationCheck() {
    _ensureInitialized();
    if (nameController.text.isEmpty) {
      return t.agentConfig.error.nameIsRequired;
    }
    if (baseUrlController.text.isEmpty) {
      return t.agentConfig.error.baseUrlRequired;
    }
    if (apiKeyController.text.isEmpty) {
      return t.agentConfig.error.apiKeyRequired;
    }
    if (agentIdController.text.isEmpty) {
      return t.agentConfig.error.agentIdRequired;
    }
    if (selectImageKey == null) {
      return t.agentConfig.error.agentImageRequired;
    }
    return null;
  }

  AgentConfig createAgentConfig() {
    _ensureInitialized();
    return AgentConfig(
        id: _id,
        name: nameController.text,
        baseUrl: baseUrlController.text,
        apiKey: apiKeyController.text,
        imageKey: selectImageKey!,
        agentId: agentIdController.text);
  }

  void _ensureInitialized() {
    if (!initialized) {
      throw UninitializedException(runtimeType.toString());
    }
  }
}
