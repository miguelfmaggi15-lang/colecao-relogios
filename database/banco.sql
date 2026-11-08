-- Colecao pessoal de relogios - Etapa 1
-- MySQL 8.0.16 ou superior.
CREATE DATABASE IF NOT EXISTS colecao_relogios
  CHARACTER SET utf8mb4;
USE colecao_relogios;

CREATE TABLE IF NOT EXISTS usuario (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(254) NOT NULL,
  senha_hash VARCHAR(255) NOT NULL,
  CONSTRAINT uq_usuario_email UNIQUE (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS marca (
  id_marca INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  CONSTRAINT uq_marca_nome UNIQUE (nome)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS relogio (
  id_relogio INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT NOT NULL,
  id_marca INT NOT NULL,
  modelo VARCHAR(120) NOT NULL,
  referencia VARCHAR(100) NOT NULL,
  mecanismo VARCHAR(15) NOT NULL,
  cor_mostrador VARCHAR(60) NOT NULL,
  data_aquisicao DATE NULL,
  preco_aquisicao DECIMAL(12,2) NULL,
  observacoes TEXT NULL,
  CONSTRAINT fk_relogio_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario(id_usuario) ON DELETE CASCADE,
  CONSTRAINT fk_relogio_marca FOREIGN KEY (id_marca)
    REFERENCES marca(id_marca) ON DELETE RESTRICT,
  CONSTRAINT ck_relogio_mecanismo CHECK (mecanismo IN ('quartzo','automatico','manual')),
  CONSTRAINT ck_relogio_preco CHECK (preco_aquisicao IS NULL OR preco_aquisicao >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS foto (
  id_foto INT AUTO_INCREMENT PRIMARY KEY,
  id_relogio INT NOT NULL,
  caminho_arquivo VARCHAR(255) NOT NULL,
  legenda VARCHAR(200) NULL,
  CONSTRAINT uq_foto_arquivo UNIQUE (caminho_arquivo),
  CONSTRAINT fk_foto_relogio FOREIGN KEY (id_relogio)
    REFERENCES relogio(id_relogio) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pasta (
  id_pasta INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT NOT NULL,
  nome VARCHAR(100) NOT NULL,
  CONSTRAINT fk_pasta_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabela associativa: um relogio pode estar em varias pastas.
-- Conferir o proprietario no Python antes de criar o vinculo (Etapa 2).
CREATE TABLE IF NOT EXISTS relogio_pasta (
  id_relogio INT NOT NULL,
  id_pasta INT NOT NULL,
  PRIMARY KEY (id_relogio, id_pasta),
  CONSTRAINT fk_vinculo_relogio FOREIGN KEY (id_relogio)
    REFERENCES relogio(id_relogio) ON DELETE CASCADE,
  CONSTRAINT fk_vinculo_pasta FOREIGN KEY (id_pasta)
    REFERENCES pasta(id_pasta) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Dados iniciais: executar este INSERT apenas uma vez no banco novo.
INSERT INTO marca (nome) VALUES
 ('Casio'),('Orient'),('Seiko'),('Citizen'),('Rolex'),('Omega'),
 ('TAG Heuer'),('Cartier'),('Tissot'),('Longines');
