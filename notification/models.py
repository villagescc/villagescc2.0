from django.db import models

from account.models import AmountField
from profile.models import Profile


class Notification(models.Model):
    # STATUS CHOICES
    READ = 'READ'
    NEW = 'NEW'

    STATUS_CHOICES = (
        (READ, 'Read'),
        (NEW, 'New')
    )

    # Notification types
    TRUST = 'TRUST'
    PAYMENT = 'PAYMENT'

    NOTIFICATION_TYPE_CHOICES = (
        (TRUST, 'Trust'),
        (PAYMENT, 'Payment')
    )

    notifier = models.ForeignKey(Profile, related_name='notifier', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Profile, related_name='notification_received', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    amount = AmountField(blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=NEW)
    created_at = models.DateTimeField(auto_now_add=True)
