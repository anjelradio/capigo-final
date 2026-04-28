import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/assignments.dart';
import 'package:mobile/features/shared/shared.dart';

class MechanicCompleteServiceSheet extends ConsumerWidget {
  const MechanicCompleteServiceSheet({super.key, required this.onSubmitReport});

  final Future<bool> Function({
    required String description,
    required double laborPrice,
  })
  onSubmitReport;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(mechanicCompletionFormProvider);
    final formNotifier = ref.read(mechanicCompletionFormProvider.notifier);

    Future<void> submit() async {
      final isSuccess = await formNotifier.submit(onSubmit: onSubmitReport);
      if (!context.mounted) return;

      if (isSuccess) {
        Navigator.of(context).pop(true);
      }
    }

    return Container(
      decoration: const BoxDecoration(
        color: AppColors.appBgBase,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(26),
          topRight: Radius.circular(26),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: EdgeInsets.fromLTRB(
            16,
            12,
            16,
            16 + MediaQuery.viewInsetsOf(context).bottom,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Center(
                child: SizedBox(
                  width: 42,
                  height: 4,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      color: AppColors.appNavBorder,
                      borderRadius: BorderRadius.all(Radius.circular(999)),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 14),
              Text(
                'Completar servicio',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppColors.appTextOnDark,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'Registra el trabajo realizado y el costo cobrado al cliente.',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.appTextOnDarkMuted,
                ),
              ),
              const SizedBox(height: 14),
              if (formState.errorMessage.isNotEmpty) ...[
                Text(
                  formState.errorMessage,
                  style: const TextStyle(
                    color: Color(0xFFE38A8A),
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 10),
              ],
              AppFormLayout(
                submitText: formState.isPosting
                    ? 'Registrando...'
                    : 'Enviar reporte y finalizar',
                onSubmit: formState.isPosting ? null : submit,
                fieldSpacing: 14,
                fields: [
                  CustomTextFormField(
                    label: 'Descripcion del trabajo',
                    hint:
                        'Ej. diagnostico, cambio de pieza, pruebas realizadas',
                    initialValue: formState.description.value,
                    onChanged: formNotifier.onDescriptionChanged,
                    errorMessage: formState.isFormPosted
                        ? formState.description.errorMessage
                        : null,
                    maxLines: 3,
                    minLines: 3,
                    borderRadius: 18,
                  ),
                  CustomTextFormField(
                    label: 'Monto cobrado (Bs)',
                    hint: 'Ej. 120.50',
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: true,
                    ),
                    initialValue: formState.laborPrice.value,
                    onChanged: formNotifier.onLaborPriceChanged,
                    errorMessage: formState.isFormPosted
                        ? formState.laborPrice.errorMessage
                        : null,
                    borderRadius: 18,
                  ),
                ],
              ),
              const SizedBox(height: 10),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: formState.isPosting
                      ? null
                      : () => Navigator.of(context).pop(false),
                  child: const Text('Cancelar'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
