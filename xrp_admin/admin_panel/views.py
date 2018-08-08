# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import util
from django.shortcuts import render,redirect
# from models import User_Master,Panel_Master
from models import Panel_Master


def check_user_valid(roles):
    def check_user_1(func):
        def check_user_2(*args,**kwargs):
            try:
                authentic = args[0].session['authentic']
                user_role = args[0].session['user_role']
                if authentic and user_role in roles:
                    user_name = args[0].session['user_name']
                    # Super Admin
                    if util.check_super_user_valid(user_name,user_role):
                        return func(*args,**kwargs)
                    else:
                        if util.check_admin_user_valid(user_name,user_role):
                            return func(*args, **kwargs)
                        else:
                            return redirect('admin_panel:log_out')
                else:
                    return redirect('admin_panel:log_out')

            except Exception as e:
                return redirect('admin_panel:log_out')

        return check_user_2
    return check_user_1


def login_page(request):
    template = 'admin_panel/login_page.html'

    if request.method == 'GET':
        return render(request,template)

    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        authentic, super_admin = util.super_user_authenticate(user_name,password)

        if authentic and super_admin:
            request.session['authentic'] = authentic
            request.session['user_name'] = user_name
            request.session['user_role'] = 'Super_Admin'
            return redirect('admin_panel:super_admin_home')
        else:
            authentic, role = util.admin_user_authenticate(user_name,password)
            if authentic:
                request.session['authentic'] = authentic
                request.session['user_name'] = user_name
                request.session['user_role'] = role
                return redirect('admin_panel:admin_home')
            else:
                template = 'admin_panel/login_page.html'
                error_message = 'Incorrect id and password'
                context = {
                    'error_message': error_message,
                }
                return render(request, template, context=context)


def log_out(request):
    request.session['authentic'] = ''
    request.session['user_role'] = ''
    request.session['user_name'] = ''
    return redirect('admin_panel:login_page')


@check_user_valid(['Super_Admin'])
def super_admin_home(request):
    template = 'admin_panel/super_admin_home.html'
    if request.method == 'GET':
        try:
            user_data = util.get_super_admin_home_data()
            context = {
                'user_data' : user_data,
            }
            return render(request,template,context=context)
        except Exception as e:
            context = {
                'result': 'Error : ' + str(e),
            }
            return render(request, template, context=context)


@check_user_valid(['Super_Admin'])
def super_admin_user_details(request, user_name):
    template = 'admin_panel/admin_home_user_tx_details.html'
    if request.method == 'GET':
        try:
            tx_data, total_transactions, sent, received, balance_info, total_balance = util.get_transaction_data(user_name)

            balance_html = ''
            for info in balance_info:
                for address, balance in info.items():
                    balance_html += '%s : %s ' % (address, balance)

            context = {
                'tx_data': tx_data,
                'total_transactions': total_transactions,
                'sent': sent,
                'received': received,
                'balance': float(total_balance / 10 ** 6),
                'balance_info': balance_html
            }

            return render(request,template,context=context)
        except Exception as e:
            context = {
                'result': 'Error : ' + str(e),
            }
            return render(request, template, context=context)


@check_user_valid(['admin','manager','customer_service'])
def admin_home(request):
    template = 'admin_panel/admin_home_user_tx_details.html'
    if request.method == 'GET':
        try:
            user_name = request.session.get('user_name')
            app_user = util.get_admin_application_user(user_name)
            tx_data, total_transactions, sent, received, balance_info, total_balance = util.get_transaction_data(app_user)

            balance_html = ''
            for info in balance_info:
                for address,balance in info.items():
                    balance_html += '%s : %s ' % (address, balance)

            context = {
                'tx_data': tx_data,
                'total_transactions' : total_transactions,
                'sent': sent,
                'received': received,
                'balance': float(total_balance/10**6),
                'balance_info': balance_html
            }
            return render(request, template, context=context)
        except Exception as e:
            context = {
                'result': 'Error : ' + str(e),
            }
            return render(request, template, context=context)


@check_user_valid(['Super_Admin'])
def super_add_app_user(request):
    template = 'admin_panel/super_add_app_user.html'

    if request.method == 'GET':
        try:
            app_user_data = util.get_super_app_user_data()
            context = {
                'app_user_data' : app_user_data,
            }
            return render(request,template,context=context)
        except Exception as e:
            context = {
                'result': 'Error : ' + str(e),
            }
            return render(request, template, context=context)


    if request.method == 'POST':
        try:
            app_user_name = request.POST.get('app_user_name')
            app_user_url = request.POST.get('app_user_url')
            token = util.get_token()
            app_key = app_user_name + '_TOKEN'
            app_secret = util.get_token()

            # Add App User
            util.create_user(
                user_name = app_user_name,
                token = token,
                notification_url = app_user_url,
                app_key = app_key,
                app_secret = app_secret
            )

            app_user_data = util.get_super_app_user_data()
            context = {
                'result': 'Success!',
                'app_user_data': app_user_data,
            }

            return render(request, template, context = context)
        except Exception as e:
            app_user_data = util.get_super_app_user_data()
            context = {
                'result': 'Error : User already exist!',
                'app_user_data': app_user_data,
            }
            return render(request, template, context = context)


@check_user_valid(['Super_Admin'])
def super_add_panel_user(request):
    template = 'admin_panel/super_add_panel_user.html'
    if request.method == 'GET':
        try:
            app_users, panel_data = util.get_super_panel_user_data()
            context = {
                'app_users': app_users,
                'panel_data': panel_data,
            }
            return render(request,template,context=context)
        except Exception as e:
            context = {
                'result': 'Error : ' + str(e),
            }
            return render(request, template, context=context)

    if request.method == 'POST':
        try:
            application_user = request.POST.get('panel_app_user')
            panel_user_name = request.POST.get('panel_user_name')
            password = request.POST.get('panel_password')
            role = request.POST.get('panel_role')
            mobile = request.POST.get('panel_mobile_number')

            # Add Panel User
            user = Panel_Master.objects.create(
                application_user=application_user,
                panel_user_name=panel_user_name,
                password=password,
                role=role,
                mobile=mobile
            )
            user.save()

            app_users, panel_data = util.get_super_panel_user_data()
            context = {
                'result': 'Success',
                'app_users': app_users,
                'panel_data': panel_data,
            }
            return render(request, template, context=context)

        except Exception as e:
            app_users, panel_data = util.get_super_panel_user_data()
            context = {
                'result': 'Error : User already exist!',
                'app_users': app_users,
                'panel_data': panel_data,
            }
            return render(request, template, context = context)


@check_user_valid(['admin'])
def admin_add_panel_user(request):
    user_name = request.session.get('user_name')
    template = 'admin_panel/admin_add_panel_user.html'
    if request.method == 'GET':
        try:
            panel_data = util.get_admin_panel_user_data(user_name)
            context = {
                'panel_data': panel_data,
            }
            return render(request,template,context=context)
        except Exception as e:
            context = {
                'result': 'Error : ' + str(e),
            }
            return render(request, template, context=context)

    if request.method == 'POST':
        try:
            panel_user_name = request.POST.get('admin_panel_user_name')
            application_user = util.get_admin_application_user(user_name)
            password = request.POST.get('admin_panel_password')
            role = request.POST.get('admin_panel_role')
            mobile = request.POST.get('admin_panel_mobile_number')

            # Add Panel User
            user = Panel_Master.objects.create(
                application_user=application_user,
                panel_user_name=panel_user_name,
                password=password,
                role=role,
                mobile=mobile
            )
            user.save()

            panel_data = util.get_admin_panel_user_data(user_name)
            context = {
                'result': 'Success!',
                'panel_data': panel_data,
            }
            return render(request, template, context=context)

        except Exception as e:
            panel_data = util.get_admin_panel_user_data(user_name)
            context = {
                'result': 'Error : User already exist! : ' + str(e),
                'panel_data': panel_data,
            }
            return render(request, template, context = context)


@check_user_valid(['admin'])
def admin_edit_url(request):
    user_name = request.session.get('user_name')
    template = 'admin_panel/admin_edit_url.html'
    if request.method == 'GET':
        try:
            panel_data = util.get_admin_app_user_data(user_name)
            context = {
                'app_user_data': panel_data,
            }
            return render(request,template,context=context)
        except Exception as e:
            context = {
                'result': 'Error : ' + str(e),
            }
            return render(request, template, context=context)

    if request.method == 'POST':
        try:
            notification_url = request.POST.get('admin_notification_url')
            application_user = util.get_admin_application_user(user_name)

            # Update Notification URL
            util.update_user_url(user_name=application_user,notification_url = notification_url)

            panel_data = util.get_admin_app_user_data(user_name)
            context = {
                'app_user_data': panel_data,
            }
            return render(request, template, context=context)

        except Exception as e:
            panel_data = util.get_admin_app_user_data(user_name)
            context = {
                'app_user_data': panel_data,
            }
            return render(request, template, context = context)