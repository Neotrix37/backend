# 📋 Documentação do Sistema de Gestão Comercial

## 📊 Visão Geral

Este documento descreve a implementação completa do sistema de gestão comercial, incluindo todas as modificações realizadas, estrutura do banco de dados, e implementação de sincronização offline.

## 🗂️ Estrutura do Projeto

```
backend/
├── app/
│   ├── api/
│   │   └── api_v1/
│   │       └── endpoints/
│   │           ├── sales.py          # Endpoints de vendas
│   │           ├── reports.py        # Endpoints de relatórios
│   │           ├── sync.py          # Endpoints de sincronização
│   │           └── cart.py          # Endpoints do carrinho
│   ├── models/                      # Modelos do banco de dados
│   └── schemas/                     # Schemas Pydantic
├── alembic/                        # Migrações do banco
└── scripts/                        # Scripts utilitários
```

## 🗃️ Tabelas do Banco de Dados

### 1. **users**
- `id` (PK)
- `username` (unique)
- `email` (unique)
- `hashed_password`
- `full_name`
- `role` (admin, manager, cashier, viewer)
- `is_active`
- `is_superuser`
- `salary` (decimal)
- `created_at`, `updated_at`

### 2. **sales**
- `id` (PK)
- `sale_number` (unique)
- `status` (pending, completed, cancelled)
- `subtotal` (decimal)
- `total_amount` (decimal)
- `payment_method` (cash, card, pix)
- `customer_id` (FK customers)
- `user_id` (FK users) ✅ **NOVO**
- `notes` (text)
- `created_at`, `updated_at`
- `last_updated` (timestamp) ✅ **Sincronização**
- `synced` (boolean) ✅ **Sincronização**

### 3. **sale_items**
- `id` (PK)
- `sale_id` (FK sales)
- `product_id` (FK products)
- `quantity` (decimal)
- `unit_price` (decimal)
- `total_price` (decimal)
- `weight` (decimal) ✅ **Produtos por peso**
- `created_at`, `updated_at`

### 4. **products**
- `id` (PK)
- `name`
- `description`
- `price` (decimal)
- `cost_price` (decimal)
- `stock_quantity` (decimal)
- `min_stock` (decimal)
- `category_id` (FK categories)
- `barcode` (unique)
- `is_active`
- `created_at`, `updated_at`
- `last_updated` (timestamp) ✅ **Sincronização**
- `synced` (boolean) ✅ **Sincronização**

### 5. **categories**
- `id` (PK)
- `name`
- `description`
- `created_at`, `updated_at`

### 6. **customers**
- `id` (PK)
- `name`
- `email`
- `phone`
- `address`
- `created_at`, `updated_at`
- `last_updated` (timestamp) ✅ **Sincronização**
- `synced` (boolean) ✅ **Sincronização**

### 7. **employees**
- `id` (PK)
- `name`
- `position`
- `salary` (decimal)
- `hire_date`
- `is_active`
- `user_id` (FK users)
- `created_at`, `updated_at`
- `last_updated` (timestamp) ✅ **Sincronização**
- `synced` (boolean) ✅ **Sincronização**

### 8. **inventory**
- `id` (PK)
- `product_id` (FK products)
- `quantity` (decimal)
- `movement_type` (in, out, adjustment)
- `notes`
- `created_at`, `updated_at`

## 🔄 Implementações Realizadas

### 1. **Associação de Vendas ao Usuário** ✅
- Adicionado campo `user_id` na tabela `sales`
- Criado relacionamento `Sale.user`
- Implementado script de migração (`migrate_sales_users.py`)
- Atualizados todos os endpoints para incluir informações do usuário

### 2. **Correção de Erros** ✅
- Corrigido `'User' object has no attribute 'name'`
- Substituído `sale.user.name` por `sale.user.full_name` em:
  - `reports.py` (2 ocorrências)
  - `sales.py` (2 ocorrências)
  - `sync.py` (1 ocorrência)

### 3. **Endpoints Atualizados** ✅
- **Vendas** (`/api/v1/sales/`): Inclui `user_id` e `user_name`
- **Relatórios** (`/api/v1/reports/financial/`): Mostra "Vendas por Usuário"
- **Carrinho** (`/api/v1/cart/checkout`): Associa `user_id` automaticamente
- **Sincronização** (`/api/v1/sync/`): Inclui informações do usuário

## 📡 Implementação de Sincronização Offline

### Arquitetura Proposta

```
[Dispositivo Offline] ←→ [Banco Local] ←→ [Serviço de Sincronização] ←→ [Servidor]
```

### 1. **Estrutura de Dados para Sincronização**

Cada tabela sincronizável possui:
- `last_updated`: Timestamp da última modificação
- `synced`: Boolean indicando se foi sincronizado
- `device_id`: Identificador do dispositivo (para conflitos)

### 2. **Endpoints de Sincronização**

#### 🔁 Sincronização Download (GET)
```http
GET /api/v1/sync/{model}?last_sync=2024-01-01T00:00:00Z
```

Retorna apenas registros modificados desde a última sincronização.

#### 🔁 Sincronização Upload (POST)
```http
POST /api/v1/sync/{model}
Content-Type: application/json

{
  "device_id": "device-001",
  "data": [
    {
      "id": 1,
      "sale_number": "001",
      "user_id": 1,
      "last_updated": "2024-01-01T10:00:00Z",
      "synced": false
    }
  ]
}
```

### 3. **Fluxo de Sincronização**

#### 📥 Download Inicial
1. Cliente faz requisição GET para `/sync/sales?last_sync=null`
2. Servidor retorna todas as vendas
3. Cliente armazena localmente com `synced = true`

#### 🔄 Sincronização Periódica
1. Cliente verifica registros com `synced = false`
2. Envia batch para POST `/sync/sales`
3. Servidor processa e retorna confirmação
4. Cliente marca registros como `synced = true`

#### ⚡ Sincronização em Tempo Real
1. Quando online, enviar imediatamente
2. Quando offline, armazenar em fila local
3. Re-tentar quando conexão restaurada

### 4. **Resolução de Conflitos**

#### Estratégia "Last-Write-Wins"
```python
def resolve_conflict(local, remote):
    if local.last_updated > remote.last_updated:
        return local  # Versão local mais recente
    else:
        return remote  # Versão remota mais recente
```

#### Estratégia por Tipo de Dados
- **Vendas**: Last-Write-Wins
- **Produtos**: Merge automático (estoque pode ser somado)
- **Clientes**: Merge por email/telefone único

### 5. **Implementação no Cliente**

#### Service Worker para Sincronização
```javascript
// Exemplo de service worker para sincronização em background
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-sales') {
    event.waitUntil(syncSales());
  }
});

async function syncSales() {
  const offlineSales = await getOfflineSales();
  if (navigator.onLine && offlineSales.length > 0) {
    await api.post('/sync/sales', {
      device_id: getDeviceId(),
      data: offlineSales
    });
    await markAsSynced(offlineSales);
  }
}
```

#### Armazenamento Local
```javascript
// IndexedDB para armazenamento offline
const db = new Dexie('OfflineStore');

db.version(1).stores({
  sales: 'id, sale_number, user_id, last_updated, synced',
  products: 'id, name, price, last_updated, synced',
  customers: 'id, name, email, last_updated, synced'
});
```

### 6. **Monitoramento e Logs**

#### Métricas de Sincronização
- Tempo desde última sincronização
- Quantidade de registros pendentes
- Taxa de sucesso/falha
- Tamanho dos batches

#### Logs de Debug
```python
# No servidor
logger.info(f"Sincronização recebida: {len(data)} registros")
logger.info(f"Dispositivo: {device_id}")
logger.info(f"Conflitos resolvidos: {conflict_count}")
```

## 🚀 Como Testar a Sincronização

### 1. **Teste Offline Simulado**
```bash
# Desligar rede
npm install -g offline-server
offline-server --port 3000

# Testar funcionalidades offline
curl http://localhost:3000/api/v1/sales/
```

### 2. **Teste de Conflitos**
```python
# Simular conflito modificando mesmo registro em dois dispositivos
python scripts/simulate_conflict.py
```

### 3. **Teste de Performance**
```bash
# Testar com grande volume de dados
python scripts/load_test_sync.py --records 1000
```

## 📈 Próximos Passos

### 🎯 Melhorias Futuras
1. **Sincronização Bidirecional em Tempo Real** com WebSockets
2. **Compressão de Dados** para reduzir uso de banda
3. **Sincronização Delta** (apenas campos modificados)
4. **Dashboard de Monitoramento** de sincronização
5. **Políticas de Retenção** de dados offline

### 🔧 Manutenção
1. **Limpeza Automática** de registros sincronizados antigos
2. **Backup Automático** do banco local
3. **Atualização Schema** sem perda de dados

## 🆘 Troubleshooting

### Problemas Comuns

#### ❌ "User object has no attribute 'name'"
**Solução**: Usar `user.full_name` em vez de `user.name`

#### ❌ Sincronização não funciona offline
**Solução**: Verificar service worker e IndexedDB

#### ❌ Conflitos não resolvidos
**Solução**: Implementar estratégia de merge específica

### Logs de Debug
```bash
# Verificar logs do servidor
python main.py --log-level DEBUG

# Verificar status da sincronização
curl http://localhost:8000/api/v1/sync/status
```

---

## 📞 Suporte

Para issues relacionadas à sincronização, incluir:
- ID do dispositivo
- Timestamp do erro
- Logs do console
- Status da conexão

**Documentação atualizada em**: {{DATA_ATUAL}}
**Versão do Sistema**: 1.2.0