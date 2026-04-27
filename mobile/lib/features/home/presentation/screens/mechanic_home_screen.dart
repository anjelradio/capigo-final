import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/assignments/assignments.dart';
import 'package:mobile/features/home/presentation/widgets/widgets.dart';

class MechanicHomeScreen extends ConsumerStatefulWidget {
  const MechanicHomeScreen({super.key});

  @override
  ConsumerState<MechanicHomeScreen> createState() => _MechanicHomeScreenState();
}

class _MechanicHomeScreenState extends ConsumerState<MechanicHomeScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() async {
      final notifier = ref.read(mechanicActiveAssignmentProvider.notifier);
      await notifier.loadActiveAssignment();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(mechanicActiveAssignmentProvider);
    final notifier = ref.read(mechanicActiveAssignmentProvider.notifier);

    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const ClampingScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                AppHeader(onProfileTap: () => context.push('/user')),
                const SizedBox(height: 8),
                MechanicActiveServiceCard(
                  assignment: state.assignment,
                  activeSince: state.activeSince,
                  isLoading: state.isLoading,
                  isRefreshing: state.isRefreshing,
                  isSyncingLocation: state.isSyncingLocation,
                  locationSyncAt: state.locationSyncAt,
                  onRefresh: notifier.refreshActiveAssignment,
                  onOpenService: () {
                    if (state.assignment == null) return;
                    context.push('/incidents/mechanic/active-service');
                  },
                ),
                if (state.errorMessage.trim().isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(
                    state.errorMessage,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: const Color(0xFFE38A8A),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
                const SizedBox(height: 12),
                MechanicTodaySummaryCards(
                  completedToday: state.todayStats?.completedToday ?? 0,
                  cancelledToday: state.todayStats?.cancelledToday ?? 0,
                ),
                const SizedBox(height: 12),
                const MechanicQuickActions(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
