from django.urls import reverse, resolve

class TestUrls:

    def test_login_url(self):
        path = reverse('admin_panel:login_page')
        assert resolve(path).view_name == 'admin_panel:login_page'
