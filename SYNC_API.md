# API de Sincronização

Este documento descreve os endpoints disponíveis para sincronização de dados entre o servidor e os clientes (PDV offline e frontend web).

## Visão Geral

A API de sincronização permite que clientes offline mantenham seus dados atualizados em relação ao servidor central. A sincronização é baseada em timestamps e usa um sistema de resolução de conflitos baseado em "o último a modificar vence".

## Autenticação

Todos os endpoints exigem autenticação via JWT. Inclua o token no cabeçalho das requisições:

```
Authorization: Bearer <seu_token_jwt>
```

## Tabelas Suportadas

- `products` - Produtos
- `categories` - Categorias
- `customers` - Clientes
- `sales` - Vendas
- `sale_items` - Itens de venda
- `employees` - Funcionários
- `inventory` - Estoque
- `users` - Usuários do sistema

## Tabelas Sincronizáveis

### Produtos

A sincronização de produtos inclui os seguintes campos:

- `id` (int): Identificador único do produto
- `codigo` (string): Código SKU do produto
- `nome` (string): Nome do produto
- `descricao` (string, opcional): Descrição detalhada
- `preco_compra` (decimal): Preço de custo
- `preco_venda` (decimal): Preço de venda
- `estoque` (int): Quantidade em estoque
- `estoque_minimo` (int): Estoque mínimo desejado
- `venda_por_peso` (boolean): Se o produto é vendido por peso
- `is_active` (boolean): Se o produto está ativo
- `category_id` (int, opcional): ID da categoria
- `created_at` (datetime): Data de criação
- `updated_at` (datetime): Última atualização

## Endpoints

### Obter Atualizações

Retorna os registros atualizados desde a última sincronização.

```
GET /api/v1/sync/{table_name}
```

#### Parâmetros de Consulta

- `last_sync` (obrigatório): Data e hora da última sincronização bem-sucedida no formato ISO 8601.

#### Exemplo de Resposta

```json
{
  "server_updated": [
    {
      "id": 1,
      "name": "Produto Atualizado",
      "price": 29.99,
      "last_updated": "2025-08-31T14:30:00Z",
      "synced": true
    }
  ],
  "synced_records": [],
  "conflicts": []
}
```

### Obter Atualizações de Produtos

Retorna os produtos atualizados desde a última sincronização.

```
GET /api/v1/sync/products
```

#### Parâmetros de Consulta

- `last_sync` (obrigatório): Data e hora da última sincronização bem-sucedida no formato ISO 8601.
- `include_inactive` (opcional, padrão: false): Incluir produtos inativos.

#### Exemplo de Resposta

```json
{
  "updated_products": [
    {
      "id": 1,
      "codigo": "PROD001",
      "nome": "Produto Atualizado",
      "preco_compra": 10.50,
      "preco_venda": 19.90,
      "estoque": 100,
      "updated_at": "2025-08-31T14:30:00Z"
    }
  ],
  "deleted_products": [23, 45, 67],
  "server_time": "2025-08-31T15:45:00Z"
}
```

### Sincronizar Dados

Envia dados do cliente para o servidor e retorna o resultado da sincronização.

```
POST /api/v1/sync/{table_name}
```

#### Parâmetros de Consulta

- `last_sync` (opcional): Data e hora da última sincronização para buscar atualizações do servidor.

#### Corpo da Requisição

```json
[
  {
    "id": 1,
    "name": "Produto Atualizado",
    "price": 29.99,
    "last_updated": "2025-08-31T14:30:00Z"
  }
]
```

#### Exemplo de Resposta

```json
{
  "synced_records": [
    {
      "id": 1,
      "name": "Produto Atualizado",
      "price": 29.99,
      "last_updated": "2025-08-31T14:30:00Z",
      "synced": true
    }
  ],
  "conflicts": [],
  "server_updated": [
    {
      "id": 2,
      "name": "Outro Produto",
      "price": 15.99,
      "last_updated": "2025-08-31T14:35:00Z",
      "synced": true
    }
  ]
}
```

### Enviar Atualizações de Produtos

Envia atualizações de produtos do cliente para o servidor.

```
POST /api/v1/sync/products
```

#### Exemplo de Requisição

```json
{
  "updated_products": [
    {
      "id": "local_123",
      "codigo": "PROD002",
      "nome": "Novo Produto",
      "preco_compra": 15.00,
      "preco_venda": 29.90,
      "estoque": 50,
      "client_updated_at": "2025-08-31T14:20:00Z"
    }
  ],
  "deleted_products": ["local_456"],
  "last_sync": "2025-08-31T14:00:00Z"
}
```

#### Resposta de Conflito

Em caso de conflito (mesmo registro modificado em ambos os lados), a API retornará:

```json
{
  "conflicts": [
    {
      "local_id": "local_123",
      "server_version": {
        "id": 2,
        "codigo": "PROD002",
        "nome": "Produto Modificado",
        "preco_venda": 25.90,
        "updated_at": "2025-08-31T14:25:00Z"
      },
      "local_version": {
        "id": "local_123",
        "codigo": "PROD002",
        "nome": "Novo Produto",
        "preco_venda": 29.90,
        "client_updated_at": "2025-08-31T14:20:00Z"
      }
    }
  ]
}
```

## Fluxo de Sincronização

1. **Primeira Sincronização**:
   - Cliente faz uma requisição GET para cada tabela sem o parâmetro `last_sync`
   - Servidor retorna todos os registros ativos

2. **Sincronizações Posteriores**:
   - Cliente envia seus registros modificados via POST
   - Servidor aplica as alterações e retorna confirmação
   - Servidor envia registros atualizados desde a última sincronização

3. **Resolução de Conflitos**:
   - Quando um registro é modificado tanto no cliente quanto no servidor, a versão mais recente (baseada em `last_updated`) prevalece
   - Conflitos são retornados na resposta para tratamento do cliente

## Estratégia de Sincronização

1. **Primeira Sincronização**:
   - Cliente faz uma requisição sem `last_sync`
   - Servidor retorna todos os registros ativos

2. **Sincronizações Incrementais**:
   - Cliente envia `last_sync` com a data da última sincronização
   - Servidor retorna apenas registros modificados desde então

3. **Resolução de Conflitos**:
   - O registro com o `updated_at` mais recente prevalece
   - Em caso de empate, o servidor decide
   - Registros excluídos são marcados como inativos em vez de removidos

## Boas Práticas

1. Sempre use a data/hora UTC para `last_updated`
2. Implemente retry com backoff exponencial em caso de falha na rede
3. Sincronize tabelas na ordem de dependência (ex: categorias antes de produtos)
4. Processe as atualizações do servidor antes de enviar as alterações locais
5. Mantenha um log de operações de sincronização para depuração

## Códigos de Resposta

- `200 OK`: Sincronização bem-sucedida
- `400 Bad Request`: Dados inválidos ou parâmetros ausentes
- `401 Unauthorized`: Token inválido ou ausente
- `404 Not Found`: Tabela não encontrada
- `500 Internal Server Error`: Erro no servidor durante a sincronização
