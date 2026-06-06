class OfflineIncidentSubmission {
  OfflineIncidentSubmission({
    required this.clientRequestId,
    required this.vehicleId,
    required this.latitude,
    required this.longitude,
    required this.imagePaths,
    required this.createdAt,
    this.description,
    this.audioPath,
  });

  final String clientRequestId;
  final String vehicleId;
  final String? description;
  final String? audioPath;
  final List<String> imagePaths;
  final double latitude;
  final double longitude;
  final DateTime createdAt;

  Map<String, dynamic> toJson() {
    return {
      'client_request_id': clientRequestId,
      'vehicle_id': vehicleId,
      'description': description,
      'audio_path': audioPath,
      'image_paths': imagePaths,
      'latitude': latitude,
      'longitude': longitude,
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory OfflineIncidentSubmission.fromJson(Map<String, dynamic> json) {
    return OfflineIncidentSubmission(
      clientRequestId: (json['client_request_id'] as String? ?? '').trim(),
      vehicleId: (json['vehicle_id'] as String? ?? '').trim(),
      description: json['description'] as String?,
      audioPath: json['audio_path'] as String?,
      imagePaths: (json['image_paths'] as List<dynamic>? ?? const [])
          .map((item) => item.toString())
          .toList(),
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      createdAt: DateTime.tryParse(json['created_at']?.toString() ?? '') ?? DateTime.now(),
    );
  }
}
