import 'package:formz/formz.dart';

enum JoinCodeError { empty, length, format }

class JoinCode extends FormzInput<String, JoinCodeError> {
  const JoinCode.pure() : super.pure('');

  const JoinCode.dirty(super.value) : super.dirty();

  String? get errorMessage {
    if (isValid || isPure) return null;

    if (displayError == JoinCodeError.empty) return 'El codigo es requerido';
    if (displayError == JoinCodeError.length) {
      return 'El codigo debe tener 6 caracteres';
    }
    if (displayError == JoinCodeError.format) {
      return 'El codigo solo permite letras y numeros';
    }

    return null;
  }

  @override
  JoinCodeError? validator(String value) {
    final normalizedCode = value.trim().toUpperCase();

    if (normalizedCode.isEmpty) return JoinCodeError.empty;
    if (normalizedCode.length != 6) return JoinCodeError.length;
    if (!RegExp(r'^[A-Z0-9]+$').hasMatch(normalizedCode)) {
      return JoinCodeError.format;
    }

    return null;
  }
}
