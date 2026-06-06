class PaymentCheckoutSession {
  PaymentCheckoutSession({
    required this.paymentId,
    required this.checkoutSessionId,
    required this.checkoutUrl,
    required this.amount,
    required this.currency,
    required this.status,
  });

  final String paymentId;
  final String checkoutSessionId;
  final String checkoutUrl;
  final double amount;
  final String currency;
  final String status;
}
