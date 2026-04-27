class BoliviaDateTimeFormatter {
  static const _utcOffsetHours = -4;

  static DateTime toBoliviaTime(DateTime value) {
    final utc = value.toUtc();
    return utc.add(const Duration(hours: _utcOffsetHours));
  }

  static String toBoliviaDateTimeLabel(DateTime value) {
    final dateTime = toBoliviaTime(value);

    final day = dateTime.day.toString().padLeft(2, '0');
    final month = dateTime.month.toString().padLeft(2, '0');
    final year = dateTime.year.toString();
    final hour = dateTime.hour.toString().padLeft(2, '0');
    final minute = dateTime.minute.toString().padLeft(2, '0');

    return '$day/$month/$year $hour:$minute';
  }

  static String toBoliviaDateLabel(DateTime value) {
    final dateTime = toBoliviaTime(value);

    final day = dateTime.day.toString().padLeft(2, '0');
    final month = dateTime.month.toString().padLeft(2, '0');
    final year = dateTime.year.toString();

    return '$day/$month/$year';
  }
}
