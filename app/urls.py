from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

urlpatterns=[
	path('', views.index, name='index'),
	path('register', views.RegistrationView.as_view(), name='register'),
	path('login', views.LoginView.as_view(), name='login'),
	path('profile', views.profile, name='profile'),
	path('logout', views.LogoutView.as_view(), name='logout'),
	path('user/<int:id>/', views.user_profile, name='user-profile'),
	path('home', login_required(views.HomeView.as_view()), name='home'),
	path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
