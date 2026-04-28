import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/incidents/domain/domain.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:url_launcher/url_launcher.dart';

class ActiveServiceDetailsSection extends StatelessWidget {
  const ActiveServiceDetailsSection({
    super.key,
    required this.detail,
    this.clientDisplayName = '',
  });

  final ActiveIncidentDetail detail;
  final String clientDisplayName;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _InfoCard(
          title: 'Resumen del servicio',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _InfoValueRow(
                label: 'Solicitado',
                value: BoliviaDateTimeFormatter.toBoliviaDateTimeLabel(
                  detail.incident.createdDate,
                ),
              ),
              const SizedBox(height: 6),
              _InfoValueRow(
                label: 'Costo envio',
                value: detail.incident.deliveryPrice == null
                    ? 'No disponible'
                    : 'Bs ${detail.incident.deliveryPrice!.toStringAsFixed(0)}',
              ),
              const SizedBox(height: 6),
              _InfoValueRow(
                label: 'Distancia',
                value: detail.incident.distanceKm == null
                    ? 'No disponible'
                    : '${detail.incident.distanceKm!.toStringAsFixed(2)} km',
              ),
              if (detail.assignment?.estimatedMinutes != null) ...[
                const SizedBox(height: 6),
                _InfoValueRow(
                  label: 'Tiempo estimado',
                  value: '${detail.assignment!.estimatedMinutes} min',
                ),
              ],
            ],
          ),
        ),
        if (detail.assignment != null) ...[
          const SizedBox(height: 12),
          _InfoCard(
            title: 'Mecanico asignado',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _InfoValueRow(
                  label: 'Nombre',
                  value: (detail.assignment?.mechanicName ?? '').trim().isEmpty
                      ? 'Asignando mecanico...'
                      : detail.assignment!.mechanicName!,
                ),
                const SizedBox(height: 6),
                _InfoValueRow(
                  label: 'Taller',
                  value:
                      (detail.assignment?.repairShopName ?? '').trim().isEmpty
                      ? 'Sin dato'
                      : detail.assignment!.repairShopName!,
                ),
                const SizedBox(height: 6),
                _InfoValueRow(
                  label: 'Estado',
                  value: _humanizeStatus(detail.assignment!.status),
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _openPhoneCall(context),
                        icon: const Icon(Icons.call_rounded, size: 18),
                        label: const Text('Llamar'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: FilledButton.icon(
                        onPressed: () => _openWhatsApp(context),
                        icon: const Icon(Icons.chat_bubble_rounded, size: 18),
                        label: const Text('WhatsApp'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 12),
        _InfoCard(
          title: 'Vehiculo',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${detail.vehicle.make} ${detail.vehicle.model}',
                style: const TextStyle(
                  color: AppColors.appTextOnDark,
                  fontWeight: FontWeight.w700,
                  fontSize: 15,
                ),
              ),
              const SizedBox(height: 6),
              _InfoValueRow(
                label: 'Tipo',
                value: _humanizeStatus(detail.vehicle.type.name),
              ),
              const SizedBox(height: 6),
              _InfoValueRow(label: 'Placa', value: detail.vehicle.plate),
            ],
          ),
        ),
        const SizedBox(height: 12),
        _InfoCard(
          title: 'Descripcion del incidente',
          child: Text(
            (detail.incident.description ?? '').trim().isEmpty
                ? 'Sin descripcion'
                : detail.incident.description!,
            style: const TextStyle(
              color: AppColors.appTextOnDark,
              fontSize: 14,
              height: 1.35,
            ),
          ),
        ),
        const SizedBox(height: 12),
        _InfoCard(
          title: 'Evidencias',
          child: SizedBox(
            height: 130,
            child: detail.evidences.isEmpty
                ? const Center(
                    child: Text(
                      'No hay evidencias registradas.',
                      style: TextStyle(
                        color: AppColors.appTextOnDarkMuted,
                        fontSize: 12,
                      ),
                    ),
                  )
                : ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: detail.evidences.length,
                    separatorBuilder: (_, _) => const SizedBox(width: 10),
                    itemBuilder: (_, index) {
                      final evidence = detail.evidences[index];
                      return ClipRRect(
                        borderRadius: BorderRadius.circular(14),
                        child: Container(
                          width: 170,
                          decoration: BoxDecoration(
                            color: AppColors.appBgDeep,
                            border: Border.all(color: AppColors.appAccentDeep),
                          ),
                          child: Image.network(
                            evidence.url,
                            fit: BoxFit.cover,
                            errorBuilder: (_, _, _) => const Center(
                              child: Icon(
                                Icons.broken_image_outlined,
                                color: AppColors.appTextOnDarkMuted,
                              ),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ),
      ],
    );
  }

  String _humanizeStatus(String value) {
    final normalized = value.trim();
    if (normalized.isEmpty) return 'Sin dato';
    final parts = normalized.split('_').map((item) {
      if (item.isEmpty) return item;
      return '${item[0].toUpperCase()}${item.substring(1).toLowerCase()}';
    });
    return parts.join(' ');
  }

  Future<void> _openPhoneCall(BuildContext context) async {
    final normalizedPhone = _normalizePhoneForCall(
      detail.assignment?.mechanicPhone,
    );
    if (normalizedPhone == null) {
      _showSnack(context, 'No hay telefono del mecanico disponible.');
      return;
    }

    final uri = Uri(scheme: 'tel', path: normalizedPhone);
    final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!launched && context.mounted) {
      _showSnack(context, 'No se pudo abrir la app de telefono.');
    }
  }

  Future<void> _openWhatsApp(BuildContext context) async {
    final normalizedPhone = _normalizePhoneForWhatsApp(
      detail.assignment?.mechanicPhone,
    );
    if (normalizedPhone == null) {
      _showSnack(context, 'No hay telefono valido para WhatsApp.');
      return;
    }

    final clientName = clientDisplayName.trim().isEmpty
        ? 'cliente'
        : clientDisplayName.trim();
    final message =
        'Hola, soy $clientName. Te contacto por el servicio ${detail.incident.id.substring(0, 8)}.';
    final uri = Uri.parse(
      'https://wa.me/$normalizedPhone?text=${Uri.encodeComponent(message)}',
    );

    final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!launched && context.mounted) {
      _showSnack(context, 'No se pudo abrir WhatsApp.');
    }
  }

  String? _normalizePhoneForCall(String? rawPhone) {
    final digits = (rawPhone ?? '').replaceAll(RegExp(r'\D'), '');
    if (digits.isEmpty) return null;
    return digits;
  }

  String? _normalizePhoneForWhatsApp(String? rawPhone) {
    final digits = (rawPhone ?? '').replaceAll(RegExp(r'\D'), '');
    if (digits.isEmpty) return null;

    if (digits.length == 8 &&
        (digits.startsWith('6') || digits.startsWith('7'))) {
      return '591$digits';
    }

    if (digits.startsWith('591')) return digits;
    return digits.length >= 8 ? digits : null;
  }

  void _showSnack(BuildContext context, String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: AppColors.appAccent,
              fontWeight: FontWeight.w800,
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 10),
          child,
        ],
      ),
    );
  }
}

class _InfoValueRow extends StatelessWidget {
  const _InfoValueRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          '$label: ',
          style: const TextStyle(
            color: AppColors.appTextOnDarkMuted,
            fontSize: 12,
          ),
        ),
        Expanded(
          child: Text(
            value,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: AppColors.appTextOnDark,
              fontWeight: FontWeight.w700,
              fontSize: 12,
            ),
          ),
        ),
      ],
    );
  }
}
