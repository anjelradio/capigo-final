class BoliviaDateTimeFormatter {
  static const _utcOffsetHours = -4;
  static final RegExp _timezoneSuffixRegExp = RegExp(
    r'(?:Z|[+-]\d{2}:?\d{2})$',
    caseSensitive: false,
  );

  static DateTime? parseServerDateTime(dynamic value) {
    if (value == null) return null;

    final raw = '$value'.trim();
    if (raw.isEmpty) return null;

    final parsed = DateTime.tryParse(raw);
    if (parsed == null) return null;

    if (_timezoneSuffixRegExp.hasMatch(raw)) {
      return parsed.toUtc();
    }

    return DateTime.utc(
      parsed.year,
      parsed.month,
      parsed.day,
      parsed.hour,
      parsed.minute,
      parsed.second,
      parsed.millisecond,
      parsed.microsecond,
    );
  }

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
