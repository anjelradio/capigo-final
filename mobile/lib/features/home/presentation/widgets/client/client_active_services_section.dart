import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/home/presentation/providers/providers.dart';
import 'package:mobile/features/incidents/presentation/widgets/widgets.dart';
import 'package:mobile/features/shared/shared.dart';

class ClientActiveServicesSection extends ConsumerStatefulWidget {
  const ClientActiveServicesSection({super.key});

  @override
  ConsumerState<ClientActiveServicesSection> createState() =>
      _ClientActiveServicesSectionState();
}

class _ClientActiveServicesSectionState
    extends ConsumerState<ClientActiveServicesSection> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      final remindersState = ref.read(pendingFeedbackRemindersProvider);
      if (!remindersState.hasLoaded && !remindersState.isLoading) {
        ref.read(pendingFeedbackRemindersProvider.notifier).load();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final remindersState = ref.watch(pendingFeedbackRemindersProvider);
    final remindersNotifier = ref.read(
      pendingFeedbackRemindersProvider.notifier,
    );
    final reminders = remindersState.reminders;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'NOTIFICACIONES PENDIENTES',
          style: textTheme.titleSmall?.copyWith(
            color: AppColors.appAccent,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 12),
        if (remindersState.isLoading)
          const SizedBox(
            height: 96,
            child: Center(child: CircularProgressIndicator(strokeWidth: 2.4)),
          )
        else if (remindersState.errorMessage.isNotEmpty)
          _PendingFeedbackPlaceholder(
            title: 'No se pudieron cargar recordatorios',
            description: remindersState.errorMessage,
            icon: Icons.warning_amber_rounded,
            actionLabel: 'Reintentar',
            onActionTap: remindersNotifier.refresh,
          )
        else if (reminders.isEmpty)
          _PendingFeedbackPlaceholder(
            title: 'No hay recordatorios pendientes',
            description:
                'Cuando completes un servicio, podras calificarlo desde aqui.',
            icon: Icons.notifications_none_rounded,
          )
        else
          Column(
            children: reminders.map((reminder) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: _PendingFeedbackCard(
                  incidentId: reminder.incidentId,
                  title: reminder.problemName,
                  description: reminder.description,
                  completedAt: reminder.completedAt,
                  onTap: () async {
                    final sent = await showModalBottomSheet<bool>(
                      context: context,
                      isScrollControlled: true,
                      backgroundColor: Colors.transparent,
                      builder: (_) => IncidentFeedbackSheet(
                        incidentId: reminder.incidentId,
                      ),
                    );
                    if ((sent ?? false) && mounted) {
                      await remindersNotifier.refresh();
                    }
                  },
                ),
              );
            }).toList(),
          ),
      ],
    );
  }
}

class _PendingFeedbackCard extends StatelessWidget {
  const _PendingFeedbackCard({
    required this.incidentId,
    required this.description,
    required this.onTap,
    this.title,
    this.completedAt,
  });

  final String incidentId;
  final String? title;
  final String description;
  final DateTime? completedAt;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final displayDescription = description.trim().isEmpty
        ? 'Servicio finalizado sin descripcion.'
        : description.trim();

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.reviews_rounded,
                color: AppColors.appAccent,
                size: 16,
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  (title ?? '').trim().isNotEmpty
                      ? title!
                      : 'Servicio completado',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: textTheme.bodyMedium?.copyWith(
                    color: AppColors.appTextOnDark,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            displayDescription,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: textTheme.bodySmall?.copyWith(
              color: AppColors.appTextOnDarkMuted,
              height: 1.3,
            ),
          ),
          if (completedAt != null) ...[
            const SizedBox(height: 6),
            Text(
              'Completado: ${BoliviaDateTimeFormatter.toBoliviaDateTimeLabel(completedAt!)}',
              style: textTheme.labelSmall?.copyWith(
                color: AppColors.appTextOnDarkMuted,
              ),
            ),
          ],
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: onTap,
              icon: const Icon(Icons.star_outline_rounded, size: 16),
              label: const Text('Calificar ahora'),
              style: TextButton.styleFrom(
                foregroundColor: AppColors.appAccent,
                visualDensity: VisualDensity.compact,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PendingFeedbackPlaceholder extends StatelessWidget {
  const _PendingFeedbackPlaceholder({
    required this.title,
    required this.description,
    required this.icon,
    this.actionLabel,
    this.onActionTap,
  });

  final String title;
  final String description;
  final IconData icon;
  final String? actionLabel;
  final VoidCallback? onActionTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      child: Column(
        children: [
          Icon(icon, color: AppColors.appAccent, size: 22),
          const SizedBox(height: 8),
          Text(
            title,
            textAlign: TextAlign.center,
            style: textTheme.bodyMedium?.copyWith(
              color: AppColors.appTextOnDark,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            description,
            textAlign: TextAlign.center,
            style: textTheme.bodySmall?.copyWith(
              color: AppColors.appTextOnDarkMuted,
              height: 1.3,
            ),
          ),
          if ((actionLabel ?? '').trim().isNotEmpty && onActionTap != null) ...[
            const SizedBox(height: 8),
            TextButton(onPressed: onActionTap, child: Text(actionLabel!)),
          ],
        ],
      ),
    );
  }
}
