import 'package:flutter/foundation.dart';
import 'package:karakuri_agent/models/agent_config.dart';
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
  static const textToSpeechModel = 'text_to_speech_model';
  static const textToSpeechVoice = 'text_to_speech_voice';
  static const speechToTextConfig = 'speech_to_text_config';
  static const speechToTextModel = 'speech_to_text_model';
  static const agentConfig = 'agent_config';
}

class ColumnName {
  static const id = 'id';
  static const name = 'name';
  static const imageKey = 'image_key';
  static const type = 'type';
  static const baseUrl = 'base_url';
  static const apiKey = 'api_key';
  static const serviceConfigId = 'service_config_id';
  static const textConfigId = 'text_config_id';
  static const textToSpeechConfigId = 'text_to_speech_config_id';
  static const speechToTextConfigId = 'speech_to_text_config_id';
  static const parentId = 'parent_id';
  static const key = 'key';
  static const value = 'value';
  static const textServiceId = 'text_service_id';
  static const textModelId = 'text_model_id';
  static const textToSpeechServiceId = 'text_to_speech_service_id';
  static const textToSpeechModelId = 'text_to_speech_model_id';
  static const textToSpeechVoiceId = 'text_to_speech_voice_id';
  static const speechToTextServiceId = 'speech_to_text_service_id';
  static const speechToTextModelId = 'speech_to_text_model_id';
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
      options: OpenDatabaseOptions(
        version: 1,
        onCreate: _createDB,
        onOpen: (db) async {
          await db.execute('PRAGMA foreign_keys = ON;');
        },
      ),
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
        ${ColumnName.textConfigId} INTEGER NOT NULL,
        ${ColumnName.key} TEXT NOT NULL,
        ${ColumnName.value} TEXT NOT NULL,
        UNIQUE (${ColumnName.textConfigId}, ${ColumnName.key}),
        FOREIGN KEY (${ColumnName.textConfigId}) REFERENCES ${TableName.textConfig}(${ColumnName.id}) ON DELETE CASCADE
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
      CREATE TABLE ${TableName.textToSpeechModel} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.textToSpeechConfigId} INTEGER NOT NULL,
        ${ColumnName.key} TEXT NOT NULL,
        ${ColumnName.value} TEXT NOT NULL,
        UNIQUE (${ColumnName.textToSpeechConfigId}, ${ColumnName.key}),
        FOREIGN KEY (${ColumnName.textToSpeechConfigId}) REFERENCES ${TableName.textToSpeechConfig}(${ColumnName.id}) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE ${TableName.textToSpeechVoice} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.textToSpeechConfigId} INTEGER NOT NULL,
        ${ColumnName.key} TEXT NOT NULL,
        ${ColumnName.value} TEXT NOT NULL,
        UNIQUE (${ColumnName.textToSpeechConfigId}, ${ColumnName.key}),
        FOREIGN KEY (${ColumnName.textToSpeechConfigId}) REFERENCES ${TableName.textToSpeechConfig}(${ColumnName.id}) ON DELETE CASCADE
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
        ${ColumnName.speechToTextConfigId} INTEGER NOT NULL,
        ${ColumnName.key} TEXT NOT NULL,
        ${ColumnName.value} TEXT NOT NULL,
        UNIQUE (${ColumnName.speechToTextConfigId}, ${ColumnName.key}),
        FOREIGN KEY (${ColumnName.speechToTextConfigId}) REFERENCES ${TableName.speechToTextConfig}(${ColumnName.id}) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE ${TableName.agentConfig} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.name} TEXT NOT NULL,
        ${ColumnName.imageKey} TEXT NOT NULL,
        ${ColumnName.textServiceId} INTEGER NOT NULL,
        ${ColumnName.textModelId} INTEGER NOT NULL,
        ${ColumnName.textToSpeechServiceId} INTEGER NOT NULL,
        ${ColumnName.textToSpeechModelId} INTEGER NOT NULL,
        ${ColumnName.textToSpeechVoiceId} INTEGER NOT NULL,
        ${ColumnName.speechToTextServiceId} INTEGER NOT NULL,
        ${ColumnName.speechToTextModelId} INTEGER NOT NULL,
        FOREIGN KEY (${ColumnName.textServiceId}) REFERENCES ${TableName.serviceConfig}(${ColumnName.id}) ON DELETE RESTRICT,
        FOREIGN KEY (${ColumnName.textModelId}) REFERENCES ${TableName.textModel}(${ColumnName.id}) ON DELETE RESTRICT,
        FOREIGN KEY (${ColumnName.speechToTextServiceId}) REFERENCES ${TableName.serviceConfig}(${ColumnName.id}) ON DELETE RESTRICT,
        FOREIGN KEY (${ColumnName.speechToTextModelId}) REFERENCES ${TableName.speechToTextModel}(${ColumnName.id}) ON DELETE RESTRICT,
        FOREIGN KEY (${ColumnName.textToSpeechServiceId}) REFERENCES ${TableName.serviceConfig}(${ColumnName.id}) ON DELETE RESTRICT,
        FOREIGN KEY (${ColumnName.textToSpeechModelId}) REFERENCES ${TableName.textToSpeechModel}(${ColumnName.id}) ON DELETE RESTRICT,
        FOREIGN KEY (${ColumnName.textToSpeechVoiceId}) REFERENCES ${TableName.textToSpeechVoice}(${ColumnName.id}) ON DELETE RESTRICT
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

  Future<List<ServiceConfig>> queryAllServiceConfig() async {
    final db = await database;
    return await _queryServiceConfigs(db, '', []);
  }

  Future<List<ServiceConfig>> queryTextServiceConfig() async {
    final db = await database;
    return await _queryServiceConfigs(
      db,
      'tc.${ColumnName.id} IS NOT NULL',
      [],
    );
  }

  Future<List<ServiceConfig>> querySpeechToTextServiceConfig() async {
    final db = await database;
    return await _queryServiceConfigs(
      db,
      'sttc.${ColumnName.id} IS NOT NULL',
      [],
    );
  }

  Future<List<ServiceConfig>> queryTextToSpeechServiceConfig() async {
    final db = await database;
    return await _queryServiceConfigs(
      db,
      'ttsc.${ColumnName.id} IS NOT NULL',
      [],
    );
  }

  Future<int> insertAgentConfig(AgentConfig config) async {
    final db = await database;
    return await db.transaction((txn) async {
      return await _insertAgentConfig(txn, config);
    });
  }

  Future<bool> updateAgentConfig(AgentConfig config) async {
    final db = await database;
    return await db.transaction((txn) async {
      return await _updateAgentConfig(txn, config);
    });
  }

  Future<bool> deleteAgentConfig(int configId) async {
    final db = await database;
    final int rowsAffected = await db.delete(
      TableName.agentConfig,
      where: '${ColumnName.id} = ?',
      whereArgs: [configId],
    );
    return rowsAffected > 0;
  }

  Future<List<AgentConfig>> queryAllAgentConfig() async {
    final db = await database;
    return _queryAgentConfigs(db);
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
        final int modelId = await txn.insert(TableName.textModel,
            model.toDatabaseMap(ColumnName.textConfigId, textConfigId));
        if (modelId == 0) return -1;
      }
    }

    if (serviceConfig.textToSpeechConfig != null) {
      final int textToSpeechConfigId = await txn.insert(
          TableName.textToSpeechConfig,
          serviceConfig.textToSpeechConfig!.toDatabaseMap(serviceConfigId));
      if (textToSpeechConfigId == 0) return -1;

      for (var model in serviceConfig.textToSpeechConfig!.models) {
        final modelId = await txn.insert(
            TableName.textToSpeechModel,
            model.toDatabaseMap(
                ColumnName.textToSpeechConfigId, textToSpeechConfigId));
        if (modelId == 0) return -1;
      }

      for (var voice in serviceConfig.textToSpeechConfig!.voices) {
        final voiceId = await txn.insert(
            TableName.textToSpeechVoice,
            voice.toDatabaseMap(
                ColumnName.textToSpeechConfigId, textToSpeechConfigId));
        if (voiceId == 0) return -1;
      }
    }

    if (serviceConfig.speechToTextConfig != null) {
      final int speechToTextConfigId = await txn.insert(
          TableName.speechToTextConfig,
          serviceConfig.speechToTextConfig!.toDatabaseMap(serviceConfigId));
      if (speechToTextConfigId == 0) return -1;

      for (var model in serviceConfig.speechToTextConfig!.models) {
        final modelId = await txn.insert(
            TableName.speechToTextModel,
            model.toDatabaseMap(
                ColumnName.speechToTextConfigId, speechToTextConfigId));
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
          ColumnName.textConfigId,
          textConfigId,
          textConfig.models,
        );
        if (!result) return false;
      } else {
        textConfigId = await txn.insert(TableName.textConfig,
            {ColumnName.serviceConfigId: serviceConfigId});
        if (textConfigId == 0) return false;

        for (var model in textConfig.models) {
          final modelId = await txn.insert(TableName.textModel,
              model.toDatabaseMap(ColumnName.textConfigId, textConfigId));
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

        final modelResult = await _updateKeyValuePairList(
          txn,
          TableName.textToSpeechModel,
          ColumnName.textToSpeechConfigId,
          textToSpeechConfigId,
          textToSpeechConfig.models,
        );
        if (!modelResult) return false;

        final voiceResult = await _updateKeyValuePairList(
          txn,
          TableName.textToSpeechVoice,
          ColumnName.textToSpeechConfigId,
          textToSpeechConfigId,
          textToSpeechConfig.voices,
        );
        if (!voiceResult) return false;
      } else {
        textToSpeechConfigId = await txn.insert(TableName.textToSpeechConfig,
            {ColumnName.serviceConfigId: serviceConfigId});
        if (textToSpeechConfigId == 0) return false;

        for (var voice in textToSpeechConfig.voices) {
          final voiceId = await txn.insert(
              TableName.textToSpeechVoice,
              voice.toDatabaseMap(
                  ColumnName.textToSpeechConfigId, textToSpeechConfigId));
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
          ColumnName.speechToTextConfigId,
          speechToTextConfigId,
          speechToTextConfig.models,
        );
        if (!result) return false;
      } else {
        speechToTextConfigId = await txn.insert(TableName.speechToTextConfig,
            {ColumnName.serviceConfigId: serviceConfigId});
        if (speechToTextConfigId == 0) return false;

        for (var model in speechToTextConfig.models) {
          final modelId = await txn.insert(
              TableName.speechToTextModel,
              model.toDatabaseMap(
                  ColumnName.speechToTextConfigId, speechToTextConfigId));
          if (modelId == 0) return false;
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
    String parentIdColumnName,
    int parentId,
    List<KeyValuePair> newList,
  ) async {
    final List<Map<String, dynamic>> existingItems = await txn.query(
      tableName,
      where: '$parentIdColumnName = ?',
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
        final itemMap = newItem.toDatabaseMap(parentIdColumnName, parentId);
        itemMap[parentIdColumnName] = parentId;
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

  Future<List<ServiceConfig>> _queryServiceConfigs(
      Database db, String where, List<dynamic> whereArgs) async {
    final List<Map<String, dynamic>> serviceConfigs = await db.rawQuery('''
    SELECT sc.*, 
           tc.${ColumnName.id} as ${ColumnName.textConfigId}, 
           ttsc.${ColumnName.id} as ${ColumnName.textToSpeechConfigId}, 
           sttc.${ColumnName.id} as ${ColumnName.speechToTextConfigId}
    FROM ${TableName.serviceConfig} sc
    LEFT JOIN ${TableName.textConfig} tc ON sc.${ColumnName.id} = tc.${ColumnName.serviceConfigId}
    LEFT JOIN ${TableName.textToSpeechConfig} ttsc ON sc.${ColumnName.id} = ttsc.${ColumnName.serviceConfigId}
    LEFT JOIN ${TableName.speechToTextConfig} sttc ON sc.${ColumnName.id} = sttc.${ColumnName.serviceConfigId}
    ${where.isNotEmpty ? 'WHERE $where' : ''} 
  ''', whereArgs);
    final List<ServiceConfig> results = [];
    for (var scRow in serviceConfigs) {
      final serviceConfig = ServiceConfig.fromJson(scRow);
      TextConfig? textConfig;
      if (scRow[ColumnName.textConfigId] != null) {
        final int textConfigId = scRow[ColumnName.textConfigId] as int;
        final List<Map<String, dynamic>> textModelRows = await db.query(
          TableName.textModel,
          where: '${ColumnName.textConfigId} = ?',
          whereArgs: [textConfigId],
        );
        final models =
            textModelRows.map((tmRow) => KeyValuePair.fromJson(tmRow)).toList();
        textConfig = TextConfig(
          id: textConfigId,
          models: models,
        );
      }
      TextToSpeechConfig? textToSpeechConfig;
      if (scRow[ColumnName.textToSpeechConfigId] != null) {
        final int textToSpeechConfigId =
            scRow[ColumnName.textToSpeechConfigId] as int;
        final List<Map<String, dynamic>> modelRows = await db.query(
          TableName.textToSpeechModel,
          where: '${ColumnName.textToSpeechConfigId} = ?',
          whereArgs: [textToSpeechConfigId],
        );
        final models =
            modelRows.map((vRow) => KeyValuePair.fromJson(vRow)).toList();

        final List<Map<String, dynamic>> voiceRows = await db.query(
          TableName.textToSpeechVoice,
          where: '${ColumnName.textToSpeechConfigId} = ?',
          whereArgs: [textToSpeechConfigId],
        );
        final voices =
            voiceRows.map((vRow) => KeyValuePair.fromJson(vRow)).toList();
        textToSpeechConfig = TextToSpeechConfig(
          id: textToSpeechConfigId,
          models: models,
          voices: voices,
        );
      }
      SpeechToTextConfig? speechToTextConfig;
      if (scRow[ColumnName.speechToTextConfigId] != null) {
        final int speechToTextConfigId =
            scRow[ColumnName.speechToTextConfigId] as int;
        final List<Map<String, dynamic>> modelRows = await db.query(
          TableName.speechToTextModel,
          where: '${ColumnName.speechToTextConfigId} = ?',
          whereArgs: [speechToTextConfigId],
        );
        final models =
            modelRows.map((mRow) => KeyValuePair.fromJson(mRow)).toList();
        speechToTextConfig = SpeechToTextConfig(
          id: speechToTextConfigId,
          models: models,
        );
      }
      final completeServiceConfig = serviceConfig.copyWith(
        textConfig: textConfig,
        textToSpeechConfig: textToSpeechConfig,
        speechToTextConfig: speechToTextConfig,
      );
      results.add(completeServiceConfig);
    }
    return results;
  }

  Future<List<KeyValuePair>> _queryTextModels(
      Database db, String where, List<dynamic> whereArgs) async {
    final List<Map<String, dynamic>> textModels = await db.rawQuery('''
    SELECT * FROM ${TableName.textModel}
    ${where.isNotEmpty ? 'WHERE $where' : ''} 
  ''', whereArgs);
    final List<KeyValuePair> results = [];
    for (var scRow in textModels) {
      results.add(KeyValuePair.fromJson(scRow));
    }
    return results;
  }

  Future<List<KeyValuePair>> _querySpeechToTextModels(
      Database db, String where, List<dynamic> whereArgs) async {
    final List<Map<String, dynamic>> speechToTextModels = await db.rawQuery('''
    SELECT * FROM ${TableName.speechToTextModel}
    ${where.isNotEmpty ? 'WHERE $where' : ''} 
  ''', whereArgs);
    final List<KeyValuePair> results = [];
    for (var scRow in speechToTextModels) {
      results.add(KeyValuePair.fromJson(scRow));
    }
    return results;
  }

  Future<List<KeyValuePair>> _queryTextToSpeechModels(
      Database db, String where, List<dynamic> whereArgs) async {
    final List<Map<String, dynamic>> textToSpeechModels = await db.rawQuery('''
    SELECT * FROM ${TableName.textToSpeechModel}
    ${where.isNotEmpty ? 'WHERE $where' : ''} 
  ''', whereArgs);
    final List<KeyValuePair> results = [];
    for (var scRow in textToSpeechModels) {
      results.add(KeyValuePair.fromJson(scRow));
    }
    return results;
  }

  Future<List<KeyValuePair>> _queryTextToSpeechVoices(
      Database db, String where, List<dynamic> whereArgs) async {
    final List<Map<String, dynamic>> textToSpeechVoices = await db.rawQuery('''
    SELECT * FROM ${TableName.textToSpeechVoice}
    ${where.isNotEmpty ? 'WHERE $where' : ''} 
  ''', whereArgs);
    final List<KeyValuePair> results = [];
    for (var scRow in textToSpeechVoices) {
      results.add(KeyValuePair.fromJson(scRow));
    }
    return results;
  }

  Future<int> _insertAgentConfig(
      Transaction txn, AgentConfig agentConfig) async {
    final int agentConfigId = await txn.insert(
      TableName.agentConfig,
      agentConfig.toDatabaseMap(),
    );
    if (agentConfigId == 0) return -1;
    return agentConfigId;
  }

  Future<bool> _updateAgentConfig(
      Transaction txn, AgentConfig agentConfig) async {
    final int agentConfigId = agentConfig.id!;
    final updateAgentConfig = await txn.update(
      TableName.agentConfig,
      agentConfig.toDatabaseMap(),
      where: '${ColumnName.id} = ?',
      whereArgs: [agentConfigId],
    );
    if (updateAgentConfig == 0) return false;
    return true;
  }

  Future<List<AgentConfig>> _queryAgentConfigs(Database db) async {
    final List<Map<String, dynamic>> rows = await db.rawQuery('''
    SELECT 
      ac.${ColumnName.id} AS ${ColumnName.id},
      ac.${ColumnName.name} AS ${ColumnName.name},
      ac.${ColumnName.imageKey} AS ${ColumnName.imageKey},
      tsc.${ColumnName.id} AS  ${ColumnName.textServiceId},
      tmodel.${ColumnName.id} AS ${ColumnName.textModelId},
      stsc.${ColumnName.id} AS ${ColumnName.speechToTextServiceId},
      stmodel.${ColumnName.id} AS ${ColumnName.speechToTextModelId},
      ttsc.${ColumnName.id} AS ${ColumnName.textToSpeechServiceId},
      ttsmodel.${ColumnName.id} AS ${ColumnName.textToSpeechModelId},
      ttsvoice.${ColumnName.id} AS ${ColumnName.textToSpeechVoiceId}
    FROM ${TableName.agentConfig} ac
    LEFT JOIN ${TableName.serviceConfig} tsc ON ac.${ColumnName.textServiceId} = tsc.${ColumnName.id}
    LEFT JOIN ${TableName.textModel} tmodel ON ac.${ColumnName.textModelId} = tmodel.${ColumnName.id}
    LEFT JOIN ${TableName.serviceConfig} stsc ON ac.${ColumnName.speechToTextServiceId} = stsc.${ColumnName.id}
    LEFT JOIN ${TableName.speechToTextModel} stmodel ON ac.${ColumnName.speechToTextModelId} = stmodel.${ColumnName.id}
    LEFT JOIN ${TableName.serviceConfig} ttsc ON ac.${ColumnName.textToSpeechServiceId} = ttsc.${ColumnName.id}
    LEFT JOIN ${TableName.textToSpeechModel} ttsmodel ON ac.${ColumnName.textToSpeechModelId} = ttsmodel.${ColumnName.id}
    LEFT JOIN ${TableName.textToSpeechVoice} ttsvoice ON ac.${ColumnName.textToSpeechVoiceId} = ttsvoice.${ColumnName.id}
  ''');
    final List<AgentConfig> agentConfigs = [];
    for (final row in rows) {
      final textServiceConfig = await _queryServiceConfigs(
              db, 'sc.${ColumnName.id} = ?', [row[ColumnName.textServiceId]])
          .then((v) => v.first);

      final textModel = await _queryTextModels(
              db, '${ColumnName.id} = ?', [row[ColumnName.textModelId]])
          .then((v) => v.first);
      final speechToTextServiceConfig = await _queryServiceConfigs(
          db,
          'sc.${ColumnName.id} = ?',
          [row[ColumnName.speechToTextServiceId]]).then((v) => v.first);
      final speechToTextModel = await _querySpeechToTextModels(
              db, '${ColumnName.id} = ?', [row[ColumnName.speechToTextModelId]])
          .then((v) => v.first);
      final textToSpeechServiceConfig = await _queryServiceConfigs(
          db,
          'sc.${ColumnName.id} = ?',
          [row[ColumnName.textToSpeechServiceId]]).then((v) => v.first);
      final textToSpeechModel = await _queryTextToSpeechModels(
              db, '${ColumnName.id} = ?', [row[ColumnName.textToSpeechModelId]])
          .then((v) => v.first);
      final textToSpeechVoice = await _queryTextToSpeechVoices(
              db, '${ColumnName.id} = ?', [row[ColumnName.textToSpeechVoiceId]])
          .then((v) => v.first);
      final agentConfig = AgentConfig(
        id: row[ColumnName.id] as int,
        name: row[ColumnName.name] as String,
        imagekey: row[ColumnName.imageKey] as String,
        textServiceConfig: textServiceConfig,
        textModel: textModel,
        speechToTextServiceConfig: speechToTextServiceConfig,
        speechToTextModel: speechToTextModel,
        textToSpeechServiceConfig: textToSpeechServiceConfig,
        textToSpeechModel: textToSpeechModel,
        textToSpeechVoice: textToSpeechVoice,
      );
      agentConfigs.add(agentConfig);
    }
    return agentConfigs;
  }
}
