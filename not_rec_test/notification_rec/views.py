# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from django.http import JsonResponse

# Create your views here.
@csrf_exempt
def receive_notification(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            app_key = str(json_data.get('app_key'))
            app_secret = str(json_data.get('app_secret'))

            # Hardcoded
            app_keys = ['123456']
            app_secrets = ['abcdef']

            if app_key in app_keys and app_secret in app_secrets:
                amount = json_data.get('amount')
                from_address = json_data.get('from_address')
                destination_tag = json_data.get('destination_tag')
                transaction_hash = json_data.get('transaction_hash')
                to_address = json_data.get('to_address')
                ledger_number = json_data.get('ledger_number')

                notification_text = 'You have received an amount of %s from %s on %s with' \
                                    ' Destination Tag %s. Hash : %s, ledger : %s'%(amount,from_address,to_address,
                                                                      destination_tag,transaction_hash,ledger_number)
                print('-' * 100)
                print(notification_text)
                print('-' * 100)
            else:
                return JsonResponse({'error ' : 'Bad Request','status_code' : 400 })

        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'result' : True})