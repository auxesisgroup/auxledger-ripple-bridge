# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import util
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def generate_new_address(request):
    if request.method == 'POST':
        try:
            user_name = request.POST.get('user_name')
            token = request.POST.get('token')
            app_key = request.POST.get('app_key')
            app_secret = request.POST.get('app_secret')
            util.logger.info("Validating User : ")
            # Check if user is valid
            user_valid = util.check_user_validation(user_name=user_name,token=token,app_key=app_key,app_secret=app_secret)
            if user_valid:
                result_user = util.generate_address()
                if result_user:
                    user_address = str(result_user['account_id'])
                    user_secret = str(result_user['master_seed'])
                    public_key = str(result_user['public_key'])
                    master_key = str(result_user['master_key'])
                    enc_master_seed = util.encrypt_secret_key(token,user_secret)
                    enc_master_key = util.encrypt_secret_key(token,master_key)
                    result = util.insert_address_master(user_name=user_name,address=user_address,public_key=public_key,enc_master_seed=enc_master_seed,enc_master_key=enc_master_key,is_multi_sig=False)
                    if result :
                        util.RED.sadd('xrp_aw_set',user_address)
                        return JsonResponse({'address': user_address,'active' : False,'HTTPStatus' : 200})
                    else:
                        raise Exception('Some Error occurred.')
                else:
                    raise Exception('Invalid Input')
            else:
                raise Exception('Invalid User')
        except Exception as e:
            return JsonResponse({'error': str(e),'HTTPStatus' : 400})


@csrf_exempt
def get_balance(request):
    if request.method == 'POST':
        try:
            user_name = request.POST.get('user_name')
            token = request.POST.get('token')
            app_key = request.POST.get('app_key')
            app_secret = request.POST.get('app_secret')
            # Check if user is valid
            user_valid = util.check_user_validation(user_name=user_name,token=token,app_key=app_key,app_secret=app_secret)
            if user_valid:
                addresses = set(map(lambda x : x.strip(),request.POST.get('address').split(',')))
                response_data = []
                # Check if address correspond to the user
                for address in addresses:
                    address_valid = util.check_address_valid(user_name=user_name,address=address)
                    if address_valid:
                        data,result = util.get_account_balance(address)
                        if result:
                            response_data.append({'address':address,'balance': data})
                        else:
                            response_data.append({'address': address, 'error': data})
                    else:
                        response_data.append({'address':address,'error':'This address does not correspond to the user.'})

                return JsonResponse({'result': response_data, 'HTTPStatus': 200})
            else:
                raise Exception('Invalid User')
        except Exception as e:
            return JsonResponse({'error': str(e),'HTTPStatus' : 400})


@csrf_exempt
def get_fee(request):
    if request.method == 'POST':
        try:
            user_name = request.POST.get('user_name')
            token = request.POST.get('token')
            app_key = request.POST.get('app_key')
            app_secret = request.POST.get('app_secret')
            # Check if user is valid
            user_valid = util.check_user_validation(user_name=user_name,token=token,app_key=app_key,app_secret=app_secret)
            if user_valid:
                fee = util.get_fee()
                return JsonResponse({'fee': fee, 'HTTPStatus': 200})
            else:
                raise Exception('Invalid User')
        except Exception as e:
            return JsonResponse({'error': str(e),'HTTPStatus' : 400})
