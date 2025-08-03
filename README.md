# Rinha de Backend 2025 - Payment Gateway

Backend para intermediar pagamentos com Payment Processor e Payment Fallback.

## Arquitetura

- Web Servers: 2 instâncias com load balancer Nginx
- Docker Compose com limites: 1,5 CPU total, 350MB memória total
- Banco PostgreSQL para persistência
- Redis para cache

## Endpoints

- `POST /payments`: intermedia pagamento
- `GET /payments-summary`: resumo de pagamentos processados
- `GET /payments/service-health`: health check com rate limit (1 req/5s)

## Tecnologias

- Python com FastAPI
- PostgreSQL
- Redis
- Docker Compose
- Nginx como load balancer
- Pydantic para validação
- SQLAlchemy para ORM

## Como executar

```bash
docker compose up --build
```

O serviço estará disponível em `http://localhost:9999`


