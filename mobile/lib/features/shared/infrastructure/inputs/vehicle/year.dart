import 'package:formz/formz.dart';

enum VehicleYearError { empty, range, format }

class VehicleYear extends FormzInput<String, VehicleYearError> {
  const VehicleYear.pure() : super.pure('');

  const VehicleYear.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isValid || isPure) return null;
    if (displayError == VehicleYearError.empty) return 'El anio es requerido';
    if (displayError == VehicleYearError.format) {
      return 'El anio debe ser numerico';
    }
    if (displayError == VehicleYearError.range) {
      final maxAllowed = DateTime.now().year + 1;
      return 'El anio debe estar entre 1900 y $maxAllowed';
    }
    return null;
  }

  int? get valueAsInt => int.tryParse(value.trim());

  @override
  VehicleYearError? validator(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) return VehicleYearError.empty;

    final parsed = int.tryParse(trimmed);
    if (parsed == null) return VehicleYearError.format;

    final maxAllowed = DateTime.now().year + 1;
    if (parsed < 1900 || parsed > maxAllowed) return VehicleYearError.range;

    return null;
  }
}
