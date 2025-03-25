from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Servico, Barbeiro, Agendamento, Cliente
from datetime import datetime, timedelta
from django.db.models import Q
from .forms import ClienteForm, LoginForm

def home(request):
    servicos = Servico.objects.filter(disponivel=True)
    barbeiros = Barbeiro.objects.filter(disponivel=True)
    return render(request, 'agendamento/home.html', {
        'servicos': servicos,
        'barbeiros': barbeiros
    })

def servicos(request):
    servicos = Servico.objects.filter(disponivel=True)
    return render(request, 'agendamento/servicos.html', {'servicos': servicos})

@login_required
def agendar(request):
    servicos = Servico.objects.filter(disponivel=True)
    barbeiros = Barbeiro.objects.filter(disponivel=True)
    
    # Gerar horários disponíveis (9h às 17h, a cada 2 horas)
    horarios = []
    for hora in range(9, 18, 2):
        horarios.append(f"{hora:02d}:00")
    
    if request.method == 'POST':
        servico_id = request.POST.get('servico')
        barbeiro_id = request.POST.get('barbeiro')
        data = request.POST.get('data')
        hora = request.POST.get('hora')
        
        try:
            data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
            data_hora = timezone.make_aware(data_hora)
            
            # Verificar se já existe agendamento para este horário
            if Agendamento.objects.filter(
                barbeiro_id=barbeiro_id,
                data_hora=data_hora,
                status='AGENDADO'
            ).exists():
                messages.error(request, 'Este horário já está agendado. Por favor, escolha outro horário.')
                return redirect('agendar')
            
            # Criar o agendamento
            agendamento = Agendamento.objects.create(
                cliente=request.user.cliente,
                barbeiro_id=barbeiro_id,
                servico_id=servico_id,
                data_hora=data_hora,
                status='AGENDADO'
            )
            
            messages.success(request, 'Agendamento realizado com sucesso!')
            return redirect('meus_agendamentos')
            
        except Exception as e:
            messages.error(request, 'Erro ao realizar agendamento. Por favor, tente novamente.')
    
    return render(request, 'agendamento/agendar.html', {
        'servicos': servicos,
        'barbeiros': barbeiros,
        'horarios': horarios,
        'today': timezone.now().strftime('%Y-%m-%d')
    })

@login_required
def meus_agendamentos(request):
    # Tentar obter o cliente, se não existir, criar um
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        cliente = Cliente.objects.create(usuario=request.user)
    
    agendamentos = Agendamento.objects.filter(
        cliente=cliente
    ).order_by('-data_hora')
    
    return render(request, 'agendamento/meus_agendamentos.html', {
        'agendamentos': agendamentos
    })

@login_required
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, cliente=request.user.cliente)
    
    if agendamento.status == 'AGENDADO':
        agendamento.status = 'CANCELADO'
        agendamento.save()
        messages.success(request, 'Agendamento cancelado com sucesso!')
    else:
        messages.error(request, 'Não é possível cancelar este agendamento.')
    
    return redirect('meus_agendamentos')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'agendamento/login.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Criar perfil de cliente automaticamente
            Cliente.objects.create(usuario=user)
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'agendamento/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('home')
