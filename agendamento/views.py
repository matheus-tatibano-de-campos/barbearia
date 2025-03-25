from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.http import JsonResponse
from .models import Servico, Barbeiro, Agendamento, Cliente
from datetime import datetime, timedelta, date
from django.db.models import Q
from .forms import ClienteForm, LoginForm, AgendamentoForm

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

def gerar_horarios_disponiveis(data, barbeiro_id=None, servico_id=None):
    """
    Gera horários disponíveis para agendamento a cada 30 minutos,
    considerando o horário de funcionamento e agendamentos existentes.
    """
    horarios = []
    hora_inicio = 9  # 9:00
    hora_fim = 18    # 18:00
    
    # Se não foi selecionado barbeiro ou serviço, retorna todos os horários possíveis
    if not barbeiro_id or not servico_id:
        current_time = datetime.strptime(f"{hora_inicio}:00", "%H:%M")
        end_time = datetime.strptime(f"{hora_fim}:00", "%H:%M")
        
        while current_time < end_time:
            horarios.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)
        
        return horarios

    # Busca a duração do serviço selecionado
    try:
        servico = Servico.objects.get(id=servico_id)
        duracao_servico = servico.duracao
    except Servico.DoesNotExist:
        return []

    # Busca todos os agendamentos do barbeiro para a data selecionada
    data_inicio = datetime.strptime(f"{data} {hora_inicio}:00", "%Y-%m-%d %H:%M")
    data_fim = datetime.strptime(f"{data} {hora_fim}:00", "%Y-%m-%d %H:%M")
    
    # Converte para aware datetime
    data_inicio = timezone.make_aware(data_inicio)
    data_fim = timezone.make_aware(data_fim)

    agendamentos = Agendamento.objects.filter(
        barbeiro_id=barbeiro_id,
        data_hora__date=data_inicio.date(),
        status='AGENDADO'
    ).order_by('data_hora')

    # Cria uma lista de intervalos ocupados
    horarios_ocupados = []
    for agendamento in agendamentos:
        inicio = agendamento.data_hora
        fim = inicio + timedelta(minutes=agendamento.servico.duracao)
        horarios_ocupados.append((inicio, fim))

    # Gera todos os horários possíveis a cada 30 minutos
    current_time = data_inicio
    while current_time < data_fim:
        # Verifica se o horário + duração do serviço não conflita com nenhum agendamento
        horario_fim = current_time + timedelta(minutes=duracao_servico)
        horario_disponivel = True

        for inicio_ocupado, fim_ocupado in horarios_ocupados:
            if (current_time < fim_ocupado and horario_fim > inicio_ocupado):
                horario_disponivel = False
                break

        if horario_disponivel:
            horarios.append(current_time.strftime("%H:%M"))

        current_time += timedelta(minutes=30)

    return horarios

@login_required
def agendar(request):
    servicos = Servico.objects.filter(disponivel=True)
    barbeiros = Barbeiro.objects.filter(disponivel=True)
    horarios = []
    data_selecionada = request.GET.get('data') or timezone.now().date().strftime('%Y-%m-%d')
    servico_selecionado = request.GET.get('servico', '')
    barbeiro_selecionado = request.GET.get('barbeiro', '')

    if servico_selecionado and barbeiro_selecionado and data_selecionada:
        horarios = gerar_horarios_disponiveis(
            data_selecionada,
            barbeiro_selecionado,
            servico_selecionado
        )
    
    if request.method == 'POST':
        servico_id = request.POST.get('servico')
        barbeiro_id = request.POST.get('barbeiro')
        data = request.POST.get('data')
        hora = request.POST.get('hora')
        
        try:
            data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
            data_hora = timezone.make_aware(data_hora)
            
            servico = Servico.objects.get(id=servico_id)
            horario_fim = data_hora + timedelta(minutes=servico.duracao)
            
            agendamento_conflitante = Agendamento.objects.filter(
                barbeiro_id=barbeiro_id,
                status='AGENDADO',
                data_hora__lt=horario_fim,
                data_hora__gt=data_hora
            ).exists()
            
            if agendamento_conflitante:
                messages.error(request, 'Este horário já não está mais disponível. Por favor, escolha outro horário.')
                # Preserva os parâmetros selecionados no redirect
                return redirect(f"{request.path}?servico={servico_id}&barbeiro={barbeiro_id}&data={data}")
            
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
            # Opcional: re-renderize o template com os dados atuais em vez de redirecionar
            return redirect(f"{request.path}?servico={servico_id}&barbeiro={barbeiro_id}&data={data}")
    
    return render(request, 'agendamento/agendar.html', {
        'servicos': servicos,
        'barbeiros': barbeiros,
        'horarios': horarios,
        'today': timezone.now().strftime('%Y-%m-%d'),
        'data_selecionada': data_selecionada,
        'barbeiro_selecionado': barbeiro_selecionado,
        'servico_selecionado': servico_selecionado
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

def api_horarios(request):
    """
    View de API que retorna os horários disponíveis em formato JSON.
    Parâmetros GET: servico, barbeiro, data
    """
    servico = request.GET.get('servico')
    barbeiro = request.GET.get('barbeiro')
    data = request.GET.get('data')
    
    if servico and barbeiro and data:
        horarios = gerar_horarios_disponiveis(data, barbeiro, servico)
    else:
        horarios = []
    
    return JsonResponse({'horarios': horarios})

def get_horarios_disponiveis(request):
    """API para retornar horários disponíveis"""
    servicos_ids = request.GET.get('servico', '').split(',')
    barbeiro_id = request.GET.get('barbeiro')
    data_str = request.GET.get('data')
    
    if not all([servicos_ids, barbeiro_id, data_str]):
        return JsonResponse({'error': 'Parâmetros incompletos'}, status=400)
    
    try:
        servicos = Servico.objects.filter(id__in=servicos_ids)
        if not servicos.exists():
            return JsonResponse({'error': 'Nenhum serviço encontrado'}, status=400)
            
        duracao_total = sum(servico.duracao for servico in servicos)
        barbeiro = Barbeiro.objects.get(id=barbeiro_id)
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
    except (Servico.DoesNotExist, Barbeiro.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Parâmetros inválidos'}, status=400)
    
    # Horário de funcionamento
    INICIO_EXPEDIENTE = datetime.strptime('09:00', '%H:%M').time()
    FIM_EXPEDIENTE = datetime.strptime('18:00', '%H:%M').time()
    INTERVALO_MINUTOS = 30
    
    # Buscar todos os agendamentos do dia
    data_inicio = timezone.make_aware(datetime.combine(data, INICIO_EXPEDIENTE))
    data_fim = timezone.make_aware(datetime.combine(data, FIM_EXPEDIENTE))
    
    agendamentos = Agendamento.objects.filter(
        barbeiro=barbeiro,
        data_hora__date=data,
        status='AGENDADO'
    ).order_by('data_hora')

    # Criar lista de intervalos ocupados
    horarios_ocupados = []
    for agendamento in agendamentos:
        inicio = agendamento.data_hora
        fim = inicio + timedelta(minutes=agendamento.servico.duracao)
        horarios_ocupados.append((inicio, fim))
    
    # Gerar todos os horários possíveis do dia
    horarios = []
    horario_atual = data_inicio
    
    while horario_atual.time() <= FIM_EXPEDIENTE:
        # Não agendar no passado
        if data == timezone.now().date() and horario_atual.time() < timezone.now().time():
            horario_atual += timedelta(minutes=INTERVALO_MINUTOS)
            continue
            
        # Verificar se o serviço cabe no horário antes do fim do expediente
        fim_servico = horario_atual + timedelta(minutes=duracao_total)
        
        if fim_servico.time() <= FIM_EXPEDIENTE:
            # Verificar se o horário está disponível
            horario_disponivel = True
            
            for inicio_ocupado, fim_ocupado in horarios_ocupados:
                # Verifica se há sobreposição de horários
                if (horario_atual < fim_ocupado and fim_servico > inicio_ocupado):
                    horario_disponivel = False
                    break
            
            if horario_disponivel:
                horarios.append(horario_atual.strftime('%H:%M'))
        
        horario_atual += timedelta(minutes=INTERVALO_MINUTOS)
    
    return JsonResponse({'horarios': horarios})
