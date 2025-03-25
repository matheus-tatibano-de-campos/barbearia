from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('servicos/', views.servicos, name='servicos'),
    path('agendar/', views.agendar, name='agendar'),
    path('meus-agendamentos/', views.meus_agendamentos, name='meus_agendamentos'),
    path('cancelar-agendamento/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('api/horarios/', views.get_horarios_disponiveis, name='api_horarios'),
] 