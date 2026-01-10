# 🔪 Nego Maq API

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](README.pt-br.md)

Uma API REST completa para plataforma de e-commerce construída com Flask, apresentando gerenciamento completo de produtos, processamento de pedidos, autenticação JWT e funcionalidades de painel administrativo.

## 🎯 Visão Geral do Projeto

Este projeto demonstra habilidades de desenvolvimento backend full-stack através da implementação de um sistema de e-commerce real com:

- **Design de API RESTful** - Endpoints bem estruturados seguindo princípios REST
- **Autenticação & Autorização** - Segurança baseada em JWT com gerenciamento de roles
- **Design de Banco de Dados** - Banco de dados relacional normalizado com SQLAlchemy ORM
- **Integração Cloud** - Armazenamento de imagens com Cloudinary, API de cálculo de frete
- **Containerização** - Deploy com Docker para ambientes consistentes
- **Pronto para Produção** - Servidor WSGI Gunicorn, configuração de ambiente, tratamento de erros

## ✨ Funcionalidades Principais

### Funcionalidades de Usuário
- Catálogo de produtos com busca e filtragem
- Carrinho de compras e gerenciamento de pedidos
- Registro e autenticação de usuários
- Gerenciamento de endereços de entrega
- Cálculo de custo de frete (integração com API Melhor Envio)
- Listagem de eventos

### Funcionalidades Administrativas
- Rotas administrativas protegidas por JWT
- Operações CRUD completas para produtos
- Gerenciamento de pedidos e atualização de status
- Sistema de gerenciamento de endereços
- Upload de imagens na nuvem (Cloudinary)

## 🛠 Stack Tecnológica

**Framework Backend:**
- Python 3.10+
- Flask (Framework Web)
- Flask-SQLAlchemy (ORM)
- Flask-CORS (Compartilhamento de Recursos entre Origens)

**Banco de Dados:**
- MySQL 8.0
- PyMySQL (Driver MySQL)

**Segurança:**
- PyJWT (JSON Web Tokens)
- Werkzeug (Hash de Senhas)

**Serviços Cloud:**
- Cloudinary (Armazenamento de Imagens)
- API Melhor Envio (Cálculo de Frete)

**DevOps:**
- Docker & Docker Compose
- Gunicorn (Servidor WSGI)

## 📁 Estrutura do Projeto

```
NEGO-MAQ-API/
├── routes/
│   ├── admin/              # Rotas administrativas protegidas
│   └── public/             # Endpoints públicos da API
├── models/                 # Modelos de banco de dados (SQLAlchemy)
├── services/               # Camada de lógica de negócio
├── utils/
│   ├── middlewares/        # Autenticação & autorização
│   └── jwt_utils.py        # Gerenciamento de tokens JWT
├── database/               # Configuração do banco de dados
├── migrations/             # Migrações de banco de dados
├── seeders/                # Dados de seed para desenvolvimento
├── app.py                  # Ponto de entrada da aplicação
├── docker-compose.yml      # Configuração Docker
└── requirements.txt        # Dependências Python
```

## 🔐 Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação.

**Para autenticar:**
1. Faça login através do endpoint `/auth/login`
2. Inclua o token nos headers das requisições:
```
Authorization: Bearer SEU_TOKEN_JWT
```

**Exemplo de requisição autenticada:**
```bash
curl -X GET http://localhost:5000/admin/pedidos \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🏗️ Destaques da Arquitetura

- **Arquitetura em Camadas** - Separação de rotas, serviços e modelos
- **Padrão Middleware** - Autenticação e validação reutilizáveis
- **Padrão ORM** - Abstração de banco de dados com SQLAlchemy
- **Design RESTful** - Métodos HTTP e códigos de status padrão
- **Configuração de Ambiente** - Metodologia 12-factor app
- **Containerização** - Deploy consistente entre ambientes

## 📚 O Que Aprendi

Este projeto me ajudou a desenvolver habilidades em:
- Projetar e implementar APIs RESTful
- Implementar autenticação segura com JWT
- Modelagem de banco de dados e uso de ORM
- Integrar APIs de terceiros
- Containerizar aplicações com Docker
- Escrever código Python pronto para produção
- Gerenciar configurações de ambiente

Lucas Blanger
- LinkedIn: [lucas-blanger-4668a2210](https://www.linkedin.com/in/lucas-blanger-4668a2210/)
- GitHub: [@Lucas-Blanger](https://github.com/Lucas-Blanger)
- Portfolio: [lucas-blanger.vercel.app](https://lucas-blanger.vercel.app)

---

⭐ Se você achou este projeto interessante, considere dar uma estrela!
