# Docker

# 🐳 Guia Completo
> Referência consolidada para criação e gerenciamento de aplicações Docker

## 1. Conceitos Fundamentais

```
Docker é uma plataforma para construir, rodar e transferir aplicações
em ambientes isolados chamados containers.

IMAGEM (Image)
  └── É o "molde" da aplicação. Contém:
        - Pedaço do sistema operacional (OS)
        - Bibliotecas e dependências
        - Arquivos da aplicação
        - Variáveis de ambiente

CONTAINER
  └── É a "instância rodando" criada a partir de uma imagem.
        - Funciona como uma VM isolada
        - Pode ser iniciado e parado
        - Múltiplos containers podem rodar a mesma imagem
```

## 2. Dockerfile — Construindo Imagens

> O `Dockerfile` é o arquivo de instruções para criar sua imagem.
> Cada linha é uma camada da imagem.

```bash
# ─────────────────────────────────────────────────────────────────
# FROM — Define a imagem base (sistema operacional + runtime)
# Exemplos: node:12-alpine | python:3.11-slim | ubuntu | alpine
# Alpine = Linux bem leve, ideal para Docker
# ─────────────────────────────────────────────────────────────────
FROM node:12-alpine

# ─────────────────────────────────────────────────────────────────
# WORKDIR — Define o diretório de trabalho dentro do container
# Todos os comandos seguintes rodam a partir daqui
# ─────────────────────────────────────────────────────────────────
WORKDIR /app

# ─────────────────────────────────────────────────────────────────
# RUN — Executa comandos durante o BUILD da imagem
# Use para instalar pacotes e dependências do sistema
# --no-cache evita guardar cache desnecessário (imagem menor)
# ─────────────────────────────────────────────────────────────────
RUN apk add --no-cache python3 make g++

# ─────────────────────────────────────────────────────────────────
# COPY — Copia arquivos do seu computador para dentro da imagem
# Sintaxe: COPY <origem_local> <destino_container>
# Copiar package.json antes do código = cache mais eficiente
# ─────────────────────────────────────────────────────────────────
COPY package.json yarn.lock ./

# Instala dependências (roda durante o build)
RUN yarn install --frozen-lockfile

# Copia todo o restante do código para dentro da imagem
COPY . .

# ─────────────────────────────────────────────────────────────────
# ADD — Alternativa ao COPY com superpoderes:
#   - Pode baixar arquivos de URLs
#   - Descompacta .zip e .tar automaticamente
# Use ADD apenas quando precisar dessas funcionalidades extras
# ─────────────────────────────────────────────────────────────────
# ADD https://exemplo.com/arquivo.json .
# ADD meu_arquivo.zip .

# ─────────────────────────────────────────────────────────────────
# ENV — Define variáveis de ambiente disponíveis no container
# Útil para URLs de API, configurações, etc.
# ─────────────────────────────────────────────────────────────────
ENV API_URL=https://api.meusite.com

# ─────────────────────────────────────────────────────────────────
# EXPOSE — Documenta qual porta o container usa internamente
# ⚠️ Isso NÃO abre a porta automaticamente — só documenta
# Para abrir a porta use -p no docker run
# ─────────────────────────────────────────────────────────────────
EXPOSE 3000

# ─────────────────────────────────────────────────────────────────
# USER — Por segurança, nunca rode como root em produção
# Criamos um grupo e usuário dedicado para a aplicação
# ─────────────────────────────────────────────────────────────────
RUN addgroup dev && adduser -S -G dev arnald
USER arnald

# ─────────────────────────────────────────────────────────────────
# CMD — Comando executado quando o container INICIA
# Formato: ["executável", "argumento1", "argumento2"]
# Só pode haver um CMD por Dockerfile
# ─────────────────────────────────────────────────────────────────
CMD ["node", "src/index.js"]
```

## 3. Comandos de Imagens

```bash
# ─────────────────────────────────────────────────────────────────
# Construir uma imagem a partir do Dockerfile
# -t = tag (nome da imagem)
# . = usa o Dockerfile da pasta atual
# ─────────────────────────────────────────────────────────────────
docker build -t nome-da-imagem .

# Construir com versão específica (boa prática para produção)
docker build -t app:v1.0.0 .

# ─────────────────────────────────────────────────────────────────
# Listar todas as imagens locais
# ─────────────────────────────────────────────────────────────────
docker images

# ─────────────────────────────────────────────────────────────────
# Renomear/criar uma tag para uma imagem existente
# ─────────────────────────────────────────────────────────────────
docker image tag app:latest app:v1.0.0

# ─────────────────────────────────────────────────────────────────
# Remover uma imagem (libera espaço em disco)
# ─────────────────────────────────────────────────────────────────
docker rmi nome-da-imagem
docker rmi -f nome-da-imagem   # -f = força remoção mesmo em uso

# ─────────────────────────────────────────────────────────────────
# Baixar uma imagem do Docker Hub sem rodar
# ─────────────────────────────────────────────────────────────────
docker pull ubuntu

# ─────────────────────────────────────────────────────────────────
# Exportar imagem para arquivo .tar (compartilhar sem Docker Hub)
# ─────────────────────────────────────────────────────────────────
docker image save -o minha_imagem.tar app:v1.0.0

# Importar imagem de um arquivo .tar
docker image load -i minha_imagem.tar
```

## 4. Comandos de Containers

```bash
# ─────────────────────────────────────────────────────────────────
# Rodar um container a partir de uma imagem
# ─────────────────────────────────────────────────────────────────

# Forma básica (ocupa o terminal)
docker run app:v2

# -d = detached (roda em segundo plano, libera o terminal)
docker run -d app:v2

# --name = dá um nome amigável ao container (fácil de referenciar)
docker run -d --name meu-container app:v2

# -p = mapeamento de portas: porta_do_host:porta_do_container
# Exemplo: acesse localhost:80 e ele redireciona para porta 3000 do container
docker run -d -p 80:3000 --name meu-container app:v2

# -it = modo interativo (entra no terminal do container)
docker run -it ubuntu

# ─────────────────────────────────────────────────────────────────
# Ver containers em execução
# ─────────────────────────────────────────────────────────────────
docker ps

# Ver TODOS os containers (inclusive os parados)
docker ps -a

# ─────────────────────────────────────────────────────────────────
# Parar e iniciar containers
# ─────────────────────────────────────────────────────────────────
docker stop meu-container    # Para o container graciosamente
docker start meu-container   # Inicia um container parado

# ─────────────────────────────────────────────────────────────────
# Remover um container
# ─────────────────────────────────────────────────────────────────
docker rm meu-container          # Remove container parado
docker rm -f meu-container       # -f = força remoção mesmo rodando

# ─────────────────────────────────────────────────────────────────
# Ver logs do container (fundamental para debugar erros)
# ─────────────────────────────────────────────────────────────────
docker logs meu-container
docker logs -f meu-container     # -f = segue os logs em tempo real
docker logs -n 50 meu-container  # -n = últimas N linhas
docker logs -t meu-container     # -t = mostra timestamp

# ─────────────────────────────────────────────────────────────────
# Executar comandos dentro de um container que está rodando
# ─────────────────────────────────────────────────────────────────
docker exec meu-container ls              # Lista arquivos
docker exec -it meu-container sh          # Entra no shell (sh)
docker exec -it meu-container bash        # Entra no shell (bash)
docker exec -it -u root meu-container sh  # Entra como root

# ─────────────────────────────────────────────────────────────────
# Copiar arquivos entre host e container
# ─────────────────────────────────────────────────────────────────
# Do container para o seu computador (. = pasta atual)
docker cp meu-container:/app/arquivo.txt .

# Do seu computador para dentro do container
docker cp arquivo.txt meu-container:/app/
```

## 5. Volumes e Persistência

> Quando um container é removido, os dados somem.
> Volumes são a solução para persistir dados.

```bash
# ─────────────────────────────────────────────────────────────────
# Criar um volume nomeado
# ─────────────────────────────────────────────────────────────────
docker volume create meus-dados

# Ver detalhes do volume (caminho físico no host, etc.)
docker volume inspect meus-dados

# ─────────────────────────────────────────────────────────────────
# Usar o volume ao rodar o container
# -v nome_do_volume:caminho_dentro_do_container
# ─────────────────────────────────────────────────────────────────
docker run -d -p 80:3000 --name meu-container -v meus-dados:/app/dados app:v2

# Verificar se o volume foi montado corretamente (olhar pasta dentro do container)
docker exec -it meu-container sh
# dentro do container: ls /app/dados

# ─────────────────────────────────────────────────────────────────
# Remover volumes sem uso (limpeza)
# ─────────────────────────────────────────────────────────────────
docker volume prune -f
```

## 6. Docker Compose

> Use o Docker Compose quando precisar rodar múltiplos containers
> que se comunicam entre si (ex: app + banco de dados).

```bash
# ─────────────────────────────────────────────────────────────────
# Verificar se o Docker Compose está instalado
# ─────────────────────────────────────────────────────────────────
docker compose version

# ─────────────────────────────────────────────────────────────────
# Comandos principais do Compose
# ─────────────────────────────────────────────────────────────────

# Constrói as imagens E sobe os containers (use na primeira vez)
docker compose up --build

# Sobe os containers em background (após já ter feito o build)
docker compose up -d

# Para e remove todos os containers do compose
docker compose down

# Ver status e mapeamento de portas dos containers
docker compose ps

# Ver logs de todos os containers juntos
docker compose logs

# Ver ajuda com todos os subcomandos disponíveis
docker compose --help
```

### Estrutura do arquivo `docker-compose.yml`

```yaml
# Versão da especificação do Compose
version: "3.8"

services:

  # ── Serviço 1: Frontend ─────────────────────────────────────────
  frontend:
    # Este serviço só sobe DEPOIS que o backend estiver pronto
    depends_on:
      - backend
    # Constrói a imagem a partir do Dockerfile na pasta ./frontend
    build: ./frontend
    # Mapeamento de portas: host:container
    ports:
      - "3000:3000"

  # ── Serviço 2: Backend ──────────────────────────────────────────
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    # Variáveis de ambiente para o container
    environment:
      - DATABASE_URL=sqlite:///mando.db
    # Monta um volume para persistir o banco de dados
    volumes:
      - ./backend/mando.db:/app/mando.db

  # ── Serviço 3: Banco de Dados (exemplo com Postgres) ────────────
  # database:
  #   image: postgres:15-alpine   # usa imagem pronta do Docker Hub
  #   environment:
  #     POSTGRES_PASSWORD: senha123
  #   volumes:
  #     - db-dados:/var/lib/postgresql/data

# Volumes nomeados (declaração obrigatória se usados nos services)
# volumes:
#   db-dados:
```

## 7. Rede Docker

> Cada container recebe um IP interno. O Docker cria uma rede
> virtual onde os containers se comunicam pelo nome do serviço.

```bash
# ─────────────────────────────────────────────────────────────────
# Subir os containers para verificar a rede
# ─────────────────────────────────────────────────────────────────
docker compose up -d

# Ver os containers rodando e seus IDs
docker ps

# Entrar no shell de um container para inspecionar a rede
docker exec -it -u root <ID_DO_CONTAINER> sh

# Dentro do container, ver configuração de rede (Linux)
ifconfig
# Cada container terá um IP como: 172.18.0.4

# Testar comunicação entre containers pelo nome do serviço
ping frontend    # o Docker resolve o nome "frontend" para o IP correto
ping backend
```

## 8. Docker Hub — Publicar e Compartilhar

```bash
# ─────────────────────────────────────────────────────────────────
# 1. Ver as imagens locais para escolher qual publicar
# ─────────────────────────────────────────────────────────────────
docker images

# ─────────────────────────────────────────────────────────────────
# 2. Fazer login no Docker Hub (dockerhub.com)
# ─────────────────────────────────────────────────────────────────
docker login

# ─────────────────────────────────────────────────────────────────
# 3. Criar uma tag com seu usuário/repositório do Docker Hub
# Formato: seu_usuario/nome_do_repositorio:versao
# ─────────────────────────────────────────────────────────────────
docker image tag app:v1.0.0 arnaldweger/app:v1.0.0

# ─────────────────────────────────────────────────────────────────
# 4. Enviar a imagem para o Docker Hub
# ─────────────────────────────────────────────────────────────────
docker push arnaldweger/app:v1.0.0
```

## 9. Limpeza e Manutenção

```bash
# ─────────────────────────────────────────────────────────────────
# Remover imagem específica
# ─────────────────────────────────────────────────────────────────
docker image rm nome-da-imagem

# ─────────────────────────────────────────────────────────────────
# Remover container específico
# ─────────────────────────────────────────────────────────────────
docker container rm nome-do-container

# ─────────────────────────────────────────────────────────────────
# Limpeza geral: remove containers parados, redes e imagens sem uso
# ⚠️ Não afeta containers rodando nem CasaOS/outros apps
# ─────────────────────────────────────────────────────────────────
docker system prune -f

# Remover volumes sem uso (opcional, libera mais espaço)
docker volume prune -f

# ─────────────────────────────────────────────────────────────────
# Sequência completa de limpeza de um projeto específico
# ─────────────────────────────────────────────────────────────────

# 1. Para o container
docker stop meu-container

# 2. Remove o container
docker rm meu-container

# 3. Confirma que foi removido
docker ps -a

# 4. Lista imagens
docker images

# 5. Remove a imagem
docker rmi minha-imagem:tag

# 6. Limpeza geral
docker system prune -f
```

## 10. Linux Básico dentro do Container

```bash
# ─────────────────────────────────────────────────────────────────
# Pacotes e atualizações (Ubuntu/Debian)
# ─────────────────────────────────────────────────────────────────
apt list            # lista pacotes instalados
apt update          # atualiza lista de pacotes
apt install nano    # instala o editor de texto nano

# ─────────────────────────────────────────────────────────────────
# Navegação e arquivos
# ─────────────────────────────────────────────────────────────────
ls                  # lista arquivos e pastas
mkdir pasta         # cria uma pasta
mv antigo novo      # renomeia arquivo ou pasta
touch arquivo.txt   # cria um arquivo vazio
rm arquivo.txt      # remove um arquivo
rm -r pasta/        # remove uma pasta e todo seu conteúdo
cat arquivo.txt     # exibe conteúdo do arquivo
more arquivo.txt    # exibe por partes (útil para arquivos grandes)

# ─────────────────────────────────────────────────────────────────
# Busca de conteúdo
# ─────────────────────────────────────────────────────────────────
grep "texto" arquivo.txt             # busca texto dentro de arquivo
grep -i "texto" arquivo.txt          # -i = ignora maiúsculas/minúsculas
grep -r "texto" .                    # busca recursiva na pasta atual

# ─────────────────────────────────────────────────────────────────
# Busca de arquivos
# ─────────────────────────────────────────────────────────────────
find /etc/                           # lista tudo dentro de /etc
find -type f -name "docker.txt"      # busca arquivo por nome exato
find -type f -name "ar*"             # busca arquivos que começam com "ar"
find -type d                         # busca somente diretórios

# ─────────────────────────────────────────────────────────────────
# Redirecionamento de saída
# ─────────────────────────────────────────────────────────────────
cat a.txt > b.txt                    # copia conteúdo de a para b
cat a.txt b.txt > completo.txt       # junta dois arquivos em um

# ─────────────────────────────────────────────────────────────────
# Processos
# ─────────────────────────────────────────────────────────────────
ps                  # lista processos ativos
kill 502            # mata o processo com ID 502

# ─────────────────────────────────────────────────────────────────
# Usuários e grupos (rodar múltiplos comandos)
# ─────────────────────────────────────────────────────────────────
mkdir pasta && cd pasta && echo "Funcionou"   # && = para se der erro
```

## 11. Exemplo Completo: Streamlit no ARM/Raspberry

### Estrutura do projeto

```
planejamento/
├── app.py                  ← aplicação Streamlit
├── requirements.txt        ← dependências Python
├── Dockerfile              ← instruções para build da imagem
├── docker-compose.yml      ← orquestração dos containers
└── dados/                  ← pasta de dados/imagens da aplicação
    ├── imagem1.png
    └── imagem2.png
```

### `app.py` — Regras de ouro do Streamlit

```python
import streamlit as st
import os

# ─────────────────────────────────────────────────────────────────
# ⚠️ REGRA DE OURO #1: set_page_config SEMPRE como primeiro comando
# Se colocado depois de qualquer st.* o app fica instável com proxy
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Planejamento Compras",
    page_icon="📊",
    layout="wide"
)

st.title("Planejamento de Compras")

# ─────────────────────────────────────────────────────────────────
# ⚠️ REGRA DE OURO #2: Evite unsafe_allow_html=True com proxy
# Use streamlit.components.v1 para HTML customizado
# ─────────────────────────────────────────────────────────────────
from streamlit.components.v1 import html
html("<h2 style='text-align:center; color:orange;'>Meu App</h2>", height=80)

# ─────────────────────────────────────────────────────────────────
# ⚠️ REGRA DE OURO #3: Use caminhos absolutos para imagens no Docker
# Caminhos relativos falham dentro do container
# ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
st.image(os.path.join(BASE_DIR, "dados", "imagem1.png"))
```

### `requirements.txt`

```
streamlit==1.37.1
pandas
numpy
plotly
```

### `Dockerfile` (compatível com ARM/Raspberry Pi)

```dockerfile
# Imagem base Python leve (slim = sem extras desnecessários)
FROM python:3.11-slim

# Define pasta de trabalho dentro do container
WORKDIR /app

# Copia e instala dependências primeiro (melhor uso de cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Documenta a porta usada pelo Streamlit
EXPOSE 8501

# Comando de inicialização: roda o app na porta 8501
# --server.address=0.0.0.0 = aceita conexões externas (obrigatório no Docker)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Comandos para rodar

```bash
# Constrói a imagem com nome e tag
docker build -t planejamento-streamlit .

# Roda o container:
# -d = em background
# -p 9000:8501 = acesse na porta 9000 do host, container usa 8501
# --name = nome amigável para o container
docker run -d -p 9000:8501 --name planejamento_streamlit planejamento-streamlit

# Acesse no navegador: http://IP_DO_RASPBERRY:9000

# ─────────────────────────────────────────────────────────────────
# Para rebuild (quando alterar o código):
# ─────────────────────────────────────────────────────────────────
docker stop planejamento_streamlit
docker rm planejamento_streamlit
docker build -t planejamento-streamlit .
docker run -d -p 9000:8501 --name planejamento_streamlit planejamento-streamlit
```

## 12. Boas Práticas

```
✅ SEMPRE faça:
   - Use imagens base leves: alpine, slim
   - Copie package.json/requirements.txt ANTES do código (cache do build)
   - Use --no-cache no pip/apk para imagens menores
   - Nomeie seus containers com --name (mais fácil de gerenciar)
   - Versione suas imagens: app:v1.0.0 (não só :latest em produção)
   - Use volumes para dados que precisam persistir
   - Teste local → depois Docker → depois proxy/cloudflare

❌ NUNCA faça:
   - Não rode como root em produção (use USER no Dockerfile)
   - Não coloque senhas e API keys direto no Dockerfile
     (use variáveis de ambiente ou arquivos .env)
   - Não ignore os logs quando algo der errado (docker logs)

🔒 SEQUÊNCIA RECOMENDADA PARA NOVO PROJETO:
   1. Faça o app rodar localmente
   2. Crie o Dockerfile
   3. docker build e docker run (teste básico)
   4. Adicione docker-compose.yml se tiver múltiplos serviços
   5. Só depois configure Nginx, proxy e Cloudflare
```

*Referência gerada a partir das anotações pessoais de estudo Docker.*
