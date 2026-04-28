import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/assignments.dart';

class MechanicServicesSheet extends ConsumerStatefulWidget {
  const MechanicServicesSheet({super.key, required this.mode});

  final MechanicServicesMode mode;

  @override
  ConsumerState<MechanicServicesSheet> createState() =>
      _MechanicServicesSheetState();
}

class _MechanicServicesSheetState extends ConsumerState<MechanicServicesSheet> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(mechanicServicesProvider(widget.mode).notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(mechanicServicesProvider(widget.mode));
    final notifier = ref.read(mechanicServicesProvider(widget.mode).notifier);
    final textTheme = Theme.of(context).textTheme;
    final title = widget.mode == MechanicServicesMode.completed
        ? 'Servicios completados'
        : 'Historial de servicios';

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
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const SizedBox(
                width: 42,
                height: 4,
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    color: AppColors.appNavBorder,
                    borderRadius: BorderRadius.all(Radius.circular(999)),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      title,
                      style: textTheme.titleMedium?.copyWith(
                        color: AppColors.appTextOnDark,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: state.isLoading || state.isRefreshing
                        ? null
                        : notifier.refresh,
                    icon: const Icon(Icons.refresh_rounded),
                  ),
                ],
              ),
              SizedBox(
                height: MediaQuery.of(context).size.height * 0.62,
                child: state.isLoading
                    ? const Center(
                        child: CircularProgressIndicator(strokeWidth: 2.4),
                      )
                    : state.errorMessage.isNotEmpty
                    ? Center(
                        child: Text(
                          state.errorMessage,
                          textAlign: TextAlign.center,
                          style: textTheme.bodyMedium?.copyWith(
                            color: AppColors.toastWarning,
                          ),
                        ),
                      )
                    : state.services.isEmpty
                    ? Center(
                        child: Text(
                          'No hay servicios para mostrar.',
                          style: textTheme.bodyMedium?.copyWith(
                            color: AppColors.appTextOnDarkMuted,
                          ),
                        ),
                      )
                    : ListView.separated(
                        itemCount: state.services.length,
                        separatorBuilder: (_, _) => const SizedBox(height: 10),
                        itemBuilder: (context, index) {
                          final item = state.services[index];
                          final isClickable =
                              widget.mode == MechanicServicesMode.completed;

                          return Material(
                            color: Colors.transparent,
                            child: InkWell(
                              borderRadius: BorderRadius.circular(14),
                              onTap: !isClickable
                                  ? null
                                  : () {
                                      Navigator.of(context).pop();
                                      context.push(
                                        '/incidents/mechanic/services/${item.incidentId}/detail',
                                      );
                                    },
                              child: Ink(
                                decoration: BoxDecoration(
                                  color: AppColors.appBgMid,
                                  borderRadius: BorderRadius.circular(14),
                                  border: Border.all(
                                    color: AppColors.appNavBorder,
                                  ),
                                ),
                                padding: const EdgeInsets.fromLTRB(
                                  12,
                                  10,
                                  12,
                                  10,
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            (item.problemName ?? '')
                                                    .trim()
                                                    .isNotEmpty
                                                ? item.problemName!
                                                : 'Incidente de servicio',
                                            style: textTheme.bodyMedium
                                                ?.copyWith(
                                                  color:
                                                      AppColors.appTextOnDark,
                                                  fontWeight: FontWeight.w700,
                                                ),
                                          ),
                                        ),
                                        _StatusBadge(
                                          status: item.incidentStatus,
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      (item.incidentDescription ?? '')
                                              .trim()
                                              .isNotEmpty
                                          ? item.incidentDescription!
                                          : 'Sin descripcion registrada.',
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                      style: textTheme.bodySmall?.copyWith(
                                        color: AppColors.appTextOnDarkMuted,
                                      ),
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      'Placa: ${item.vehiclePlate ?? 'No disponible'}',
                                      style: textTheme.labelSmall?.copyWith(
                                        color: AppColors.appTextOnDarkMuted,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final normalized = status.trim().toLowerCase();
    Color color = const Color(0xFF94A3B8);
    String label = normalized.isEmpty ? 'Sin estado' : normalized;

    if (normalized == 'completed') {
      color = const Color(0xFF34D399);
      label = 'Completado';
    } else if (normalized == 'cancelled') {
      color = const Color(0xFFF59E0B);
      label = 'Cancelado';
    } else if (normalized == 'failed') {
      color = const Color(0xFFF87171);
      label = 'Fallido';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.18),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: AppColors.appTextOnDark,
          fontWeight: FontWeight.w700,
          fontSize: 11,
        ),
      ),
    );
  }
}
