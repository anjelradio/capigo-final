import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/incidents/presentation/providers/providers.dart';
import 'package:mobile/features/shared/shared.dart';

class IncidentFeedbackSheet extends ConsumerWidget {
  const IncidentFeedbackSheet({super.key, required this.incidentId});

  final String incidentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(incidentFeedbackFormProvider(incidentId));
    final formNotifier = ref.read(
      incidentFeedbackFormProvider(incidentId).notifier,
    );

    Future<void> onSubmit() async {
      final isSuccess = await formNotifier.submit();
      if (!context.mounted) return;
      if (!isSuccess) return;

      Navigator.of(context).pop(true);
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
                'Servicio finalizado',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppColors.appTextOnDark,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'Cuentanos como fue tu experiencia con este servicio.',
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
              _RatingSelector(
                rating: formState.rating.value,
                onRatingChanged: formState.isPosting
                    ? null
                    : formNotifier.onRatingChanged,
                errorMessage: formState.isFormPosted
                    ? formState.rating.errorMessage
                    : null,
              ),
              const SizedBox(height: 12),
              AppFormLayout(
                submitText: formState.isPosting
                    ? 'Enviando...'
                    : 'Enviar calificacion',
                onSubmit: formState.isPosting ? null : onSubmit,
                fieldSpacing: 14,
                fields: [
                  CustomTextFormField(
                    label: 'Comentario (opcional)',
                    hint: 'Tu experiencia con el mecanico y el servicio',
                    initialValue: formState.comment.value,
                    onChanged: formNotifier.onCommentChanged,
                    errorMessage: formState.isFormPosted
                        ? formState.comment.errorMessage
                        : null,
                    minLines: 3,
                    maxLines: 3,
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
                  child: const Text('Ahora no'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RatingSelector extends StatelessWidget {
  const _RatingSelector({
    required this.rating,
    required this.onRatingChanged,
    required this.errorMessage,
  });

  final int rating;
  final void Function(int rating)? onRatingChanged;
  final String? errorMessage;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Calificacion',
          style: TextStyle(
            color: AppColors.appTextOnDark,
            fontWeight: FontWeight.w700,
            fontSize: 14,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: List.generate(5, (index) {
            final star = index + 1;
            final isFilled = star <= rating;
            return IconButton(
              onPressed: onRatingChanged == null
                  ? null
                  : () => onRatingChanged!(star),
              icon: Icon(
                isFilled ? Icons.star_rounded : Icons.star_border_rounded,
                color: isFilled
                    ? const Color(0xFFFFC857)
                    : AppColors.appNavBorder,
                size: 32,
              ),
              tooltip: '$star estrella${star == 1 ? '' : 's'}',
            );
          }),
        ),
        if ((errorMessage ?? '').isNotEmpty)
          Text(
            errorMessage!,
            style: const TextStyle(
              color: Color(0xFFE38A8A),
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
      ],
    );
  }
}
