# Documentação do Backend

## Visão Geral
O backend do sistema é construído usando Python com FastAPI, SQLAlchemy para ORM e PostgreSQL como banco de dados. A aplicação segue uma arquitetura limpa com separação clara de responsabilidades entre modelos, rotas e serviços.

## Estrutura de Diretórios

```
app/
├── api/
│   └── api_v1/          # Rotas da API versão 1
├── core/                # Configurações e utilitários principais
├── models/              # Modelos do banco de dados
└── schemas/             # Esquemas Pydantic para validação
```

## Autenticação

O sistema utiliza autenticação JWT (JSON Web Tokens) com os seguintes fluxos:

- **Login**: `/auth/login` - Gera um token de acesso
- **Verificação de Token**: Middleware para validar tokens em requisições
- **Papéis de Usuário**:
  - `admin`: Acesso total ao sistema
  - `manager`: Gerenciamento de produtos e vendas
  - `cashier`: Operações de PDV
  - `viewer`: Apenas visualização

## Banco de Dados

### Tabelas Principais

#### 1. users
Armazena os usuários do sistema.
- **Campos**:
  - `id` (PK)
  - `username` (único)
  - `email` (único)
  - `hashed_password`
  - `full_name`
  - `role` (enum: admin, manager, cashier, viewer)
  - `is_active`
  - `is_superuser`
  - `salary`
  - `created_at`
  - `updated_at`

#### 2. categories
Categorias para organização de produtos.
- **Campos**:
  - `id` (PK)
  - `name` (único)
  - `description`
  - `color` (código hexadecimal)
  - `is_active`
  - `created_at`
  - `updated_at`

#### 3. products
Cadastro de produtos do sistema.
- **Campos**:
  - `id` (PK)
  - `codigo` (SKU, único)
  - `category_id` (FK para categories)
  - `name`
  - `description`
  - `cost_price`
  - `sale_price`
  - `current_stock`
  - `min_stock`
  - `is_active`
  - `created_at`
  - `updated_at`

#### 4. sales
Registro de vendas.
- **Campos**:
  - `id` (PK)
  - `sale_number` (único)
  - `status` (enum: concluída, cancelada, etc.)
  - `subtotal`
  - `tax_amount`
  - `discount_amount`
  - `total_amount`
  - `payment_method`
  - `payment_status`
  - `customer_id` (FK para customers)
  - `employee_id` (FK para employees)
  - `user_id` (FK para users)
  - `notes`
  - `is_delivery`
  - `delivery_address`
  - `created_at`
  - `updated_at`

#### 5. sale_items
Itens de cada venda.
- **Campos**:
  - `id` (PK)
  - `sale_id` (FK para sales)
  - `product_id` (FK para products)
  - `quantity`
  - `unit_price`
  - `discount_percent`
  - `total_price`
  - `created_at`
  - `updated_at`

#### 6. customers
Clientes do sistema.
- **Campos**:
  - `id` (PK)
  - `name`
  - `email`
  - `phone`
  - `address`
  - `cpf_cnpj` (documento)
  - `is_active`
  - `created_at`
  - `updated_at`

#### 7. employees
Funcionários da empresa.
- **Campos**:
  - `id` (PK)
  - `user_id` (FK para users, opcional)
  - `name`
  - `email`
  - `phone`
  - `address`
  - `cpf`
  - `role`
  - `hire_date`
  - `is_active`
  - `created_at`
  - `updated_at`

#### 8. inventory
Movimentações de estoque.
- **Campos**:
  - `id` (PK)
  - `product_id` (FK para products)
  - `movement_type` (entrada/saída)
  - `quantity`
  - `notes`
  - `user_id` (FK para users)
  - `created_at`
  - `updated_at`

## Relacionamentos

- Um `User` pode ter múltiplas `Sales`
- Uma `Sale` tem múltiplos `SaleItem`s
- Um `Product` pertence a uma `Category`
- Um `SaleItem` está associado a um `Product`
- Um `Customer` pode ter múltiplas `Sales`
- Um `Employee` pode estar associado a múltiplas `Sales`
- Um `Product` pode ter múltiplas entradas em `Inventory`

## Endpoints da API

### Autenticação
- `POST /auth/login` - Realiza login e retorna token JWT
- `GET /auth/me` - Retorna informações do usuário logado

### Produtos
- `GET /products` - Lista todos os produtos
- `POST /products` - Cria um novo produto
- `GET /products/{id}` - Obtém detalhes de um produto
- `PUT /products/{id}` - Atualiza um produto
- `DELETE /products/{id}` - Remove um produto

### Vendas
- `GET /sales` - Lista todas as vendas
- `POST /sales` - Cria uma nova venda
- `GET /sales/{id}` - Obtém detalhes de uma venda
- `PUT /sales/{id}` - Atualiza uma venda
- `DELETE /sales/{id}` - Cancela uma venda

### Clientes
- `GET /customers` - Lista todos os clientes
- `POST /customers` - Cria um novo cliente
- `GET /customers/{id}` - Obtém detalhes de um cliente
- `PUT /customers/{id}` - Atualiza um cliente
- `DELETE /customers/{id}` - Remove um cliente

## Variáveis de Ambiente

O sistema utiliza as seguintes variáveis de ambiente (definidas no arquivo `.env`):

```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas
```

## Executando o Projeto

1. Clone o repositório
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente virtual:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Configure as variáveis de ambiente no arquivo `.env`
6. Execute as migrações: `alembic upgrade head`
7. Inicie o servidor: `uvicorn app.main:app --reload`

O servidor estará disponível em `http://localhost:8000`

## Documentação da API

A documentação interativa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
