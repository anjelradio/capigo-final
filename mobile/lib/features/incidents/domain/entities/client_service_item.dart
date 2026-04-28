class ClientServiceItem {
  ClientServiceItem({
    required this.incidentId,
    required this.status,
    required this.createdDate,
    required this.updatedDate,
    this.description,
    this.problemName,
    this.vehiclePlate,
  });

  final String incidentId;
  final String status;
  final DateTime createdDate;
  final DateTime updatedDate;
  final String? description;
  final String? problemName;
  final String? vehiclePlate;
}
