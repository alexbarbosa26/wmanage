from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls import handler500
from pages.views import ProfileView
from two_factor.urls import urlpatterns as tf_urls
from django_otp.admin import OTPAdminSite
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django.conf.urls.static import static
from django.conf import settings

class OTPAdmin(OTPAdminSite):
    pass


admin_site = OTPAdmin(name='OTPAdmin')
admin_site.register(User)
admin_site.register(TOTPDevice, TOTPDeviceAdmin)

app_name = 'orcamento'

urlpatterns = [
    # Page Home
    path('', include('pages.urls', namespace="pages")),
    path('', include('core.urls')),
    path('', include('csvs.urls')),
    path('orcamento/', include(('orcamento.urls', app_name), namespace='orcamento')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('', include(tf_urls)),

    path('admin/', admin.site.urls),    
    path('account/', include('allauth.urls')),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),

    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='account/change-password.html',
            success_url='/password-reset-complete/'
        ),
        name='change_password'
    ),

    # Forget Password
    path('password-reset/', auth_views.PasswordResetView.as_view(
             template_name='password-reset/password-reset.html',
             subject_template_name='password-reset/password_reset_subject.txt',
             email_template_name='password-reset/password_reset_email.html',
            #  success_url='/accounts/login/'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password-reset/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password-reset/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password-reset/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500='core.views.error_500'
handler404='core.views.error_404'