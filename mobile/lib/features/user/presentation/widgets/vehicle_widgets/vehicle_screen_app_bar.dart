import 'package:flutter/material.dart';
import 'package:mobile/config/theme/app_theme.dart';

class VehicleScreenAppBar extends StatelessWidget
    implements PreferredSizeWidget {
  const VehicleScreenAppBar({
    super.key,
    required this.title,
    required this.showDeleteAction,
    required this.isPosting,
    this.onDeletePressed,
  });

  final String title;
  final bool showDeleteAction;
  final bool isPosting;
  final Future<void> Function()? onDeletePressed;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title),
      foregroundColor: AppColors.appAccent,
      iconTheme: const IconThemeData(color: AppColors.appAccent),
      titleTextStyle: Theme.of(context).textTheme.titleSmall?.copyWith(
        color: AppColors.appAccent,
        fontWeight: FontWeight.w800,
      ),
      centerTitle: true,
      actions: [
        if (showDeleteAction)
          IconButton(
            onPressed: isPosting
                ? null
                : () async {
                    await onDeletePressed?.call();
                  },
            icon: const Icon(Icons.delete_outline_rounded),
            tooltip: 'Eliminar vehiculo',
            color: AppColors.appAccent,
          ),
      ],
    );
  }
}
