import 'package:mobile/features/assignments/data/api/mechanic_assignment_api.dart';
import 'package:mobile/features/assignments/data/mappers/mechanic_assignment_mapper.dart';
import 'package:mobile/features/assignments/domain/domain.dart';

class MechanicAssignmentRepository {
  MechanicAssignmentRepository({required MechanicAssignmentApi mechanicApi})
    : _mechanicApi = mechanicApi;

  final MechanicAssignmentApi _mechanicApi;

  Future<MechanicAssignment?> getMyActiveAssignment() async {
    final json = await _mechanicApi.getMyActiveAssignment();
    return MechanicAssignmentMapper.activeAssignmentFromJson(json);
  }

  Future<MechanicAssignment> getAssignmentDetail(String assignmentId) async {
    final json = await _mechanicApi.getAssignmentDetail(assignmentId);
    return MechanicAssignmentMapper.assignmentFromJson(json ?? {});
  }

  Future<MechanicAssignmentActionResult> updateAssignmentStatus({
    required String assignmentId,
    required String status,
  }) async {
    final json = await _mechanicApi.updateAssignmentStatus(
      assignmentId: assignmentId,
      status: status,
    );
    return MechanicAssignmentMapper.actionResultFromJson(json);
  }

  Future<MechanicAssignmentActionResult> updateAssignmentLocation({
    required String assignmentId,
    required double latitude,
    required double longitude,
    DateTime? recordedAt,
  }) async {
    final json = await _mechanicApi.updateAssignmentLocation(
      assignmentId: assignmentId,
      latitude: latitude,
      longitude: longitude,
      recordedAt: recordedAt,
    );
    return MechanicAssignmentMapper.actionResultFromJson(json);
  }

  Future<MechanicTodayStats> getTodayStats() async {
    final json = await _mechanicApi.getTodayStats();
    return MechanicAssignmentMapper.todayStatsFromJson(json);
  }
}
