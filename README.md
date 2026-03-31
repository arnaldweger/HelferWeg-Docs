# 📘 HelferWeg Docs — Gestão de Notas Personalizada

O **HelferWeg Docs** é um sistema independente para gestão de documentação e notas, desenvolvido em **Python (Dash)** com interface moderna baseada no tema **Catppuccin**. O projeto é totalmente conteinerizado, garantindo que rode exatamente da mesma forma em qualquer máquina.

---

## 🚀 Como Rodar o Projeto (Windows)

Para rodar este app localmente, você não precisa instalar o Python manualmente. Usaremos o **Docker**, que cuidará de todas as dependências (Pandas, Dash, temas, etc.) de forma isolada.

### 1. Pré-requisitos
* **Docker Desktop**: O "motor" que rodará o aplicativo.
  * [Baixe aqui o Docker Desktop](https://www.docker.com/products/docker-desktop/)
  * *Nota: Durante a instalação, aceite a ativação do WSL 2 (Windows Subsystem for Linux) se solicitado.*
* **Git** (Opcional): Para clonar o repositório.
  * [Baixe aqui o Git](https://git-scm.com/)

### 2. Instalação e Execução

1. **Obtenha os arquivos:**
   Abra o Terminal (PowerShell ou Prompt de Comando) e clone o repositório:
   ```bash
   git clone [https://github.com/arnaldweger/helferweg-docs.git](https://github.com/seu-usuario/helferweg-docs.git)
   cd helferweg-docs
   ```

   (Ou simplesmente baixe o ZIP do projeto e extraia em uma pasta).

---

2. Inicie o Docker Desktop:
Certifique-se de que o ícone do Docker está aparecendo na barra de tarefas (próximo ao relógio).

3. Suba o Container:
No terminal, dentro da pasta do projeto, execute:
```bash
docker compose up -d --build
```
Este comando irá baixar a imagem do Python 3.12, instalar as bibliotecas e configurar o servidor automaticamente.


3. Acessando o App
Após o término do comando acima, abra o seu navegador e acesse:
👉 http://localhost:8501

🛠️ Tecnologias Utilizadas

- Linguagem: Python 3.12 

- Framework Web: Dash & Dash Bootstrap Components

- Gerenciador de Pacotes: uv (Alta performance) 

- Servidor de Produção: Gunicorn 


Containerização: Docker 


📂 Estrutura de Pastas
/notas: Onde seus arquivos .md ficam salvos (sincronizados com o seu computador).

/assets: Imagens, logos e favicons do sistema.

app.py: O código principal do sistema Dash.