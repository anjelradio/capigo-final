import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/incidents/presentation/providers/providers.dart';
import 'package:mobile/features/shared/shared.dart';

class ClientServiceDetailScreen extends ConsumerStatefulWidget {
  const ClientServiceDetailScreen({super.key, required this.incidentId});

  final String incidentId;

  @override
  ConsumerState<ClientServiceDetailScreen> createState() =>
      _ClientServiceDetailScreenState();
}

class _ClientServiceDetailScreenState
    extends ConsumerState<ClientServiceDetailScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(clientServiceDetailProvider(widget.incidentId).notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(clientServiceDetailProvider(widget.incidentId));
    final notifier = ref.read(
      clientServiceDetailProvider(widget.incidentId).notifier,
    );
    final detail = state.detail;

    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      appBar: AppBar(
        title: const Text('Detalle del servicio'),
        foregroundColor: AppColors.toastWarning,
        titleTextStyle: Theme.of(context).textTheme.titleMedium?.copyWith(
          color: AppColors.toastWarning,
          fontWeight: FontWeight.w800,
        ),
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
          : detail == null
          ? const Center(child: Text('Sin informacion del servicio'))
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
              children: [
                _Block(
                  title: 'Incidente',
                  children: [
                    _line('Estado', detail.status),
                    _line('Problema', detail.problemName ?? 'Sin diagnostico'),
                    _line(
                      'Descripcion',
                      (detail.description ?? '').trim().isEmpty
                          ? 'Sin descripcion'
                          : detail.description!,
                    ),
                    _line(
                      'Direccion',
                      detail.address ?? 'Sin direccion textual',
                    ),
                    _line(
                      'Distancia',
                      detail.distanceKm == null
                          ? 'No disponible'
                          : '${detail.distanceKm!.toStringAsFixed(2)} km',
                    ),
                    _line(
                      'Costo traslado',
                      detail.deliveryPrice == null
                          ? 'No disponible'
                          : 'Bs ${detail.deliveryPrice!.toStringAsFixed(2)}',
                    ),
                    _line(
                      'Fecha',
                      BoliviaDateTimeFormatter.toBoliviaDateTimeLabel(
                        detail.createdDate,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _Block(
                  title: 'Vehiculo',
                  children: [
                    _line('Marca', detail.vehicle.make),
                    _line('Modelo', detail.vehicle.model),
                    _line('Placa', detail.vehicle.plate),
                    _line('Color', detail.vehicle.color),
                  ],
                ),
                const SizedBox(height: 12),
                _Block(
                  title: 'Atencion',
                  children: [
                    _line(
                      'Taller',
                      detail.repairShopName ?? 'Sin taller asignado',
                    ),
                    _line(
                      'Mecanico',
                      detail.mechanicName ?? 'Sin mecanico asignado',
                    ),
                    _line(
                      'Costo mano de obra',
                      detail.laborPrice == null
                          ? 'No disponible'
                          : 'Bs ${detail.laborPrice!.toStringAsFixed(2)}',
                    ),
                    _line(
                      'Reporte final',
                      (detail.reportDescription ?? '').trim().isEmpty
                          ? 'Sin reporte'
                          : detail.reportDescription!,
                    ),
                  ],
                ),
              ],
            ),
    );
  }

  Widget _line(String label, String value) {
    final textStyle = Theme.of(context).textTheme.bodyMedium?.copyWith(
      color: AppColors.appTextOnDark,
      fontWeight: FontWeight.w600,
      fontSize: 14,
      height: 1.3,
    );

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: RichText(
        text: TextSpan(
          style: textStyle,
          children: [
            TextSpan(
              text: '$label: ',
              style: const TextStyle(
                color: AppColors.appTextOnDark,
                fontWeight: FontWeight.bold,
              ),
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
