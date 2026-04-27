import 'package:mobile/features/incidents/data/api/incident_api.dart';
import 'package:mobile/features/incidents/data/mappers/mappers.dart';
import 'package:mobile/features/incidents/domain/domain.dart';

class IncidentRepository {
  IncidentRepository({required IncidentApi incidentApi})
    : _incidentApi = incidentApi;

  final IncidentApi _incidentApi;

  Future<void> createIncident({
    required String vehicleId,
    String? description,
    String? audioPath,
    required double latitude,
    required double longitude,
    required List<String> imagePaths,
  }) {
    return _incidentApi.createIncident(
      vehicleId: vehicleId,
      description: description,
      audioPath: audioPath,
      latitude: latitude,
      longitude: longitude,
      imagePaths: imagePaths,
    );
  }

  Future<ActiveIncidentDetail?> getActiveIncidentDetail() async {
    final json = await _incidentApi.getActiveIncidentDetail();
    if (json == null) return null;
    return IncidentMapper.activeIncidentJsonToEntity(json);
  }
}
