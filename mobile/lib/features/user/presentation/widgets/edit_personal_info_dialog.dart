import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/features/shared/shared.dart';
import 'package:mobile/features/user/presentation/providers/providers.dart';

class EditPersonalInfoDialog extends ConsumerStatefulWidget {
  const EditPersonalInfoDialog({
    super.key,
    required this.firstName,
    required this.lastName,
    required this.phone,
  });

  final String firstName;
  final String lastName;
  final String phone;

  @override
  ConsumerState<EditPersonalInfoDialog> createState() =>
      _EditPersonalInfoDialogState();
}

class _EditPersonalInfoDialogState
    extends ConsumerState<EditPersonalInfoDialog> {
  late final TextEditingController _firstNameController;
  late final TextEditingController _lastNameController;
  late final TextEditingController _phoneController;

  @override
  void initState() {
    super.initState();
    _firstNameController = TextEditingController(text: widget.firstName);
    _lastNameController = TextEditingController(text: widget.lastName);
    _phoneController = TextEditingController(text: widget.phone);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      ref
          .read(personalInfoFormProvider.notifier)
          .setInitialValues(
            firstName: widget.firstName,
            lastName: widget.lastName,
            phone: widget.phone,
          );
    });
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final formState = ref.watch(personalInfoFormProvider);
    final formNotifier = ref.read(personalInfoFormProvider.notifier);

    Future<void> onSubmit() async {
      final isSuccess = await formNotifier.submit();
      if (!context.mounted) return;

      if (isSuccess) {
        Navigator.of(context).pop(true);
        return;
      }

      final message = ref.read(personalInfoFormProvider).errorMessage;
      if (message.isEmpty) return;

      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: Colors.red.shade800,
          ),
        );
    }

    return AppDialogShell(
      title: 'Editar informacion personal',
      description:
          'Actualiza tu nombre, apellido y telefono para mantener tus datos al dia.',
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AppFormLayout(
            submitText: 'Guardar cambios',
            onSubmit: formState.isPosting ? null : onSubmit,
            fields: [
              CustomTextFormField(
                label: 'Nombre',
                controller: _firstNameController,
                onChanged: formNotifier.onFirstNameChange,
                errorMessage: formState.isFormPosted
                    ? formState.firstName.errorMessage
                    : null,
              ),
              CustomTextFormField(
                label: 'Apellido',
                controller: _lastNameController,
                onChanged: formNotifier.onLastNameChange,
                errorMessage: formState.isFormPosted
                    ? formState.lastName.errorMessage
                    : null,
              ),
              CustomTextFormField(
                label: 'Telefono',
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                onChanged: formNotifier.onPhoneChange,
                errorMessage: formState.isFormPosted
                    ? formState.phone.errorMessage
                    : null,
              ),
            ],
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: formState.isPosting
                  ? null
                  : () => Navigator.of(context).pop(false),
              child: const Text('Cancelar'),
            ),
          ),
        ],
      ),
    );
  }
}
