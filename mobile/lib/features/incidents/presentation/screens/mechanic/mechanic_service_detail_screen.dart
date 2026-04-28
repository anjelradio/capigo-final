import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/assignments.dart';
import 'package:mobile/features/shared/shared.dart';

class MechanicServiceDetailScreen extends ConsumerStatefulWidget {
  const MechanicServiceDetailScreen({super.key, required this.incidentId});

  final String incidentId;

  @override
  ConsumerState<MechanicServiceDetailScreen> createState() =>
      _MechanicServiceDetailScreenState();
}

class _MechanicServiceDetailScreenState
    extends ConsumerState<MechanicServiceDetailScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref
          .read(mechanicServiceDetailProvider(widget.incidentId).notifier)
          .load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(mechanicServiceDetailProvider(widget.incidentId));
    final notifier = ref.read(
      mechanicServiceDetailProvider(widget.incidentId).notifier,
    );
    final assignment = state.detail;

    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      appBar: AppBar(
        title: const Text('Detalle del servicio'),
        foregroundColor: AppColors.toastWarning,
        centerTitle: true,
      ),
      body: state.isLoading
          ? const Center(child: CircularProgressIndicator(strokeWidth: 2.4))
          : state.errorMessage.isNotEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 22),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      state.errorMessage,
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: AppColors.toastWarning),
                    ),
                    const SizedBox(height: 10),
                    OutlinedButton(
                      onPressed: notifier.refresh,
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
              ),
            )
          : assignment == null
          ? const Center(child: Text('Sin informacion del servicio'))
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
              children: [
                _Block(
                  title: 'Incidente',
                  children: [
                    _line('Estado', assignment.incident.status),
                    _line(
                      'Problema',
                      assignment.incident.problemName ?? 'Sin diagnostico',
                    ),
                    _line(
                      'Descripcion',
                      (assignment.incident.description ?? '').trim().isEmpty
                          ? 'Sin descripcion'
                          : assignment.incident.description!,
                    ),
                    _line(
                      'Direccion',
                      assignment.incident.address ?? 'Sin direccion textual',
                    ),
                    _line(
                      'Distancia',
                      assignment.incident.distanceKm == null
                          ? 'No disponible'
                          : '${assignment.incident.distanceKm!.toStringAsFixed(2)} km',
                    ),
                    _line(
                      'Costo traslado',
                      assignment.incident.deliveryPrice == null
                          ? 'No disponible'
                          : 'Bs ${assignment.incident.deliveryPrice!.toStringAsFixed(2)}',
                    ),
                    if (assignment.assignedAt != null)
                      _line(
                        'Fecha',
                        BoliviaDateTimeFormatter.toBoliviaDateTimeLabel(
                          assignment.assignedAt!,
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 12),
                _Block(
                  title: 'Cliente',
                  children: [
                    _line(
                      'Nombre',
                      assignment.incident.clientName ?? 'No disponible',
                    ),
                    _line(
                      'Correo',
                      assignment.incident.clientEmail ?? 'No disponible',
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _Block(
                  title: 'Vehiculo',
                  children: [
                    _line('Marca', assignment.incident.vehicle?.make ?? '--'),
                    _line('Modelo', assignment.incident.vehicle?.model ?? '--'),
                    _line('Placa', assignment.incident.vehicle?.plate ?? '--'),
                    _line('Color', assignment.incident.vehicle?.color ?? '--'),
                  ],
                ),
              ],
            ),
    );
  }

  Widget _line(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: RichText(
        text: TextSpan(
          style: const TextStyle(
            color: AppColors.appTextOnDark,
            fontWeight: FontWeight.w600,
            fontSize: 14,
            height: 1.3,
          ),
          children: [
            TextSpan(
              text: '$label: ',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            TextSpan(text: value),
          ],
        ),
      ),
    );
  }
}

class _Block extends StatelessWidget {
  const _Block({required this.title, required this.children});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 8),
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: AppColors.appAccent,
              fontWeight: FontWeight.w800,
              fontSize: 17,
            ),
          ),
          const SizedBox(height: 10),
          ...children,
        ],
      ),
    );
  }
}
