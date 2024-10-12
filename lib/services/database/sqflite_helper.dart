import 'package:flutter/foundation.dart';
import 'package:karakuri_agent/models/key_value_pair.dart';
import 'package:karakuri_agent/models/service_config.dart';
import 'package:karakuri_agent/models/speech_to_text_config.dart';
import 'package:karakuri_agent/models/text_config.dart';
import 'package:karakuri_agent/models/text_to_speech_config.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';

class TableName {
  static const serviceConfig = 'service_config';
  static const textConfig = 'text_config';
  static const textModel = 'text_model';
  static const textToSpeechConfig = 'text_to_speech_config';
  static const textToSpeechVoice = 'text_to_speech_voice';
  static const speechToTextConfig = 'speech_to_text_config';
  static const speechToTextModel = 'speech_to_text_model';
}

class ColumnName {
  static const id = 'id';
  static const name = 'name';
  static const type = 'type';
  static const baseUrl = 'base_url';
  static const apiKey = 'api_key';
  static const serviceConfigId = 'service_config_id';
  static const parentId = 'parent_id';
  static const key = 'key';
  static const value = 'value';
}

class SqfliteHelper {
  static final SqfliteHelper instance = SqfliteHelper._init();
  static Database? _database;

  SqfliteHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    const fileName = 'karakuri.db';
    final path = kIsWeb ? fileName : join(await getDatabasesPath(), fileName);
    final factory = kIsWeb ? databaseFactoryFfiWeb : databaseFactory;
    return await factory.openDatabase(
      path,
      options: OpenDatabaseOptions(version: 1, onCreate: _createDB),
    );
  }

  Future<void> close() async => await _database?.close();

  Future<void> _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE ${TableName.serviceConfig} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.name} TEXT NOT NULL,
        ${ColumnName.type} TEXT NOT NULL,
        ${ColumnName.baseUrl} TEXT NOT NULL,
        ${ColumnName.apiKey} TEXT NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE ${TableName.textConfig} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.serviceConfigId} INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (${ColumnName.serviceConfigId}) REFERENCES ${TableName.serviceConfig}(${ColumnName.id}) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE ${TableName.textModel} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.parentId} INTEGER NOT NULL,
        ${ColumnName.key} TEXT NOT NULL,
        ${ColumnName.value} TEXT NOT NULL,
        UNIQUE (${ColumnName.parentId}, ${ColumnName.key}),
        FOREIGN KEY (${ColumnName.parentId}) REFERENCES ${TableName.textConfig}(${ColumnName.id}) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE ${TableName.textToSpeechConfig} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.serviceConfigId} INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (${ColumnName.serviceConfigId}) REFERENCES ${TableName.serviceConfig}(${ColumnName.id}) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE ${TableName.textToSpeechVoice} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.parentId} INTEGER NOT NULL,
        ${ColumnName.key} TEXT NOT NULL,
        ${ColumnName.value} TEXT NOT NULL,
        UNIQUE (${ColumnName.parentId}, ${ColumnName.key}),
        FOREIGN KEY (${ColumnName.parentId}) REFERENCES ${TableName.textToSpeechConfig}(${ColumnName.id}) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE ${TableName.speechToTextConfig} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.serviceConfigId} INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (${ColumnName.serviceConfigId}) REFERENCES ${TableName.serviceConfig}(${ColumnName.id}) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE ${TableName.speechToTextModel} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.parentId} INTEGER NOT NULL,
        ${ColumnName.key} TEXT NOT NULL,
        ${ColumnName.value} TEXT NOT NULL,
        UNIQUE (${ColumnName.parentId}, ${ColumnName.key}),
        FOREIGN KEY (${ColumnName.parentId}) REFERENCES ${TableName.speechToTextConfig}(${ColumnName.id}) ON DELETE CASCADE
      )
    ''');
  }

  Future<int> insertServiceConfig(ServiceConfig serviceConfig) async {
    final db = await database;
    return await db.transaction((txn) async {
      return await _insertServiceConfig(txn, serviceConfig);
    });
  }

  Future<bool> updateServiceConfig(ServiceConfig serviceConfig) async {
    final db = await database;
    return await db.transaction((txn) async {
      return await _updateServiceConfig(txn, serviceConfig);
    });
  }

  Future<bool> deleteServiceConfig(int configId) async {
    final db = await database;
    final int rowsAffected = await db.delete(
      TableName.serviceConfig,
      where: '${ColumnName.id} = ?',
      whereArgs: [configId],
    );
    return rowsAffected > 0;
  }

  Future<int> _insertServiceConfig(
      Transaction txn, ServiceConfig serviceConfig) async {
    final int serviceConfigId = await txn.insert(
      TableName.serviceConfig,
      serviceConfig.toDatabaseMap(),
    );
    if (serviceConfigId == 0) return -1;

    serviceConfig = serviceConfig.copyWith(id: serviceConfigId);

    if (serviceConfig.textConfig != null) {
      final int textConfigId = await txn.insert(TableName.textConfig,
          serviceConfig.textConfig!.toDatabaseMap(serviceConfigId));
      if (textConfigId == 0) return -1;

      for (var model in serviceConfig.textConfig!.models) {
        final int modelId = await txn.insert(
            TableName.textModel, model.toDatabaseMap(textConfigId));
        if (modelId == 0) return -1;
      }
    }

    if (serviceConfig.textToSpeechConfig != null) {
      final int textToSpeechConfigId = await txn.insert(
          TableName.textToSpeechConfig,
          serviceConfig.textToSpeechConfig!.toDatabaseMap(serviceConfigId));
      if (textToSpeechConfigId == 0) return -1;

      for (var voice in serviceConfig.textToSpeechConfig!.voices) {
        final voiceId = await txn.insert(TableName.textToSpeechVoice,
            voice.toDatabaseMap(textToSpeechConfigId));
        if (voiceId == 0) return -1;
      }
    }

    if (serviceConfig.speechToTextConfig != null) {
      final int speechToTextConfigId = await txn.insert(
          TableName.speechToTextConfig,
          serviceConfig.speechToTextConfig!.toDatabaseMap(serviceConfigId));
      if (speechToTextConfigId == 0) return -1;

      for (var model in serviceConfig.speechToTextConfig!.models) {
        final modelId = await txn.insert(TableName.speechToTextModel,
            model.toDatabaseMap(speechToTextConfigId));
        if (modelId == 0) return -1;
      }
    }

    return serviceConfigId;
  }

  Future<bool> _updateServiceConfig(
      Transaction txn, ServiceConfig serviceConfig) async {
    final int serviceConfigId = serviceConfig.id!;

    final updateServiceConfig = await txn.update(
      TableName.serviceConfig,
      serviceConfig.toDatabaseMap(),
      where: '${ColumnName.id} = ?',
      whereArgs: [serviceConfigId],
    );
    if (updateServiceConfig == 0) return false;

    final updateTextConfig =
        await _updateTextConfig(txn, serviceConfigId, serviceConfig.textConfig);
    if (!updateTextConfig) return false;

    final updateTextToSpeechConfig = await _updateTextToSpeechConfig(
        txn, serviceConfigId, serviceConfig.textToSpeechConfig);
    if (!updateTextToSpeechConfig) return false;

    final updateSpeechToTextConfig = await _updateSpeechToTextConfig(
        txn, serviceConfigId, serviceConfig.speechToTextConfig);
    if (!updateSpeechToTextConfig) return false;

    return true;
  }

  Future<bool> _updateTextConfig(
      Transaction txn, int serviceConfigId, TextConfig? textConfig) async {
    if (textConfig != null) {
      final List<Map<String, dynamic>> existingTextConfig = await txn.query(
        TableName.textConfig,
        where: '${ColumnName.serviceConfigId} = ?',
        whereArgs: [serviceConfigId],
      );

      int textConfigId;
      if (existingTextConfig.isNotEmpty) {
        textConfigId = existingTextConfig.first[ColumnName.id] as int;

        final result = await _updateKeyValuePairList(
          txn,
          TableName.textModel,
          textConfigId,
          textConfig.models,
        );
        if (!result) return false;
      } else {
        textConfigId = await txn.insert(TableName.textConfig,
            {ColumnName.serviceConfigId: serviceConfigId});
        if (textConfigId == 0) return false;

        for (var model in textConfig.models) {
          final modelId = await txn.insert(
              TableName.textModel, model.toDatabaseMap(textConfigId));
          if (modelId == 0) return false;
        }
      }
    } else {
      await txn.delete(
        TableName.textConfig,
        where: '${ColumnName.serviceConfigId} = ?',
        whereArgs: [serviceConfigId],
      );
    }
    return true;
  }

  Future<bool> _updateTextToSpeechConfig(Transaction txn, int serviceConfigId,
      TextToSpeechConfig? textToSpeechConfig) async {
    if (textToSpeechConfig != null) {
      final List<Map<String, dynamic>> existingTextToSpeechConfig =
          await txn.query(
        TableName.textToSpeechConfig,
        where: '${ColumnName.serviceConfigId} = ?',
        whereArgs: [serviceConfigId],
      );

      int textToSpeechConfigId;
      if (existingTextToSpeechConfig.isNotEmpty) {
        textToSpeechConfigId =
            existingTextToSpeechConfig.first[ColumnName.id] as int;

        final result = await _updateKeyValuePairList(
          txn,
          TableName.textToSpeechVoice,
          textToSpeechConfigId,
          textToSpeechConfig.voices,
        );
        if (!result) return false;
      } else {
        textToSpeechConfigId = await txn.insert(TableName.textToSpeechConfig,
            {ColumnName.serviceConfigId: serviceConfigId});
        if (textToSpeechConfigId == 0) return false;

        for (var voice in textToSpeechConfig.voices) {
          final voiceId = await txn.insert(TableName.textToSpeechVoice,
              voice.toDatabaseMap(textToSpeechConfigId));
          if (voiceId == 0) return false;
        }
      }
    } else {
      await txn.delete(
        TableName.textToSpeechConfig,
        where: '${ColumnName.serviceConfigId} = ?',
        whereArgs: [serviceConfigId],
      );
    }
    return true;
  }

  Future<bool> _updateSpeechToTextConfig(Transaction txn, int serviceConfigId,
      SpeechToTextConfig? speechToTextConfig) async {
    if (speechToTextConfig != null) {
      final List<Map<String, dynamic>> existingSpeechToTextConfig =
          await txn.query(
        TableName.speechToTextConfig,
        where: '${ColumnName.serviceConfigId} = ?',
        whereArgs: [serviceConfigId],
      );

      int speechToTextConfigId;
      if (existingSpeechToTextConfig.isNotEmpty) {
        speechToTextConfigId =
            existingSpeechToTextConfig.first[ColumnName.id] as int;

        final result = await _updateKeyValuePairList(
          txn,
          TableName.speechToTextModel,
          speechToTextConfigId,
          speechToTextConfig.models,
        );
        if (!result) return false;
      } else {
        speechToTextConfigId = await txn.insert(TableName.speechToTextConfig,
            {ColumnName.serviceConfigId: serviceConfigId});
        if (speechToTextConfigId == 0) return false;

        for (var model in speechToTextConfig.models) {
          final mldelId = await txn.insert(TableName.speechToTextModel,
              model.toDatabaseMap(speechToTextConfigId));
          if (mldelId == 0) return false;
        }
      }
    } else {
      await txn.delete(
        TableName.speechToTextConfig,
        where: '${ColumnName.serviceConfigId} = ?',
        whereArgs: [serviceConfigId],
      );
    }
    return true;
  }

  Future<bool> _updateKeyValuePairList(
    Transaction txn,
    String tableName,
    int parentId,
    List<KeyValuePair> newList,
  ) async {
    final List<Map<String, dynamic>> existingItems = await txn.query(
      tableName,
      where: '${ColumnName.parentId} = ?',
      whereArgs: [parentId],
    );

    final Map<int, Map<String, dynamic>> existingItemsMap = {
      for (var item in existingItems) item[ColumnName.id] as int: item
    };

    for (var newItem in newList) {
      MapEntry<int, Map<String, dynamic>>? existingEntry;
      try {
        existingEntry = existingItemsMap.entries.firstWhere(
          (entry) =>
              entry.value[ColumnName.key] == newItem.key &&
              entry.value[ColumnName.value] == newItem.value,
        );
      } catch (e) {
        existingEntry = null;
      }

      if (existingEntry != null) {
        existingItemsMap.remove(existingEntry.key);
      } else {
        final itemMap = newItem.toDatabaseMap(parentId);
        itemMap[ColumnName.parentId] = parentId;
        final id = await txn.insert(tableName, itemMap);
        if (id == 0) return false;
      }
    }

    for (var remainingKey in existingItemsMap.keys) {
      await txn.delete(
        tableName,
        where: '${ColumnName.id} = ?',
        whereArgs: [remainingKey],
      );
    }
    return true;
  }

  Future<List<ServiceConfig>> queryAllServiceConfig() async {
    final db = await instance.database;
    final serviceConfigs = await db.query(TableName.serviceConfig);
    final textConfigs = await db.query(TableName.textConfig);
    final textModels = await db.query(TableName.textModel);
    final textToSpeechConfigs = await db.query(TableName.textToSpeechConfig);
    final textToSpeechVoices = await db.query(TableName.textToSpeechVoice);
    final speechToTextConfigs = await db.query(TableName.speechToTextConfig);
    final speechToTextModels = await db.query(TableName.speechToTextModel);

    final textConfigMap = {
      for (var d in textConfigs)
        d[ColumnName.serviceConfigId] as int: TextConfig.fromJson(d)
    };
    final textModelMap = <int, List<KeyValuePair>>{};
    for (var textModel in textModels) {
      textModelMap
          .putIfAbsent(textModel[ColumnName.parentId] as int, () => [])
          .add(KeyValuePair.fromJson(textModel));
    }
    final textToSpeechConfigMap = {
      for (var d in textToSpeechConfigs)
        d[ColumnName.serviceConfigId] as int: TextToSpeechConfig.fromJson(d)
    };
    final textToSpeechVoiceMap = <int, List<KeyValuePair>>{};
    for (var voice in textToSpeechVoices) {
      textToSpeechVoiceMap
          .putIfAbsent(voice[ColumnName.parentId] as int, () => [])
          .add(KeyValuePair.fromJson(voice));
    }
    final speechToTextConfigMap = {
      for (var d in speechToTextConfigs)
        d[ColumnName.serviceConfigId] as int: SpeechToTextConfig.fromJson(d)
    };
    final speechToTextModelMap = <int, List<KeyValuePair>>{};
    for (var model in speechToTextModels) {
      speechToTextModelMap
          .putIfAbsent(model[ColumnName.parentId] as int, () => [])
          .add(KeyValuePair.fromJson(model));
    }
    return serviceConfigs.map((serviceConfig) {
      final textConfig = textConfigMap[serviceConfig[ColumnName.id] as int];
      final textToSpeechConfig =
          textToSpeechConfigMap[serviceConfig[ColumnName.id] as int];
      final speechToTextConfig =
          speechToTextConfigMap[serviceConfig[ColumnName.id] as int];
      return ServiceConfig.fromJson(serviceConfig).copyWith(
        textConfig:
            textConfig?.copyWith(models: textModelMap[textConfig.id] ?? []),
        textToSpeechConfig: textToSpeechConfig?.copyWith(
            voices: textToSpeechVoiceMap[textToSpeechConfig.id] ?? []),
        speechToTextConfig: speechToTextConfig?.copyWith(
            models: speechToTextModelMap[speechToTextConfig.id] ?? []),
      );
    }).toList();
  }
}
