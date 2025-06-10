from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

class Balance(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=8)

class Transaction(models.Model):
    TRANSACTION_TYPES = (('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('transfer', 'Transfer'))

    user_id = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

# You can expand models with DepositAddress, WithdrawalLimit, Settings, etc.
