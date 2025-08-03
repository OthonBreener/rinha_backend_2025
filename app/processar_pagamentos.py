from httpx import AsyncClient

from app.depends import HTTP_LIMITS, HTTP_TIMEOUT


async def enviar_pagamentos(
    processador_escolhido: str,
    pagamento: dict[str, str],
) -> bool:
    processors = {
        "default": "http://payment-processor-default:8080/payments",
        "fallback": "http://payment-processor-fallback:8080/payments",
    }

    async with AsyncClient(limits=HTTP_LIMITS, timeout=HTTP_TIMEOUT, http2=True) as client:
        resposta = await client.post(
            url=processors[processador_escolhido],
            json=pagamento,
            timeout=5.0,
            headers={"Content-Type": "application/json"},
        )
        if resposta.status_code == 200:
            return True

    return False
