import 'package:shared_preferences/shared_preferences.dart';

import 'key_value_storage_service.dart';

class KeyValueStorageServiceImpl extends KeyValueStorageService {
  Future<SharedPreferences> getSharedPrefers() async {
    return await SharedPreferences.getInstance();
  }

  @override
  Future<T?> getValue<T>(String key) async {
    final prefers = await getSharedPrefers();

    switch (T) {
      case int:
        return prefers.getInt(key) as T?;
      case String:
        return prefers.getString(key) as T?;
      default:
        throw UnimplementedError(
          'Get not implemented for type ${T.runtimeType}',
        );
    }
  }

  @override
  Future<bool> removeKey(String key) async {
    final prefers = await getSharedPrefers();
    return await prefers.remove(key);
  }

  @override
  Future<void> setKeyValue<T>(String key, T value) async {
    final prefers = await getSharedPrefers();

    switch (T) {
      case int:
        prefers.setInt(key, value as int);
        break;
      case String:
        prefers.setString(key, value as String);
        break;
      default:
        throw UnimplementedError(
          'Set not implemented for type ${T.runtimeType}',
        );
    }
  }
}
