from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import redirect
from ref_strings import UserExceptionStr
import util
from views import log_out
from django.utils.deprecation import MiddlewareMixin


class AutoLogout(MiddlewareMixin):

    def process_request(self, request):
        if not util.session_check_user_valid(request) :
          #Can't log out if not logged in
          return

        try:
            if datetime.now() - request.session['last_touch'] > timedelta( 0, settings.AUTO_LOGOUT_DELAY, 0):
                del request.session['last_touch']
                redirect('admin_panel:log_out', reason=UserExceptionStr.bad_request)
                return
        except KeyError:
            pass

        request.session['last_touch'] = datetime.now()