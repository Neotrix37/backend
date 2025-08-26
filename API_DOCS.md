# Documentação da API - Sistema PDV

Esta documentação descreve como interagir com a API do Sistema PDV para gerenciamento de produtos, categorias e outras funcionalidades.

## Índice
- [Autenticação](#autenticação)
- [Produtos](#produtos)
- [Categorias](#categorias)
- [Vendas](#vendas)
- [Clientes](#clientes)
- [Funcionários](#funcionários)
- [Usuários](#usuários)
- [Tratamento de Erros](#tratamento-de-erros)
- [Exemplo de Uso](#exemplo-de-uso)

## Autenticação

### Registrar Usuário
```http
POST /api/v1/auth/register
```
**Corpo da requisição:**
```json
{
  "username": "novousuario",
  "email": "usuario@exemplo.com",
  "password": "senhasegura123",
  "full_name": "Nome Completo"
}
```

### Login
```http
POST /api/v1/auth/login
```
**Corpo da requisição:**
```json
{
  "username": "usuario",
  "password": "senha123"
}
```

### Obter Perfil do Usuário
```http
GET /api/v1/auth/me
```
**Cabeçalho de Autorização:**
```
Authorization: Bearer seu_token_jwt
```

## Produtos

### Listar Produtos
```http
GET /api/v1/products/
```
**Parâmetros de consulta:**
- `skip` (opcional): Número de itens para pular
- `limit` (opcional): Limite de itens por página
- `search` (opcional): Termo de busca
- `category_id` (opcional): Filtrar por categoria

### Criar Produto
```http
POST /api/v1/products/
```
**Corpo da requisição:**
```json
{
  "name": "Novo Produto",
  "description": "Descrição do produto",
  "sku": "PROD001",
  "cost_price": 10.50,
  "sale_price": 19.90,
  "current_stock": 100,
  "min_stock": 10,
  "category_id": 1,
  "venda_por_peso": false
}
```

### Obter Produto por ID
```http
GET /api/v1/products/{product_id}
```

### Atualizar Produto
```http
PUT /api/v1/products/{product_id}
```
**Corpo da requisição:**
```json
{
  "name": "Nome Atualizado",
  "description": "Descrição atualizada",
  "sku": "NOVOSKU123"
}
```

### Deletar Produto
```http
DELETE /api/v1/products/{product_id}
```

### Deletar Todos os Produtos
```http
DELETE /api/v1/products/delete-all
```

### Obter Estoque do Produto
```http
GET /api/v1/products/{product_id}/stock
```

## Categorias

### Listar Categorias
```http
GET /api/v1/categories/
```

### Criar Categoria
```http
POST /api/v1/categories/
```
**Corpo da requisição:**
```json
{
  "name": "Eletrônicos",
  "description": "Produtos eletrônicos"
}
```

### Obter Categoria por ID
```http
GET /api/v1/categories/{category_id}
```

### Atualizar Categoria
```http
PUT /api/v1/categories/{category_id}
```

### Deletar Categoria
```http
DELETE /api/v1/categories/{category_id}
```

## Vendas

### Listar Vendas
```http
GET /api/v1/sales/
```

### Criar Venda
```http
POST /api/v1/sales/
```

### Obter Venda por ID
```http
GET /api/v1/sales/{sale_id}
```

### Atualizar Venda
```http
PUT /api/v1/sales/{sale_id}
```

### Deletar Venda
```http
DELETE /api/v1/sales/{sale_id}
```

## Clientes

### Listar Clientes
```http
GET /api/v1/customers/
```

### Criar Cliente
```http
POST /api/v1/customers/
```

### Obter Cliente por ID
```http
GET /api/v1/customers/{customer_id}
```

### Atualizar Cliente
```http
PUT /api/v1/customers/{customer_id}
```

### Deletar Cliente
```http
DELETE /api/v1/customers/{customer_id}
```

## Funcionários

### Listar Funcionários
```http
GET /api/v1/employees/
```

### Criar Funcionário
```http
POST /api/v1/employees/
```

### Obter Funcionário por ID
```http
GET /api/v1/employees/{employee_id}
```

### Atualizar Funcionário
```http
PUT /api/v1/employees/{employee_id}
```

### Deletar Funcionário
```http
DELETE /api/v1/employees/{employee_id}
```

## Usuários

### Listar Usuários
```http
GET /api/v1/users/
```

### Criar Usuário
```http
POST /api/v1/users/
```

### Obter Usuário por ID
```http
GET /api/v1/users/{user_id}
```

### Atualizar Usuário
```http
PUT /api/v1/users/{user_id}
```

### Deletar Usuário
```http
DELETE /api/v1/users/{user_id}
```

## Tratamento de Erros

A API retorna os seguintes códigos de status:

| Código | Status | Descrição |
|--------|--------|------------|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 400 | Bad Request | Dados inválidos |
| 401 | Unauthorized | Autenticação necessária |
| 403 | Forbidden | Permissão negada |
| 404 | Not Found | Recurso não encontrado |
| 409 | Conflict | Conflito (ex: registro duplicado) |
| 500 | Internal Server Error | Erro no servidor |

## Exemplo de Uso

```javascript
// Exemplo de requisição para listar produtos
const response = await fetch('https://backend-production-f01c.up.railway.app/api/v1/products/', {
  headers: {
    'Authorization': 'Bearer seu_token_jwt',
    'Content-Type': 'application/json'
  }
});

if (response.ok) {
  const produtos = await response.json();
  console.log(produtos);
} else {
  console.error('Erro ao buscar produtos:', response.status);
}
