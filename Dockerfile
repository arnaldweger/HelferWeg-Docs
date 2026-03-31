# ── Stage 1: builder com UV ───────────────────────────────────────────────────
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml .

# Instalando dependências para Dash em vez de Streamlit
RUN uv venv .venv && \
    uv pip install --no-cache \
        "dash>=2.17.0" \
        "dash-bootstrap-components>=1.6.0" \
        "pandas>=2.2.0" \
        "gunicorn>=22.0.0"

# ── Stage 2: imagem final ─────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copia o ambiente virtual do builder
COPY --from=builder /app/.venv /app/.venv

# Copia o código do seu app (certifique-se de que o arquivo principal se chama app.py)
COPY app.py .
COPY assets/ assets/ 

# Cria diretórios necessários conforme seu projeto anterior [cite: 3]
RUN mkdir -p notas data

# Configurações de ambiente
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Porta padrão do Dash/Flask
EXPOSE 8050

# Comando para rodar com Gunicorn (melhor para produção no Raspberry Pi)
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"]