from fastapi import Depends, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from http import HTTPStatus

from sqlalchemy.sql.expression import and_

from app.depends import get_async_session
from app.schemas import PagamentoRequest
from app.orm import Pagamento
from app.worker import enviar_pagamento_para_fila


router = APIRouter()

SUCCESS_MESSAGE = "Pagamento processado com sucesso!"


@router.post("/payments")
async def process_payment(
    pagamento: PagamentoRequest,
):
    """
    Processa um pagamento tentando primeiro o processador default.
    Em caso de falha, tenta o fallback uma única vez.
    """

    await enviar_pagamento_para_fila(pagamento.model_dump(by_alias=True))

    return {"message": SUCCESS_MESSAGE}, HTTPStatus.OK


@router.get('/payments-summary')
async def payments_summary(
    from_: str = Query(alias="from"),
    to: str = Query(alias="to"),
    session: AsyncSession = Depends(get_async_session),
):
    # Converte as strings para datetime
    inicio = datetime.fromisoformat(from_.replace('Z', '+00:00'))
    fim = datetime.fromisoformat(to.replace('Z', '+00:00'))

    # Busca pagamentos default no período
    dados_default = await session.execute(
        select(Pagamento)
        .where(
            and_(
                Pagamento.requested_at >= inicio,
                Pagamento.requested_at <= fim,
                Pagamento.processor_used == "default",
            ),
        )
    )

    # Busca pagamentos fallback no período
    dados_fallback = await session.execute(
        select(Pagamento)
        .where(
            and_(
                Pagamento.requested_at >= inicio,
                Pagamento.requested_at <= fim,
                Pagamento.processor_used == "fallback",
            ),
        )
    )

    dados_default = dados_default.scalars().all()
    dados_fallback = dados_fallback.scalars().all()

    return {
        'default': {
            'totalRequests': len(dados_default),
            'totalAmount': sum(payment.amount for payment in dados_default),
        },
        'fallback': {
            'totalRequests': len(dados_fallback),
            'totalAmount': sum(payment.amount for payment in dados_fallback),
        }
    }
