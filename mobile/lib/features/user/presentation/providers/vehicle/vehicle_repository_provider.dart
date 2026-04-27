import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/user/data/data.dart';

final vehicleApiProvider = Provider<VehicleApi>((ref) {
  final accessToken = ref.watch(
    authProvider.select((state) => state.user?.token ?? ''),
  );

  return VehicleApi(accessToken: accessToken);
});

final vehicleRepositoryProvider = Provider<VehicleRepository>((ref) {
  final vehicleApi = ref.watch(vehicleApiProvider);
  return VehicleRepository(vehicleApi: vehicleApi);
});
