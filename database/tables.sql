CREATE DATABASE IF NOT EXISTS nego_maq;
USE nego_maq;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuario (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produto (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    categoria ENUM('facas', 'aventais', 'estojos', 'churrascos') NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    img TEXT,
    estoque INT NOT NULL DEFAULT 0
);

-- Tabela de carrinho 
CREATE TABLE IF NOT EXISTS carrinho (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(36),
    produto_id VARCHAR(36),
    quantidade INT DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produto(id) ON DELETE CASCADE
);

-- Tabela de Eventos 
CREATE TABLE evento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(36),
    produto_id VARCHAR(36),
    tipo_evento VARCHAR(50), -- "visualizacao", "adicao_carrinho", "compra", "busca", "clique"
    valor DECIMAL(10, 2) NULL,
    data_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL,
    FOREIGN KEY (produto_id) REFERENCES produto(id) ON DELETE SET NULL
);
