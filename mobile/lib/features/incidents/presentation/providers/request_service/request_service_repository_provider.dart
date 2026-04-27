import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/auth/auth.dart';
import 'package:mobile/features/incidents/data/data.dart';

final incidentApiProvider = Provider<IncidentApi>((ref) {
  final accessToken = ref.watch(
    authProvider.select((state) => state.user?.token ?? ''),
  );
  return IncidentApi(accessToken: accessToken);
});

final incidentRepositoryProvider = Provider<IncidentRepository>((ref) {
  final incidentApi = ref.watch(incidentApiProvider);
  return IncidentRepository(incidentApi: incidentApi);
});
