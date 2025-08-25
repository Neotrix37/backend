# PDV System Backend

Backend do Sistema PDV desenvolvido com FastAPI para gestão de produtos, funcionários e sincronização com PDV offline.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados
- **JWT** - Autenticação segura
- **Alembic** - Migrações de banco

## 📁 Estrutura do Projeto

```
backend-pdv/
├── app/
│   ├── api/           # Rotas da API
│   ├── core/          # Configurações e utilitários
│   ├── models/        # Modelos do banco de dados
│   ├── schemas/       # Schemas Pydantic
│   ├── crud/          # Operações CRUD
│   └── auth/          # Autenticação e autorização
├── main.py            # Arquivo principal
├── requirements.txt   # Dependências Python
└── env.example        # Exemplo de variáveis de ambiente
```

## 🛠️ Instalação

### 1. Clonar o repositório
```bash
git clone <repository-url>
cd backend-pdv
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
cp env.example .env
# Editar .env com suas configurações
```

### 5. Configurar banco de dados
```bash
# Instalar PostgreSQL e criar banco 'pdv_system'
# Configurar DATABASE_URL no .env
```

### 6. Executar migrações
```bash
alembic upgrade head
```

### 7. Executar aplicação
```bash
python main.py
# ou
uvicorn main:app --reload
```

## 📚 Documentação da API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens) para autenticação:

1. **Login**: `POST /api/v1/auth/login`
2. **Token**: Incluir no header: `Authorization: Bearer <token>`

## 📊 Endpoints Principais

### Autenticação
- `POST /api/v1/auth/login` - Login de usuário
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Dados do usuário atual

### Produtos
- `GET /api/v1/products` - Listar produtos
- `POST /api/v1/products` - Criar produto
- `GET /api/v1/products/{id}` - Buscar produto
- `PUT /api/v1/products/{id}` - Atualizar produto
- `DELETE /api/v1/products/{id}` - Deletar produto

### Funcionários
- `GET /api/v1/employees` - Listar funcionários
- `POST /api/v1/employees` - Criar funcionário
- `GET /api/v1/employees/{id}` - Buscar funcionário
- `PUT /api/v1/employees/{id}` - Atualizar funcionário
- `DELETE /api/v1/employees/{id}` - Deletar funcionário

### Sincronização
- `POST /api/v1/sync/upload-sales` - Enviar vendas do PDV
- `GET /api/v1/sync/download-updates` - Buscar atualizações
- `POST /api/v1/sync/confirm-sync` - Confirmar sincronização

## 🔄 Sincronização

O sistema permite sincronização bidirecional entre:
- **PDV Offline** (Python + SQLite)
- **Backend Online** (FastAPI + PostgreSQL)

### Fluxo de Sincronização
1. PDV offline armazena vendas localmente
2. Quando conecta à internet, envia vendas para o backend
3. Backend envia atualizações (produtos, preços, funcionários)
4. PDV atualiza dados locais

## 🧪 Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=app
```

## 🚀 Deploy

### Desenvolvimento
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Produção
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📝 Licença

Este projeto está sob a licença MIT.

## 👥 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request 