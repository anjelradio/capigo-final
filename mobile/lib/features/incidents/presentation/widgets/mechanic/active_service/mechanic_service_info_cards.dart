import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/domain/domain.dart';

import 'mechanic_incident_evidence_gallery.dart';

class MechanicIncidentInfoCard extends StatelessWidget {
  const MechanicIncidentInfoCard({
    super.key,
    required this.assignment,
    required this.statusLabel,
  });

  final MechanicAssignment assignment;
  final String statusLabel;

  @override
  Widget build(BuildContext context) {
    final incidentDescription = assignment.incident.description?.trim() ?? '';
    final incidentAddress = assignment.incident.address?.trim() ?? '';

    return _InfoCardShell(
      title: 'Incidente',
      icon: Icons.report_problem_rounded,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _DetailRow(label: 'Estado', value: statusLabel),
          const SizedBox(height: 6),
          _DetailRow(
            label: 'Direccion',
            value: incidentAddress.isNotEmpty
                ? incidentAddress
                : 'Ubicacion sin direccion textual.',
          ),
          const SizedBox(height: 6),
          _DetailRow(
            label: 'Descripcion',
            value: incidentDescription.isNotEmpty
                ? incidentDescription
                : 'Sin descripcion adicional del incidente.',
          ),
        ],
      ),
    );
  }
}

class MechanicIncidentEvidenceSectionCard extends StatelessWidget {
  const MechanicIncidentEvidenceSectionCard({
    super.key,
    required this.evidenceUrls,
  });

  final List<String> evidenceUrls;

  @override
  Widget build(BuildContext context) {
    if (evidenceUrls.isEmpty) return const SizedBox.shrink();

    return _InfoCardShell(
      title: 'Evidencias',
      icon: Icons.photo_library_rounded,
      child: MechanicIncidentEvidenceGallery(
        evidenceUrls: evidenceUrls,
        showHeader: false,
      ),
    );
  }
}

class MechanicClientInfoCard extends StatelessWidget {
  const MechanicClientInfoCard({
    super.key,
    required this.assignment,
    required this.onCallClient,
    required this.onWhatsAppClient,
  });

  final MechanicAssignment assignment;
  final Future<void> Function() onCallClient;
  final Future<void> Function() onWhatsAppClient;

  @override
  Widget build(BuildContext context) {
    final clientName = assignment.incident.clientName?.trim() ?? '';
    final clientEmail = assignment.incident.clientEmail?.trim() ?? '';
    final clientPhone = assignment.incident.clientPhone?.trim() ?? '';
    final hasClientContact = clientPhone.isNotEmpty;

    return _InfoCardShell(
      title: 'Cliente',
      icon: Icons.person_rounded,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _DetailRow(
            label: 'Nombre',
            value: clientName.isNotEmpty
                ? clientName
                : 'Cliente no identificado',
          ),
          const SizedBox(height: 6),
          _DetailRow(
            label: 'Telefono',
            value: clientPhone.isNotEmpty ? clientPhone : 'Sin telefono',
          ),
          const SizedBox(height: 6),
          _DetailRow(
            label: 'Correo',
            value: clientEmail.isNotEmpty ? clientEmail : 'Sin correo',
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: hasClientContact ? onCallClient : null,
                  icon: const Icon(Icons.call_rounded, size: 18),
                  label: const Text('Llamar'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: FilledButton.icon(
                  onPressed: hasClientContact ? onWhatsAppClient : null,
                  icon: const Icon(Icons.chat_bubble_rounded, size: 18),
                  label: const Text('WhatsApp'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class MechanicVehicleInfoCard extends StatelessWidget {
  const MechanicVehicleInfoCard({super.key, required this.assignment});

  final MechanicAssignment assignment;

  @override
  Widget build(BuildContext context) {
    return _InfoCardShell(
      title: 'Vehiculo',
      icon: Icons.directions_car_filled_rounded,
      child: Text(
        _vehicleText(),
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
          color: AppColors.appTextOnDark,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  String _vehicleText() {
    final vehicle = assignment.incident.vehicle;
    if (vehicle == null) return 'Vehiculo: sin informacion';

    return 'Vehiculo: ${vehicle.make} ${vehicle.model} - ${vehicle.plate} - ${vehicle.color}';
  }
}

class _InfoCardShell extends StatelessWidget {
  const _InfoCardShell({
    required this.title,
    required this.icon,
    required this.child,
  });

  final String title;
  final IconData icon;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.appBgDeep.withValues(alpha: 0.38),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: AppColors.appAccent),
              const SizedBox(width: 6),
              Text(
                title,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.appAccent,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          child,
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 80,
          child: Text(
            '$label:',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: AppColors.appTextOnDarkMuted,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.appTextOnDark,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}

class MechanicStatusChip extends StatelessWidget {
  const MechanicStatusChip({super.key, required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: AppColors.appAccent.withValues(alpha: 0.18),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
          color: AppColors.appTextOnDark,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}
