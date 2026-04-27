import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/user/data/data.dart';

final userApiProvider = Provider<UserApi>((ref) {
  final keyValueStorageService = ref.watch(keyValueStorageProvider);
  return UserApi(keyValueStorageService: keyValueStorageService);
});

final userRepositoryProvider = Provider<UserRepository>((ref) {
  final userApi = ref.watch(userApiProvider);
  return UserRepository(userApi: userApi);
});
