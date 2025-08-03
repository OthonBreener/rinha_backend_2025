# Dockerfile para aplicação FastAPI
FROM python:3.11-slim

# Configurações de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependências
COPY pyproject.toml poetry.lock README.md ./

# Copia código da aplicação
COPY app/ ./app/

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e .

# Cria usuário não-root
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

EXPOSE 9999

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9999"]
