from .models import Account

def get_email_from_address(address):
    return Account.objects.filter(address = address).values('email')[0]['email']