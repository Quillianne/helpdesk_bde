from django.contrib import admin
from django.urls import path, include
from events import views as events_views
from acces import views as acces_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', acces_views.home, name='home'),  # Page d'accueil
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),
    path('acces/', include('acces.urls', namespace='acces')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
