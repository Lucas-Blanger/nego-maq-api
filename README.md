# 🔪 API - Nego Maq

Esta é uma API simples desenvolvida com **Flask + MySQL**, voltada para uma loja de facas. Ela permite:

- Visualizar produtos
- Adicionar ao carrinho (frontend)
- Finalizar compra com redirecionamento para o WhatsApp
- Área administrativa com autenticação por token para cadastrar/remover produtos
- Login e cadastro de usuários (com ou sem admin)

---

## 🛠️ Tecnologias utilizadas

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- MySQL
- Werkzeug (hash de senha)
- Dotenv (.env para configurações)

---

## ⚙️ Como rodar o projeto

### 1. Clone o repositório


    git clone https://github.com/Lucas-Blanger/nego-maq-api.git
    cd nego-maq-api

### 2. Instale as dependências

pip install -r requirements.txt

### 3. Configure o config.py

### 4. Crie o banco de dados

Use o arquivo tables.sql incluído no projeto para criar as tabelas no MySQL:

-- No MySQL ou Workbench
source script.sql;

### 5. Rode a aplicação

    python app.py
