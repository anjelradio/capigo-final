class WrongCredentials implements Exception {}

class InvalidToken implements Exception {}

class ConnectionTimeOut {}

class CustomError implements Exception {
  final List<String> messages;

  String get message => messages.first;

  CustomError(String message) : messages = [message];

  CustomError.multiple(List<String> messages)
    : messages = messages.isEmpty ? ['Error desconocido'] : messages;
}
