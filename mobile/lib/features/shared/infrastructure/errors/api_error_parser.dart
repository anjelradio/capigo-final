List<String> parseApiErrors(dynamic error) {
  if (error == null) return const ['Error desconocido'];

  if (error is String) {
    return [error];
  }

  if (error is! Map) {
    return const ['Error desconocido'];
  }

  final detail = error['detail'];

  if (detail is String && detail.trim().isNotEmpty) {
    return [detail];
  }

  if (detail is List) {
    final messages = detail
        .map((item) {
          if (item is Map && item['msg'] is String) {
            return item['msg'] as String;
          }

          if (item is String) return item;

          return '';
        })
        .where((message) => message.trim().isNotEmpty)
        .toList();

    if (messages.isNotEmpty) return messages;
  }

  return const ['Error desconocido'];
}
