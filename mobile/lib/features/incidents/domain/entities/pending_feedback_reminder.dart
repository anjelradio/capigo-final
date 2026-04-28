class PendingFeedbackReminder {
  PendingFeedbackReminder({
    required this.incidentId,
    required this.description,
    this.problemName,
    this.completedAt,
  });

  final String incidentId;
  final String description;
  final String? problemName;
  final DateTime? completedAt;
}
