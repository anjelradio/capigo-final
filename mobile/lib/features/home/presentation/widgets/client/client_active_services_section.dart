import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';

class ClientActiveServicesSection extends StatelessWidget {
  const ClientActiveServicesSection({super.key});

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'SERVICIOS EN CURSO',
          style: textTheme.titleSmall?.copyWith(
            color: AppColors.appAccent,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: AppColors.appBgMid,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.appNavBorder),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 24),
          child: Column(
            children: [
              Container(
                width: 58,
                height: 58,
                decoration: const BoxDecoration(
                  color: AppColors.appBgDeep,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.directions_car_filled_rounded,
                  color: AppColors.appAccent,
                  size: 28,
                ),
              ),
              const SizedBox(height: 14),
              Text(
                'No hay servicios activos',
                style: textTheme.titleMedium?.copyWith(
                  color: AppColors.appTextOnDark,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Cuando solicites asistencia o mantenimiento, los detalles del progreso apareceran aqui.',
                textAlign: TextAlign.center,
                style: textTheme.bodyMedium?.copyWith(
                  color: AppColors.appTextOnDarkMuted,
                  height: 1.35,
                ),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () => context.push('/incidents/active-service'),
                child: Text(
                  'Ver servicios en curso',
                  style: textTheme.bodyMedium?.copyWith(
                    color: AppColors.appAccent,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
