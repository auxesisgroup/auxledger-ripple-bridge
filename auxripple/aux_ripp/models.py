from django.db import models


class User_Master(models.Model):
    user_name = models.CharField(max_length=500)
    token = models.CharField(max_length=500)
    notification_url = models.URLField(max_length=500)
    app_key = models.CharField(max_length=500)
    app_secret = models.CharField(max_length=500)

    # Override String Representation
    def __str__(self):
        return self.user_name


class Address_Master(models.Model):
    user_name = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    public_key = models.CharField(max_length=500)
    enc_master_seed = models.CharField(max_length=500)
    enc_master_key = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)
    is_multi_sig = models.BooleanField(default=False)

    # Override String Representation
    def __str__(self):
        return self.user_name + ' - ' + str(self.is_active)


class Transaction_Master(models.Model):
    from_address = models.CharField(max_length=2500)
    to_address = models.CharField(max_length=2500)
    amount = models.CharField(max_length=2500)
    txid = models.CharField(max_length=2500)
    sequence = models.CharField(max_length=2500)
    ledger_index = models.CharField(max_length=2500)
    created_at = models.DateTimeField(auto_now_add=True)
    bid_id = models.CharField(max_length=2500)

    def __str__(self):
        return self.from_address + ' -> ' + self.to_address + ' : ' + self.amount

