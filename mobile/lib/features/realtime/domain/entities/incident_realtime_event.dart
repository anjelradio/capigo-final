class IncidentRealtimeEvent {
  IncidentRealtimeEvent({
    required this.id,
    required this.type,
    required this.createdAt,
    required this.payload,
  });

  final String id;
  final String type;
  final DateTime createdAt;
  final Map<String, dynamic> payload;
}
