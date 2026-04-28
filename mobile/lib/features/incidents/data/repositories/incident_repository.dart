import 'package:mobile/features/incidents/data/api/incident_api.dart';
import 'package:mobile/features/incidents/data/mappers/mappers.dart';
import 'package:mobile/features/incidents/domain/domain.dart';
import 'package:mobile/features/auth/data/errors/auth_errors.dart';

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

  Future<void> submitIncidentFeedback({
    required String incidentId,
    required int rating,
    String? comment,
  }) async {
    await _incidentApi.submitIncidentFeedback(
      incidentId: incidentId,
      rating: rating,
      comment: comment,
    );
  }

  Future<List<PendingFeedbackReminder>> getPendingFeedbackReminders() async {
    final json = await _incidentApi.getPendingFeedbackReminders();
    return IncidentMapper.pendingFeedbackRemindersFromJson(json);
  }

  Future<List<ClientServiceItem>> getCompletedServices() async {
    final json = await _incidentApi.getCompletedServices();
    return IncidentMapper.clientServiceItemsFromJson(json);
  }

  Future<List<ClientServiceItem>> getServicesHistory() async {
    final json = await _incidentApi.getServicesHistory();
    return IncidentMapper.clientServiceItemsFromJson(json);
  }

  Future<ClientServiceDetail> getServiceDetail({
    required String incidentId,
  }) async {
    final json = await _incidentApi.getServiceDetail(incidentId: incidentId);
    if (json == null) {
      throw CustomError('No fue posible cargar el detalle del servicio');
    }
    return IncidentMapper.clientServiceDetailFromJson(json);
  }
}
