from django.urls import path
from . import views  # Import correct du module views depuis le répertoire actuel

urlpatterns = [
    path('', views.home, name="home"),
    path('register', views.register, name='register'),
    path('login', views.logIn, name='login'),
    path('logout', views.logOut, name='logout'),  # Suppression de l'espace après 'views.'
    path('activate/<uidb64>/<token>', views.activate, name="activate")  # Suppression de l'espace après 'views.'
]
