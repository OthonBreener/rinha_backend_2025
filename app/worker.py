"""
Redis P2P para processamento de pagamentos em background.
"""
import json
import redis.asyncio as redis
from datetime import datetime, timezone

from app.orm import salvar_pagamento
from app.processar_pagamentos import enviar_pagamentos


# Redis connection pool for the worker
redis_pool = redis.ConnectionPool.from_url("redis://redis:6379", decode_responses=True)


def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)


async def enviar_pagamento_para_fila(payment: dict[str, str | float]) -> None:
    """
    Envia um pagamento para a fila de processamento no Redis.
    """
    redis_client = get_redis()
    await redis_client.rpush('pagamentos', json.dumps(payment))


async def worker() -> None:
    """Worker que processa pagamentos da fila do Redis."""
    redis_client = get_redis()

    try:
        while True:
            resultado = await redis_client.blpop("pagamentos", timeout=0)
            if resultado:
                _, payment = resultado

                processador_escolhido = await redis_client.get("processador_disponivel")
                if not processador_escolhido:
                    processador_escolhido = "default"

                payment = json.loads(payment)

                requested_at = datetime.now(timezone.utc)

                enviado = await enviar_pagamentos(
                    processador_escolhido=processador_escolhido,
                    pagamento={
                        'requestedAt': requested_at.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                        'correlationId': str(payment['correlationId']),
                        'amount': float(payment['amount']),
                    },
                )

                if enviado:
                    await salvar_pagamento(
                        {
                            'processor_used': processador_escolhido,
                            'requested_at': requested_at,
                            'correlation_id': payment['correlationId'],
                            'amount': payment['amount'],
                        }
                    )
    finally:
        await redis_client.close()
