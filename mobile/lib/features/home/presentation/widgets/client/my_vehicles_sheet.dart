import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/home/presentation/widgets/client/vehicle_card.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/domain/domain.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';

void showMyVehiclesSheet(BuildContext context) {
  final height = MediaQuery.of(context).size.height * 0.8;

  showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (modalContext) {
      return SafeArea(
        top: false,
        child: SizedBox(height: height, child: const _MyVehiclesSheet()),
      );
    },
  );
}

class _MyVehiclesSheet extends ConsumerStatefulWidget {
  const _MyVehiclesSheet();

  @override
  ConsumerState<_MyVehiclesSheet> createState() => _MyVehiclesSheetState();
}

class _MyVehiclesSheetState extends ConsumerState<_MyVehiclesSheet> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(vehiclesProvider.notifier).loadVehicles());
  }

  @override
  Widget build(BuildContext context) {
    final vehiclesState = ref.watch(vehiclesProvider);

    return DecoratedBox(
      decoration: const BoxDecoration(
        color: AppColors.appBgBase,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 14, 20, 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Mis vehiculos',
                    style: TextStyle(
                      color: AppColors.appAccent,
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.of(context).pop(),
                  icon: const Icon(
                    Icons.close_rounded,
                    color: AppColors.appAccent,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Expanded(
              child: vehiclesState.isLoading
                  ? const _VehiclesLoadingList()
                  : _VehiclesLoadedList(vehicles: vehiclesState.vehicles),
            ),
          ],
        ),
      ),
    );
  }
}

class _VehiclesLoadingList extends StatelessWidget {
  const _VehiclesLoadingList();

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      physics: const ClampingScrollPhysics(),
      itemCount: 3,
      separatorBuilder: (_, _) => const SizedBox(height: 12),
      itemBuilder: (_, index) => const _VehicleLoadingCard(),
    );
  }
}

class _VehicleLoadingCard extends StatelessWidget {
  const _VehicleLoadingCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.appBgMid,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.appNavBorder),
      ),
      child: const Row(
        children: [
          _SkeletonVehicleBadge(),
          SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _SkeletonLine(width: 180, height: 16),
                SizedBox(height: 10),
                _SkeletonLine(width: 120, height: 12),
                SizedBox(height: 8),
                _SkeletonLine(width: 140, height: 12),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SkeletonVehicleBadge extends StatelessWidget {
  const _SkeletonVehicleBadge();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        color: AppColors.appBgDeep,
        borderRadius: BorderRadius.circular(20),
      ),
    );
  }
}

class _SkeletonLine extends StatelessWidget {
  const _SkeletonLine({required this.width, required this.height});

  final double width;
  final double height;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: AppColors.appBgDeep,
        borderRadius: BorderRadius.circular(12),
      ),
    );
  }
}

class _VehiclesLoadedList extends StatelessWidget {
  const _VehiclesLoadedList({required this.vehicles});

  final List<Vehicle> vehicles;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      physics: const ClampingScrollPhysics(),
      itemCount: vehicles.length + 1,
      separatorBuilder: (_, _) => const SizedBox(height: 12),
      itemBuilder: (_, index) {
        if (index == vehicles.length) {
          return const _CreateVehicleButton();
        }

        final vehicle = vehicles[index];

        return VehicleCard(
          vehicle: vehicle,
          onTap: () => context.push('/user/vehicles/${vehicle.id}?fromSheet=1'),
        );
      },
    );
  }
}

class _CreateVehicleButton extends StatelessWidget {
  const _CreateVehicleButton();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 52,
      child: CustomFilledButton(
        onPressed: () => context.push('/user/vehicles/new?fromSheet=1'),
        text: 'Agregar vehiculo',
        buttonColor: AppColors.appAccent,
        textColor: AppColors.appAccentText,
        borderRadius: 22,
      ),
    );
  }
}
