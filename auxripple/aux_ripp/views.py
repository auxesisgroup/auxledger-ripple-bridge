# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import util
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ref_strings import UserExceptionStr


def who_is_hitting(func):
    def user_details(*args,**kwargs):
        # Before
        request = args[0]
        url = request.build_absolute_uri()
        ip = util.get_client_ip(request)
        log = "#"*100 + "\n"
        log += "From => " + str(ip) + "\n"
        log += "URL => " + str(url)
        log += '\nRequest Params => '
        for key,value in request.POST.items():
            log += key + " : " + value + ", "

        # Main
        response = func(*args,**kwargs)

        # After
        log += "\nResponse => " + str(response)
        log += "\n" + "#" * 100
        util.init_logger()
        util.logger.info(log)
        return response
    return user_details

@csrf_exempt
@who_is_hitting
def generate_new_address(request):
    """
    End point for generating new address
    Checks if the user is valid
    :param request:
    :return: address if the user is valid
    """
    if request.method == 'POST':
        try:
            user_name = request.POST.get('user_name')
            token = request.POST.get('token')
            enc_sec = request.POST.get('enc_sec')


            if not (user_name and token and enc_sec):
                raise util.UserException(UserExceptionStr.specify_required_fields)

            # Check if user is valid
            user_valid = util.check_user_validation(user_name=user_name,token=token,enc_sec=enc_sec)
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
                        return JsonResponse({'address': user_address,'active' : False,'status' : 200})
                    else:
                        raise util.UserException(UserExceptionStr.some_error_occurred)
                else:
                    raise util.UserException(UserExceptionStr.server_not_responding)
            else:
                raise util.UserException(UserExceptionStr.invalid_user)
        except util.UserException as e:
            return JsonResponse({'error': str(e), 'status': 400})
        except Exception as e:
            util.init_logger()
            util.logger.info("Error generate_new_address : " + str(e))
            return JsonResponse({'error': UserExceptionStr.bad_request,'status' : 400})


@csrf_exempt
@who_is_hitting
def get_balance(request):
    """
    End point for getting balance
    Checks if the user is valid
    :param request:
    :return: balance if the user is valid
    """
    if request.method == 'POST':
        try:
            user_name = request.POST.get('user_name')
            token = request.POST.get('token')
            enc_sec = request.POST.get('enc_sec')
            addresses = set(map(lambda x: x.strip(), request.POST.get('address').split(','))) if request.POST.get('address') else []

            if not (user_name and token and enc_sec and addresses):
                raise util.UserException(UserExceptionStr.specify_required_fields)

            # Check if user is valid
            user_valid = util.check_user_validation(user_name=user_name, token=token, enc_sec=enc_sec)
            if user_valid:
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
                        response_data.append({'address':address,'error':UserExceptionStr.address_not_owner})

                return JsonResponse({'result': response_data, 'status': 200})
            else:
                raise util.UserException(UserExceptionStr.invalid_user)
        except util.UserException as e:
            return JsonResponse({'error': str(e), 'status': 400})
        except Exception as e:
            util.init_logger()
            util.logger.info("Error get_balance : " + str(e))
            return JsonResponse({'error': UserExceptionStr.bad_request,'status' : 400})


@csrf_exempt
@who_is_hitting
def get_fee(request):
    """
    End point for getting fee for normal transaction
    Checks if the user is valid
    :param request:
    :return: fee if the user is valid
    """
    if request.method == 'POST':
        try:
            user_name = request.POST.get('user_name')
            token = request.POST.get('token')
            enc_sec = request.POST.get('enc_sec')

            if not (user_name and token and enc_sec):
                raise util.UserException(UserExceptionStr.specify_required_fields)

            # Check if user is valid
            user_valid = util.check_user_validation(user_name=user_name, token=token, enc_sec=enc_sec)
            if user_valid:
                fee = util.get_fee()
                return JsonResponse({'fee': fee, 'status': 200})
            else:
                raise util.UserException(UserExceptionStr.invalid_user)
        except util.UserException as e:
            return JsonResponse({'error': str(e), 'status': 400})
        except Exception as e:
            util.init_logger()
            util.logger.info("Error get_balance : " + str(e))
            return JsonResponse({'error': UserExceptionStr.bad_request,'status' : 400})
