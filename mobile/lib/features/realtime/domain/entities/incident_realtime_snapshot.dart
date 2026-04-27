class IncidentRealtimeSnapshot {
  IncidentRealtimeSnapshot({
    required this.incidentId,
    required this.status,
    this.assignmentId,
    this.repairShopId,
    this.mechanicId,
    this.mechanicLatitude,
    this.mechanicLongitude,
    this.mechanicLocationUpdatedAt,
    this.lastEventAt,
  });

  final String incidentId;
  final String status;
  final String? assignmentId;
  final String? repairShopId;
  final String? mechanicId;
  final double? mechanicLatitude;
  final double? mechanicLongitude;
  final DateTime? mechanicLocationUpdatedAt;
  final DateTime? lastEventAt;
}
