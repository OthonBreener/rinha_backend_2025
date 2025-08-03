import asyncio
import redis.asyncio as redis
from httpx import AsyncClient
from app.depends import HTTP_LIMITS, HTTP_TIMEOUT


async def salvar_disponibilidade() -> None:
    """
    Verifica a disponibilidade dos processadores de pagamento.

    Utiliza cache Redis (TTL 5 s) para evitar sobrecarregar os processadores.
    Em caso de falha, alterna para o fallback ou retorna indisponível.
    """
    async with AsyncClient(
        limits=HTTP_LIMITS,
        timeout=HTTP_TIMEOUT,
    ) as cliente:
        response_default, response_fallback = await asyncio.gather(
            cliente.get(
                "http://payment-processor-default:8080/payments/service-health",
                timeout=5.0
            ),
            cliente.get(
                "http://payment-processor-fallback:8080/payments/service-health",
                timeout=5.0
            )
        )

    if response_default.status_code == 200 and response_fallback.status_code == 200:

        resposta_default = response_default.json()
        resposta_fallback = response_fallback.json()
        if resposta_default.get("failing"):
            processador_disponivel = 'fallback'

        elif resposta_default.get('minResponseTime') < 120:
            processador_disponivel = 'default'

        elif resposta_default.get('minResponseTime') > 120 and resposta_fallback.get('minResponseTime') > 120:
            if resposta_default.get('minResponseTime') < resposta_fallback.get('minResponseTime'):
                processador_disponivel = 'default'
            else:
                processador_disponivel = 'fallback'

        elif not resposta_fallback.get('failing'):
            processador_disponivel = 'fallback'
        else:
            processador_disponivel = 'default'

    else:
        # Se nenhum dos processadores responder, processa com o default
        processador_disponivel = 'default'

    redis_cliente = await redis.from_url(
        "redis://redis:6379", encoding="utf-8", decode_responses=True
    )

    async with redis_cliente.pipeline(transaction=True) as pipe:
        await (
            pipe.set("processador_disponivel", processador_disponivel, ex=5).execute()
        )


async def executar_cache() -> None:
    while True:
        try:
            await salvar_disponibilidade()

            await asyncio.sleep(5)
        except:
            await asyncio.sleep(0.01)