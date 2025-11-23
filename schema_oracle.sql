CREATE TABLE usuario (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome VARCHAR2(200),
  email VARCHAR2(200) UNIQUE
);

CREATE TABLE carreira (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nome VARCHAR2(200) NOT NULL,
  descricao VARCHAR2(1000)
);

CREATE TABLE curso (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  titulo VARCHAR2(300),
  provedor VARCHAR2(120),
  carga_horaria NUMBER
);

CREATE TABLE peso_classe_carreira (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  classe_yolo VARCHAR2(120) NOT NULL,
  carreira_id NUMBER REFERENCES carreira(id),
  peso NUMBER
);

CREATE TABLE deteccao (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  usuario_id NUMBER REFERENCES usuario(id),
  criado_em TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE detalhe_deteccao (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  deteccao_id NUMBER REFERENCES deteccao(id),
  label VARCHAR2(120),
  confidence NUMBER,
  x NUMBER, y NUMBER, w NUMBER, h NUMBER
);

CREATE TABLE trilha (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  usuario_id NUMBER REFERENCES usuario(id),
  carreira_id NUMBER REFERENCES carreira(id),
  score_total NUMBER,
  criado_em TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE trilha_item (
  id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  trilha_id NUMBER REFERENCES trilha(id),
  curso_id NUMBER REFERENCES curso(id),
  ordem NUMBER
);

-- índices úteis
CREATE INDEX idx_detalhe_deteccao_det ON detalhe_deteccao(deteccao_id);
CREATE INDEX idx_peso_classe_carreira_classe ON peso_classe_carreira(classe_yolo);
