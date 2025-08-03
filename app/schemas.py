from pydantic import BaseModel, Field


class PagamentoRequest(BaseModel):
    correlation_id: str = Field(alias="correlationId")
    amount: float
