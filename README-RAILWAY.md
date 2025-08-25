# Deploy do Backend PDV no Railway

Este guia contém instruções para fazer o deploy do Backend PDV no Railway, incluindo a configuração do banco de dados PostgreSQL.

## Pré-requisitos

- Conta no [Railway](https://railway.app/)
- Git instalado na sua máquina
- Repositório do projeto no GitHub

## Configuração do Banco de Dados PostgreSQL no Railway

1. Faça login na sua conta do Railway
2. Clique em "New Project" e selecione "Database"
3. Escolha "PostgreSQL"
4. Após a criação do banco de dados, vá para a aba "Variables" e anote a variável `DATABASE_URL`

## Deploy da Aplicação

### Método 1: Deploy direto do GitHub

1. No Railway, clique em "New Project" e selecione "Deploy from GitHub repo"
2. Selecione o repositório do Backend PDV
3. O Railway detectará automaticamente o Dockerfile e usará ele para o build
4. Vá para a aba "Variables" e configure as seguintes variáveis de ambiente:
   - `SECRET_KEY`: Uma chave secreta forte para segurança
   - `ENVIRONMENT`: Defina como "production"
   - `DATABASE_URL`: Use o valor do banco de dados PostgreSQL criado anteriormente

### Método 2: Deploy usando a CLI do Railway

1. Instale a CLI do Railway:
   ```
   npm i -g @railway/cli
   ```

2. Faça login na sua conta Railway:
   ```
   railway login
   ```

3. Vincule o projeto ao Railway:
   ```
   railway link
   ```

4. Configure as variáveis de ambiente:
   ```
   railway variables set SECRET_KEY=sua-chave-secreta-aqui
   railway variables set ENVIRONMENT=production
   ```

5. Faça o deploy:
   ```
   railway up
   ```

## Verificação do Deploy

1. Após o deploy, o Railway fornecerá uma URL para acessar a aplicação
2. Acesse a URL fornecida para verificar se a aplicação está funcionando corretamente
3. Verifique o endpoint de saúde em `/health` para confirmar que a aplicação está saudável

## Monitoramento e Logs

1. No Railway, vá para a aba "Deployments" para ver o status dos deploys
2. Clique em um deploy específico para ver os logs
3. Use a aba "Metrics" para monitorar o uso de recursos

## Troubleshooting

- Se o deploy falhar, verifique os logs para identificar o problema
- Certifique-se de que todas as variáveis de ambiente estão configuradas corretamente
- Verifique se o banco de dados está acessível pela aplicação

## Notas Importantes

- O Railway fornecerá automaticamente a variável `PORT` para a aplicação
- O script `start.sh` executará as migrações do banco de dados automaticamente
- Certifique-se de atualizar a lista `ALLOWED_ORIGINS` no arquivo `.env.production` com os domínios do seu frontend