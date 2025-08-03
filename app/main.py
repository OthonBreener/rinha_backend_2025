import asyncio
import os

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.apis import router
from app.worker import worker
from app.orm import create_tables_async
from app.cache import executar_cache

import logging

logging.basicConfig(
    level=logging.INFO,  # ou DEBUG para mais detalhes
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria as tabelas
    if os.getenv('INSTANCE_NAME') == 'app1':
        await create_tables_async()

    # coloca o cache pra rodar

    task_1 = asyncio.create_task(executar_cache())
    task_2 = asyncio.create_task(worker())

    yield

    # cancela as tarefas quando a aplicação for encerrada
    task_1.cancel()
    task_2.cancel()

    tasks = [task_1, task_2]

    await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(
    title="Payment Intermediary Backend",
    lifespan=lifespan
)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9999)