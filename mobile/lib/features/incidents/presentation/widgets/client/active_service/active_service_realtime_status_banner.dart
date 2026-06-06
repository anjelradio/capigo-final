import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class ActiveServiceRealtimeStatusBanner extends StatelessWidget {
  const ActiveServiceRealtimeStatusBanner({
    super.key,
    required this.status,
    required this.isConnecting,
    required this.isConnected,
  });

  final String status;
  final bool isConnecting;
  final bool isConnected;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final normalizedStatus = _normalizeStatus(status);

    return Material(
      color: Colors.transparent,
      child: Ink(
        height: 40,
        decoration: BoxDecoration(
          color: AppColors.appBgDeep,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.appNavBorder),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: Row(
          children: [
            _StatusLeadingIcon(
              status: normalizedStatus,
              isConnecting: isConnecting,
              isConnected: isConnected,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                _statusLabel(normalizedStatus),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: textTheme.labelLarge?.copyWith(
                  color: AppColors.appTextOnDark,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.2,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Icon(
              isConnected ? Icons.wifi_rounded : Icons.wifi_off_rounded,
              size: 16,
              color: isConnected
                  ? AppColors.toastSuccess
                  : AppColors.appTextOnDarkMuted,
            ),
          ],
        ),
      ),
    );
  }

  String _normalizeStatus(String value) {
    final status = value.trim().toLowerCase();
    return status.isEmpty ? 'pending' : status;
  }

  String _statusLabel(String status) {
    const labels = {
      'pending': 'Pendiente',
      'classifying': 'Clasificando incidente',
      'classified': 'Incidente clasificado',
      'searching_shop': 'Buscando taller',
      'assigned': 'Asignado',
      'on_the_way': 'Mecanico en camino',
      'arrived': 'Mecanico llego',
      'payment_pending': 'Pago pendiente',
      'completed': 'Servicio completado',
      'cancelled': 'Servicio cancelado',
      'failed': 'Servicio fallido',
    };

    return labels[status] ?? 'Procesando servicio';
  }
}

class _StatusLeadingIcon extends StatelessWidget {
  const _StatusLeadingIcon({
    required this.status,
    required this.isConnecting,
    required this.isConnected,
  });

  final String status;
  final bool isConnecting;
  final bool isConnected;

  @override
  Widget build(BuildContext context) {
    if (isConnecting || _isProcessingStatus(status)) {
      return const SizedBox(
        width: 16,
        height: 16,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          color: AppColors.appAccent,
        ),
      );
    }

    final icon = _isSuccessStatus(status)
        ? Icons.check_circle_rounded
        : Icons.info_rounded;
    final color = _isSuccessStatus(status)
        ? AppColors.toastSuccess
        : (isConnected ? AppColors.appAccent : AppColors.appTextOnDarkMuted);

    return Icon(icon, size: 18, color: color);
  }

  bool _isProcessingStatus(String status) {
    return status == 'pending' ||
        status == 'classifying' ||
        status == 'classified' ||
        status == 'searching_shop';
  }

  bool _isSuccessStatus(String status) {
    return status == 'assigned' ||
        status == 'on_the_way' ||
        status == 'arrived' ||
        status == 'payment_pending' ||
        status == 'completed';
  }
}
