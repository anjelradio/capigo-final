import 'package:formz/formz.dart';

enum NameError { empty, length }

class Name extends FormzInput<String, NameError> {
  const Name.pure() : super.pure('');

  const Name.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isValid || isPure) return null;
    if (displayError == NameError.empty) return 'El campo es requerido';
    if (displayError == NameError.length) return 'Mínimo 3 caracteres';
    return null;
  }

  @override
  NameError? validator(String value) {
    final trimmedValue = value.trim();
    if (trimmedValue.isEmpty) return NameError.empty;
    if (trimmedValue.length < 3) return NameError.length;
    return null;
  }
}
