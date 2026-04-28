import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile/config/theme/app_theme.dart';
import 'package:mobile/features/home/presentation/widgets/widgets.dart';
import 'package:mobile/features/incidents/presentation/widgets/widgets.dart';

class ClientHomeScreen extends ConsumerStatefulWidget {
  const ClientHomeScreen({super.key, this.reviewIncidentId});

  final String? reviewIncidentId;

  @override
  ConsumerState<ClientHomeScreen> createState() => _ClientHomeScreenState();
}

class _ClientHomeScreenState extends ConsumerState<ClientHomeScreen> {
  bool _hasOpenedReviewSheet = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _openReviewSheetIfNeeded();
    });
  }

  @override
  void didUpdateWidget(covariant ClientHomeScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.reviewIncidentId != widget.reviewIncidentId) {
      _hasOpenedReviewSheet = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _openReviewSheetIfNeeded();
      });
    }
  }

  Future<void> _openReviewSheetIfNeeded() async {
    if (!mounted || _hasOpenedReviewSheet) return;
    final incidentId = (widget.reviewIncidentId ?? '').trim();
    if (incidentId.isEmpty) return;

    _hasOpenedReviewSheet = true;
    await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => IncidentFeedbackSheet(incidentId: incidentId),
    );

    if (!mounted) return;
    context.go('/home/client');
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: AppColors.appBgBase,
      body: SingleChildScrollView(
        physics: const ClampingScrollPhysics(),
        child: Column(
          children: [
            SizedBox(
              height: size.height * 0.40,
              width: double.infinity,
              child: Stack(
                children: [
                  Positioned.fill(child: ClientLocationMapSection()),
                  Positioned.fill(
                    child: IgnorePointer(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              AppColors.appBgDeep.withValues(alpha: 0.40),
                              AppColors.appBgDeep.withValues(alpha: 0.18),
                              Colors.transparent,
                            ],
                            stops: const [0.0, 0.16, 0.38],
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SafeArea(child: _HomeHeader()),
                ],
              ),
            ),
            Transform.translate(
              offset: const Offset(0, -56),
              child: Container(
                width: double.infinity,
                decoration: const BoxDecoration(
                  color: AppColors.appBgBase,
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(28),
                    topRight: Radius.circular(28),
                  ),
                ),
                child: const Padding(
                  padding: EdgeInsets.fromLTRB(16, 24, 16, 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      ClientHelpButton(),
                      SizedBox(height: 16),
                      ClientQuickActions(),
                      SizedBox(height: 20),
                      ClientActiveServicesSection(),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HomeHeader extends StatelessWidget {
  const _HomeHeader();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        AppHeader(
          onDarkBackground: true,
          onProfileTap: () => context.push('/user'),
        ),
      ],
    );
  }
}
