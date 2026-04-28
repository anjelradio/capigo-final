import 'package:flutter_riverpod/legacy.dart';
import 'package:formz/formz.dart';

final mechanicCompletionFormProvider =
    StateNotifierProvider.autoDispose<
      MechanicCompletionFormNotifier,
      MechanicCompletionFormState
    >((ref) {
      return MechanicCompletionFormNotifier();
    });

class MechanicCompletionFormNotifier
    extends StateNotifier<MechanicCompletionFormState> {
  MechanicCompletionFormNotifier() : super(MechanicCompletionFormState());

  void onDescriptionChanged(String value) {
    final description = ServiceReportDescription.dirty(value);
    state = state.copyWith(
      description: description,
      errorMessages: const [],
      isValid: _validate(description: description),
    );
  }

  void onLaborPriceChanged(String value) {
    final laborPrice = ServiceReportLaborPrice.dirty(value);
    state = state.copyWith(
      laborPrice: laborPrice,
      errorMessages: const [],
      isValid: _validate(laborPrice: laborPrice),
    );
  }

  Future<bool> submit({
    required Future<bool> Function({
      required String description,
      required double laborPrice,
    })
    onSubmit,
  }) async {
    _touchAll();
    if (!state.isValid) return false;

    state = state.copyWith(isPosting: true, errorMessages: const []);

    final parsedLaborPrice = state.laborPrice.valueAsDouble;
    if (parsedLaborPrice == null) {
      state = state.copyWith(
        isPosting: false,
        errorMessages: const ['Ingresa un monto valido en Bs.'],
      );
      return false;
    }

    final isSuccess = await onSubmit(
      description: state.description.value.trim(),
      laborPrice: parsedLaborPrice,
    );
    if (!mounted) return false;

    if (!isSuccess) {
      state = state.copyWith(
        isPosting: false,
        errorMessages: const ['No fue posible registrar el reporte final.'],
      );
      return false;
    }

    state = state.copyWith(isPosting: false, errorMessages: const []);
    return true;
  }

  bool _validate({
    ServiceReportDescription? description,
    ServiceReportLaborPrice? laborPrice,
  }) {
    return Formz.validate([
      description ?? state.description,
      laborPrice ?? state.laborPrice,
    ]);
  }

  void _touchAll() {
    final description = ServiceReportDescription.dirty(state.description.value);
    final laborPrice = ServiceReportLaborPrice.dirty(state.laborPrice.value);

    state = state.copyWith(
      description: description,
      laborPrice: laborPrice,
      isFormPosted: true,
      isValid: Formz.validate([description, laborPrice]),
    );
  }
}

class MechanicCompletionFormState {
  MechanicCompletionFormState({
    this.description = const ServiceReportDescription.pure(),
    this.laborPrice = const ServiceReportLaborPrice.pure(),
    this.isPosting = false,
    this.isFormPosted = false,
    this.isValid = false,
    this.errorMessages = const [],
  });

  final ServiceReportDescription description;
  final ServiceReportLaborPrice laborPrice;
  final bool isPosting;
  final bool isFormPosted;
  final bool isValid;
  final List<String> errorMessages;

  String get errorMessage =>
      errorMessages.isNotEmpty ? errorMessages.first : '';

  MechanicCompletionFormState copyWith({
    ServiceReportDescription? description,
    ServiceReportLaborPrice? laborPrice,
    bool? isPosting,
    bool? isFormPosted,
    bool? isValid,
    List<String>? errorMessages,
  }) {
    return MechanicCompletionFormState(
      description: description ?? this.description,
      laborPrice: laborPrice ?? this.laborPrice,
      isPosting: isPosting ?? this.isPosting,
      isFormPosted: isFormPosted ?? this.isFormPosted,
      isValid: isValid ?? this.isValid,
      errorMessages: errorMessages ?? this.errorMessages,
    );
  }
}

enum ServiceReportDescriptionError { empty, length }

class ServiceReportDescription
    extends FormzInput<String, ServiceReportDescriptionError> {
  const ServiceReportDescription.pure() : super.pure('');
  const ServiceReportDescription.dirty(String value) : super.dirty(value);

  String? get errorMessage {
    if (isPure || isValid) return null;
    if (displayError == ServiceReportDescriptionError.empty) {
      return 'Describe brevemente el trabajo realizado';
    }
    if (displayError == ServiceReportDescriptionError.length) {
      return 'La descripcion debe tener entre 8 y 2000 caracteres';
    }
    return null;
  }

  @override
  ServiceReportDescriptionError? validator(String value) {
    final normalized = value.trim();
    if (normalized.isEmpty) return ServiceReportDescriptionError.empty;
    if (normalized.length < 8 || normalized.length > 2000) {
      return ServiceReportDescriptionError.length;
    }
    return null;
  }
}

enum ServiceReportLaborPriceError { empty, format, negative }

class ServiceReportLaborPrice
    extends FormzInput<String, ServiceReportLaborPriceError> {
  const ServiceReportLaborPrice.pure() : super.pure('');
  const ServiceReportLaborPrice.dirty(String value) : super.dirty(value);

  double? get valueAsDouble {
    final normalized = value.trim().replaceAll(',', '.');
    return double.tryParse(normalized);
  }

  String? get errorMessage {
    if (isPure || isValid) return null;
    if (displayError == ServiceReportLaborPriceError.empty) {
      return 'Ingresa el monto cobrado';
    }
    if (displayError == ServiceReportLaborPriceError.format) {
      return 'Ingresa un monto valido';
    }
    if (displayError == ServiceReportLaborPriceError.negative) {
      return 'El monto no puede ser negativo';
    }
    return null;
  }

  @override
  ServiceReportLaborPriceError? validator(String value) {
    final normalized = value.trim();
    if (normalized.isEmpty) return ServiceReportLaborPriceError.empty;

    final parsed = double.tryParse(normalized.replaceAll(',', '.'));
    if (parsed == null) return ServiceReportLaborPriceError.format;
    if (parsed < 0) return ServiceReportLaborPriceError.negative;

    return null;
  }
}
