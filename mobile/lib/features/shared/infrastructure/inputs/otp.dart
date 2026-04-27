import 'package:formz/formz.dart';

enum OtpError { empty, length, format }

class Otp extends FormzInput<String, OtpError> {
  const Otp.pure() : super.pure('');

  const Otp.dirty(super.value) : super.dirty();

  String? get errorMessage {
    if (isValid || isPure) return null;
    if (displayError == OtpError.empty) {
      return 'El codigo OTP es requerido';
    }
    if (displayError == OtpError.length) {
      return 'El codigo OTP debe tener 6 digitos';
    }
    if (displayError == OtpError.format) {
      return 'El codigo OTP solo debe contener numeros';
    }
    return null;
  }

  @override
  OtpError? validator(String value) {
    final trimmedValue = value.trim();
    if (trimmedValue.isEmpty) return OtpError.empty;
    if (trimmedValue.length != 6) return OtpError.length;
    if (!RegExp(r'^\d+$').hasMatch(trimmedValue)) return OtpError.format;
    return null;
  }
}
