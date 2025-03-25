from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from agendamento.models import Cliente, Barbeiro, Servico, Agendamento
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Cria dados de exemplo para o sistema'

    def handle(self, *args, **kwargs):
        # Criar barbeiros
        barbeiros = [
            {'username': 'joao', 'nome': 'João Silva', 'especialidade': 'Corte de Cabelo Masculino'},
            {'username': 'pedro', 'nome': 'Pedro Santos', 'especialidade': 'Barba'},
            {'username': 'marcos', 'nome': 'Marcos Oliveira', 'especialidade': 'Corte Feminino'},
        ]

        for barbeiro in barbeiros:
            user = User.objects.create_user(
                username=barbeiro['username'],
                password='123456',
                first_name=barbeiro['nome'].split()[0],
                last_name=barbeiro['nome'].split()[1]
            )
            Barbeiro.objects.create(
                usuario=user,
                telefone=f'(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}',
                especialidade=barbeiro['especialidade']
            )
            self.stdout.write(self.style.SUCCESS(f'Barbeiro {barbeiro["nome"]} criado com sucesso!'))

        # Criar clientes
        clientes = [
            {'username': 'cliente1', 'nome': 'Carlos Silva'},
            {'username': 'cliente2', 'nome': 'Maria Santos'},
            {'username': 'cliente3', 'nome': 'José Oliveira'},
        ]

        for cliente in clientes:
            user = User.objects.create_user(
                username=cliente['username'],
                password='123456',
                first_name=cliente['nome'].split()[0],
                last_name=cliente['nome'].split()[1]
            )
            Cliente.objects.create(
                usuario=user,
                telefone=f'(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}'
            )
            self.stdout.write(self.style.SUCCESS(f'Cliente {cliente["nome"]} criado com sucesso!'))

        # Criar alguns agendamentos
        servicos = Servico.objects.all()
        barbeiros = Barbeiro.objects.all()
        clientes = Cliente.objects.all()

        # Criar agendamentos para os próximos 7 dias
        for i in range(7):
            data = datetime.now() + timedelta(days=i)
            for hora in range(9, 18, 2):  # Horários das 9h às 17h
                if random.random() < 0.3:  # 30% de chance de criar um agendamento
                    agendamento = Agendamento.objects.create(
                        cliente=random.choice(clientes),
                        barbeiro=random.choice(barbeiros),
                        servico=random.choice(servicos),
                        data_hora=data.replace(hour=hora, minute=0),
                        status='AGENDADO'
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Agendamento criado: {agendamento.cliente} com {agendamento.barbeiro} '
                            f'para {agendamento.data_hora.strftime("%d/%m/%Y %H:%M")}'
                        )
                    ) 