# Sistema de Agendamento para Barbearia

Um sistema web desenvolvido com Django para gerenciamento de agendamentos em barbearias.

## Funcionalidades

- Cadastro de clientes
- Cadastro de barbeiros
- Gerenciamento de serviços
- Agendamento de horários
- Visualização de agendamentos
- Sistema de login e autenticação

## Tecnologias Utilizadas

- Python 3.13
- Django 5.1.4
- Bootstrap 5
- Font Awesome
- SQLite3

## Como executar o projeto

1. Clone este repositório
```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd barbearia
```

2. Crie um ambiente virtual e ative-o
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Execute as migrações
```bash
python manage.py migrate
```

5. Crie um superusuário (opcional)
```bash
python manage.py createsuperuser
```

6. Inicie o servidor
```bash
python manage.py runserver
```

O sistema estará disponível em `http://localhost:8000`

## Contribuindo

1. Faça o fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Faça commit das suas alterações (`git commit -m 'Add some AmazingFeature'`)
4. Faça push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 