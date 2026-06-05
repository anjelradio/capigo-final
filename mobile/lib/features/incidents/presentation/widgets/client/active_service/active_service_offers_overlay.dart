import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/incidents/domain/domain.dart';
import 'package:mobile/features/shared/shared.dart';

class ActiveServiceOffersOverlay extends StatelessWidget {
  const ActiveServiceOffersOverlay({
    super.key,
    required this.offers,
    required this.actingOfferId,
    required this.isAcceptingOffer,
    required this.isLoadingOffers,
    this.errorMessage,
    required this.onAcceptOffer,
    required this.onRejectOffer,
  });

  final List<ClientIncidentOffer> offers;
  final String actingOfferId;
  final bool isAcceptingOffer;
  final bool isLoadingOffers;
  final String? errorMessage;
  final ValueChanged<String> onAcceptOffer;
  final ValueChanged<String> onRejectOffer;

  @override
  Widget build(BuildContext context) {
    final hasActionInProgress = actingOfferId.trim().isNotEmpty;

    return Positioned.fill(
      child: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppColors.appBgDeep.withValues(alpha: 0.9),
              AppColors.appBgBase.withValues(alpha: 0.83),
              AppColors.appBgDeep.withValues(alpha: 0.92),
            ],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 18, 16, 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'OFERTAS DISPONIBLES',
                  style: TextStyle(
                    color: AppColors.appAccent,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 0.8,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Elige el taller que atendera tu incidente.',
                  style: TextStyle(
                    color: AppColors.appTextOnDark.withValues(alpha: 0.9),
                    fontSize: 13,
                  ),
                ),
                if ((errorMessage ?? '').trim().isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _ErrorBanner(message: errorMessage!.trim()),
                ],
                const SizedBox(height: 14),
                Expanded(
                  child: isLoadingOffers && offers.isEmpty
                      ? const Center(
                          child: CircularProgressIndicator(
                            color: AppColors.appAccent,
                          ),
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.only(bottom: 12),
                          itemCount: offers.length,
                          separatorBuilder: (_, _) =>
                              const SizedBox(height: 12),
                          itemBuilder: (_, index) {
                            final offer = offers[index];
                            final isActing =
                                actingOfferId == offer.assignmentId;

                            return _OfferCard(
                              offer: offer,
                              isActing: isActing,
                              isAccepting: isActing && isAcceptingOffer,
                              hasActionInProgress: hasActionInProgress,
                              onAccept: () => onAcceptOffer(offer.assignmentId),
                              onReject: () => onRejectOffer(offer.assignmentId),
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _OfferCard extends StatelessWidget {
  const _OfferCard({
    required this.offer,
    required this.isActing,
    required this.isAccepting,
    required this.hasActionInProgress,
    required this.onAccept,
    required this.onReject,
  });

  final ClientIncidentOffer offer;
  final bool isActing;
  final bool isAccepting;
  final bool hasActionInProgress;
  final VoidCallback onAccept;
  final VoidCallback onReject;

  @override
  Widget build(BuildContext context) {
    final formattedOfferedAt = offer.offeredAt == null
        ? 'Hace un momento'
        : BoliviaDateTimeFormatter.toBoliviaDateTimeLabel(offer.offeredAt!);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 220),
      curve: Curves.easeOutCubic,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.appBgMid.withValues(alpha: 0.95),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: isActing
              ? AppColors.appAccent
              : AppColors.appNavBorder.withValues(alpha: 0.85),
        ),
        boxShadow: [
          BoxShadow(
            blurRadius: 18,
            offset: const Offset(0, 8),
            color: Colors.black.withValues(alpha: 0.24),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: AppColors.appAccent.withValues(alpha: 0.16),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.garage_rounded,
                  color: AppColors.appAccent,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      (offer.repairShopName ?? '').trim().isEmpty
                          ? 'Taller disponible'
                          : offer.repairShopName!.trim(),
                      style: const TextStyle(
                        color: AppColors.appTextOnDark,
                        fontWeight: FontWeight.w800,
                        fontSize: 15,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      (offer.mechanicName ?? '').trim().isEmpty
                          ? 'Mecanico por confirmar'
                          : offer.mechanicName!.trim(),
                      style: const TextStyle(
                        color: AppColors.appTextOnDarkMuted,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _OfferMetricChip(
                icon: Icons.sell_rounded,
                label: 'Oferta',
                value: _formatMoney(offer.quotedPrice),
              ),
              _OfferMetricChip(
                icon: Icons.local_shipping_rounded,
                label: 'Envio',
                value: _formatMoney(offer.deliveryPrice),
              ),
              _OfferMetricChip(
                icon: Icons.route_rounded,
                label: 'Distancia',
                value: offer.distanceKm == null
                    ? 'N/D'
                    : '${offer.distanceKm!.toStringAsFixed(2)} km',
              ),
              _OfferMetricChip(
                icon: Icons.schedule_rounded,
                label: 'ETA',
                value: offer.estimatedMinutes == null
                    ? 'N/D'
                    : '${offer.estimatedMinutes} min',
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            'Recibida: $formattedOfferedAt',
            style: TextStyle(
              color: AppColors.appTextOnDarkMuted.withValues(alpha: 0.9),
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: hasActionInProgress ? null : onReject,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFFF5AEAE),
                    side: const BorderSide(color: Color(0xFF925151)),
                  ),
                  child: isActing && !isAccepting
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Rechazar'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: FilledButton(
                  onPressed: hasActionInProgress ? null : onAccept,
                  child: isActing && isAccepting
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: AppColors.appAccentText,
                          ),
                        )
                      : const Text('Aceptar'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatMoney(double? value) {
    if (value == null) return 'N/D';
    return 'Bs ${value.toStringAsFixed(2)}';
  }
}

class _OfferMetricChip extends StatelessWidget {
  const _OfferMetricChip({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.appBgDeep.withValues(alpha: 0.56),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.appNavBorder.withValues(alpha: 0.8),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppColors.appAccent),
          const SizedBox(width: 6),
          Text(
            '$label: ',
            style: const TextStyle(
              color: AppColors.appTextOnDarkMuted,
              fontSize: 11,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: AppColors.appTextOnDark,
              fontWeight: FontWeight.w700,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF5B242A).withValues(alpha: 0.85),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFB84552)),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.error_outline_rounded,
            color: Color(0xFFFFC8D0),
            size: 18,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(color: Color(0xFFFFE5EA), fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }
}
