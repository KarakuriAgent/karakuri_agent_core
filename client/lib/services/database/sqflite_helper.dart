import 'package:flutter/foundation.dart';
import 'package:karakuri_agent/models/agent_config.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';

class TableName {
  static const agentConfig = 'agent_config';
}

class ColumnName {
  static const id = 'id';
  static const name = 'name';
  static const imageKey = 'image_key';
  static const baseUrl = 'base_url';
  static const apiKey = 'api_key';
  static const agentId = 'agent_id';
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
      CREATE TABLE ${TableName.agentConfig} (
        ${ColumnName.id} INTEGER PRIMARY KEY AUTOINCREMENT,
        ${ColumnName.name} TEXT NOT NULL,
        ${ColumnName.baseUrl} TEXT NOT NULL,
        ${ColumnName.apiKey} TEXT NOT NULL,
        ${ColumnName.imageKey} TEXT NOT NULL,
        ${ColumnName.agentId} TEXT NOT NULL
      )
    ''');
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
    final List<Map<String, dynamic>> rows =
        await db.query(TableName.agentConfig);
    return rows.map((it) => AgentConfig.fromDatabaseMap(it)).toList();
  }
}
