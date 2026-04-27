import 'package:formz/formz.dart';

enum PhoneError { empty, length, format }

class Phone extends FormzInput<String, PhoneError> {

  // Solo números, exactamente 8 dígitos
  static final RegExp phoneRegExp = RegExp(r'^\d{8}$');

  const Phone.pure() : super.pure('');
  const Phone.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isValid || isPure) return null;

    if (displayError == PhoneError.empty) {
      return 'El número es requerido';
    }
    if (displayError == PhoneError.length) {
      return 'Debe tener exactamente 8 dígitos';
    }
    if (displayError == PhoneError.format) {
      return 'Solo se permiten números';
    }

    return null;
  }

  @override
  PhoneError? validator(String value) {
    final trimmed = value.trim();

    if (trimmed.isEmpty) return PhoneError.empty;
    if (trimmed.length != 8) return PhoneError.length;
    if (!RegExp(r'^\d+$').hasMatch(trimmed)) return PhoneError.format;

    return null;
  }
}