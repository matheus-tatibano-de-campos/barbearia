from django.contrib import admin
from .models import Cliente, Barbeiro, Servico, Agendamento

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefone', 'data_cadastro')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'telefone')
    list_filter = ('data_cadastro',)

@admin.register(Barbeiro)
class BarbeiroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefone', 'especialidade', 'disponivel', 'data_cadastro')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'especialidade')
    list_filter = ('disponivel', 'especialidade', 'data_cadastro')

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'duracao', 'disponivel')
    search_fields = ('nome', 'descricao')
    list_filter = ('disponivel',)

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'barbeiro', 'servico', 'data_hora', 'status')
    search_fields = (
        'cliente__usuario__username',
        'barbeiro__usuario__username',
        'servico__nome'
    )
    list_filter = ('status', 'data_hora', 'barbeiro', 'servico')
    readonly_fields = ('data_agendamento', 'ultima_atualizacao')
