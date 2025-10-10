# 🔪 Nego Maq API

API REST desenvolvida em Flask para uma loja online de facas e artigos de churrasco. O sistema oferece funcionalidades completas para e-commerce, incluindo catálogo de produtos, gerenciamento de pedidos, autenticação de usuários e área administrativa.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Executar](#-como-executar)
- [Autenticação](#-autenticação)

## ✨ Funcionalidades

### Público

- 🛍️ Visualização de catálogo de produtos
- 🛒 Gerenciamento de pedidos
- 👤 Cadastro e autenticação de usuários
- 📍 Gerenciamento de endereços de entrega
- 📦 Cálculo de frete (integração Melhor Envio)
- 📅 Visualização de eventos

### Administrativo

- 🔐 Autenticação JWT para administradores
- ➕ Cadastro, edição e remoção de produtos
- 📊 Gerenciamento de pedidos
- 📍 Gerenciamento de endereços
- ☁️ Upload de imagens (Cloudinary)

## 🛠 Tecnologias

- **Python** 3.10+
- **Flask** - Framework web
- **Flask-SQLAlchemy** - ORM para banco de dados
- **MySQL** 8.0 - Banco de dados relacional
- **PyMySQL** - Driver MySQL
- **Flask-CORS** - Gerenciamento de CORS
- **PyJWT** - Autenticação via tokens JWT
- **Werkzeug** - Hash de senhas
- **Cloudinary** - Armazenamento de imagens
- **Gunicorn** - Servidor WSGI para produção
- **Docker** - Containerização da aplicação

## 📁 Estrutura do Projeto

```
NEGO-MAQ-API/
├── routes/
│   ├── admin/
│   │   ├── admin.py              # Rotas administrativas gerais
│   │   ├── pedidos_admin.py      # Gerenciamento de pedidos (admin)
│   │   └── enderecos_admin.py    # Gerenciamento de endereços (admin)
│   └── public/
│       ├── public.py             # Rotas públicas gerais
│       ├── auth.py               # Autenticação e registro
│       ├── pedidos_public.py     # Pedidos (usuários)
│       ├── enderecos_public.py   # Endereços (usuários)
│       ├── eventos.py            # Eventos da loja
│       └── melhor_envio.py       # Integração para cálculo de frete
├── models/                       # Modelos do banco de dados
├── services/                     # Lógica de negócio
│   ├── admin/
│   └── public/
├── utils/
│   ├── middlewares/              # Middlewares (autenticação, etc)
│   ├── formatters.py             # Formatadores de dados
│   └── jwt_utils.py              # Utilitários JWT
├── seeders/
│   └── seed.py                   # Dados iniciais para desenvolvimento
├── migrations/                   # Migrações do banco
├── enums/                        # Enumeradores
├── database/                     # Configuração do banco
├── app.py                        # Arquivo principal da aplicação
├── docker-compose.yml            # Configuração Docker
├── Dockerfile                    # Imagem Docker
├── requirements.txt              # Dependências Python
├── .env.example                  # Exemplo de variáveis de ambiente
└── README.md
```

## 📦 Pré-requisitos

- Python 3.10 ou superior
- Docker e Docker Compose (recomendado)
- MySQL 8.0 (se não usar Docker)
- Conta Cloudinary (para upload de imagens)
- Token API Melhor Envio (para cálculo de frete)

## 🚀 Instalação

### Opção 1: Com Docker (Recomendado)

1. **Clone o repositório**

```bash
git clone https://github.com/Lucas-Blanger/nego-maq-api.git
cd nego-maq-api
```

2. **Configure as variáveis de ambiente**

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Suba os containers**

```bash
docker-compose up --build
```

A API estará disponível em `http://localhost:5000`

### Opção 2: Instalação Local

1. **Clone o repositório**

```bash
git clone https://github.com/Lucas-Blanger/nego-maq-api.git
cd nego-maq-api
```

2. **Crie um ambiente virtual**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Inicie o MySQL** e crie o banco de dados (ou deixe a aplicação criar automaticamente)

6. **Execute os seeders** (opcional, apenas para desenvolvimento)

```bash
python -m seeders.seed
```

7. **Rode a aplicação**

```bash
python app.py
```

## ⚙ Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Database
DATABASE_USER=adminuser
DATABASE_PASSWORD=adminpass
DATABASE_HOST=localhost  # Use 'db' se estiver usando Docker
DATABASE_NAME=nego_maq

# Flask
SECRET_KEY=sua_chave_secreta_aqui
FLASK_ENV=development

# Cloudinary
CLOUDE_NAME=seu_cloud_name
API_KEY=sua_api_key
API_SECRET=seu_api_secret

# Melhor Envio (opcional)
MELHOR_ENVIO_TOKEN=seu_token_aqui
```

## 🎯 Como Executar

### Desenvolvimento Local

```bash
python app.py
```

### Desenvolvimento com Docker

```bash
docker-compose up
```

### Produção

```bash
gunicorn -b 0.0.0.0:5000 app:app
```

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação.

### Como autenticar:

1. Faça login através do endpoint `/auth/login`
2. Receba o token JWT na resposta
3. Inclua o token no header das requisições protegidas:

```
Authorization: Bearer SEU_TOKEN_AQUI
```

### Exemplo de requisição autenticada:

```bash
curl -X GET http://localhost:5000/admin/pedidos \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🧪 Testando a API

Você pode testar a API usando:

- **Postman** ou **Insomnia**
- **cURL** via terminal

## 👥 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 📞 Contato

Para dúvidas ou sugestões, entre em contato através do repositório no GitHub.

---

Desenvolvido com ❤️ pela equipe Nego Maq
