CREATE DATABASE IF NOT EXISTS almoxarifado;
USE almoxarifado;

-- =========================
-- 👤 USUÁRIOS
-- =========================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('ADMIN', 'USUARIO') DEFAULT 'USUARIO',
    ativo TINYINT(1) DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- 📦 MATERIAIS
-- =========================
CREATE TABLE materiais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE,
    nome VARCHAR(120) NOT NULL,
    categoria VARCHAR(80),
    quantidade_total INT DEFAULT 0,
    quantidade_disponivel INT DEFAULT 0,
    status ENUM('DISPONIVEL', 'INDISPONIVEL') DEFAULT 'DISPONIVEL',
    localizacao VARCHAR(80),
    observacao TEXT,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_material_nome ON materiais(nome);

-- =========================
-- 🚗 VEÍCULOS
-- =========================
CREATE TABLE veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(15) UNIQUE NOT NULL,
    descricao VARCHAR(100)
);

-- =========================
-- 📋 LISTAS MODELO
-- =========================
CREATE TABLE listas_modelo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE listas_modelo_itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lista_id INT NOT NULL,
    material_id INT NOT NULL,
    quantidade INT DEFAULT 1,
    FOREIGN KEY (lista_id) REFERENCES listas_modelo(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materiais(id)
);

-- =========================
-- 🚚 SAÍDAS
-- =========================
CREATE TABLE saidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    responsavel VARCHAR(100),
    data_saida DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_retorno DATETIME NULL,
    status ENUM('ABERTO', 'FECHADO', 'CANCELADO') DEFAULT 'ABERTO',

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);

CREATE INDEX idx_saida_data ON saidas(data_saida);
CREATE INDEX idx_saida_usuario ON saidas(usuario_id);

-- =========================
-- 📦 ITENS DA SAÍDA
-- =========================
CREATE TABLE saida_itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    saida_id INT NOT NULL,
    material_id INT NOT NULL,
    quantidade INT NOT NULL,
    retornado INT DEFAULT 0,

    FOREIGN KEY (saida_id) REFERENCES saidas(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materiais(id)
);

-- =========================
-- 📊 MOVIMENTAÇÃO DE ESTOQUE (🔥 NOVO - CRÍTICO)
-- =========================
CREATE TABLE movimentacoes_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT NOT NULL,
    tipo ENUM('ENTRADA', 'SAIDA', 'RETORNO') NOT NULL,
    quantidade INT NOT NULL,
    referencia_id INT,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (material_id) REFERENCES materiais(id)
);

-- =========================
-- 🧠 HISTÓRICO (EVOLUÍDO)
-- =========================
CREATE TABLE historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    entidade VARCHAR(50),
    entidade_id INT,
    acao VARCHAR(50),
    dados_antes JSON,
    dados_depois JSON,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- =========================
-- 📈 VIEW PARA DASHBOARD (BI)
-- =========================
CREATE VIEW vw_dashboard_saidas AS
SELECT 
    DATE(data_saida) AS data,
    COUNT(*) AS total
FROM saidas
GROUP BY DATE(data_saida);