# 🔪 Nego Maq API

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](README.pt-br.md)

A comprehensive REST API for an e-commerce platform built with Flask, featuring complete product management, order processing, JWT authentication, and admin dashboard capabilities.

## 🎯 Project Overview

This project demonstrates full-stack backend development skills by implementing a real-world e-commerce system with:

- **RESTful API Design** - Well-structured endpoints following REST principles
- **Authentication & Authorization** - JWT-based security with role management
- **Database Design** - Normalized relational database with SQLAlchemy ORM
- **Cloud Integration** - Image storage with Cloudinary, shipping calculation API
- **Containerization** - Docker deployment for consistent environments
- **Production-Ready** - Gunicorn WSGI server, environment configuration, error handling

## ✨ Key Features

### User Features
- Product catalog with search and filtering
- Shopping cart and order management
- User registration and authentication
- Delivery address management
- Shipping cost calculation (Melhor Envio API integration)
- Event listings

### Admin Features
- JWT-protected administrative routes
- Full CRUD operations for products
- Order management and status updates
- Address management system
- Cloud-based image upload (Cloudinary)

## 🛠 Tech Stack

**Backend Framework:**
- Python 3.10+
- Flask (Web Framework)
- Flask-SQLAlchemy (ORM)
- Flask-CORS (Cross-Origin Resource Sharing)

**Database:**
- MySQL 8.0
- PyMySQL (MySQL Driver)

**Security:**
- PyJWT (JSON Web Tokens)
- Werkzeug (Password Hashing)

**Cloud Services:**
- Cloudinary (Image Storage)
- Melhor Envio API (Shipping Calculation)

**DevOps:**
- Docker & Docker Compose
- Gunicorn (WSGI Server)

## 📁 Project Structure

```
NEGO-MAQ-API/
├── routes/
│   ├── admin/              # Protected admin routes
│   └── public/             # Public API endpoints
├── models/                 # Database models (SQLAlchemy)
├── services/               # Business logic layer
├── utils/
│   ├── middlewares/        # Authentication & authorization
│   └── jwt_utils.py        # JWT token management
├── database/               # Database configuration
├── migrations/             # Database migrations
├── seeders/                # Development seed data
├── app.py                  # Application entry point
├── docker-compose.yml      # Docker configuration
└── requirements.txt        # Python dependencies
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

**To authenticate:**
1. Login via `/auth/login` endpoint
2. Include the token in request headers:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Example authenticated request:**
```bash
curl -X GET http://localhost:5000/admin/pedidos \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🏗️ Architecture Highlights

- **Layered Architecture** - Separation of routes, services, and models
- **Middleware Pattern** - Reusable authentication and validation
- **ORM Pattern** - Database abstraction with SQLAlchemy
- **RESTful Design** - Standard HTTP methods and status codes
- **Environment Configuration** - 12-factor app methodology
- **Containerization** - Consistent deployment across environments

## 📚 What I Learned

This project helped me develop skills in:
- Designing and implementing RESTful APIs
- Implementing secure authentication with JWT
- Database modeling and ORM usage
- Integrating third-party APIs
- Containerizing applications with Docker
- Writing production-ready Python code
- Managing environment configurations

## 📫 Contact

Lucas Blanger
- LinkedIn: [lucas-blanger-4668a2210](https://www.linkedin.com/in/lucas-blanger-4668a2210/)
- GitHub: [@Lucas-Blanger](https://github.com/Lucas-Blanger)
- Portfolio: [lucas-blanger.vercel.app](https://lucas-blanger.vercel.app)

---

⭐ If you found this project interesting, please consider giving it a star!
