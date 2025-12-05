-- Ativa extensão para gerar UUIDs aleatórios, usada nas chaves primárias
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Tabela de coleções de histórias (ex.: "Contos de aventura", "Histórias de dormir")
CREATE TABLE IF NOT EXISTS collections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    description text,
    sort_order int DEFAULT 0, -- controla a ordem de exibição das coleções
    is_active boolean DEFAULT true, -- permite desativar uma coleção sem apagá-la
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Tabela de histórias individuais; cada história pode pertencer a uma coleção
CREATE TABLE IF NOT EXISTS stories (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id uuid REFERENCES collections(id) ON DELETE SET NULL,
    title text NOT NULL,
    body text NOT NULL,
    image_url text,
    audio_url text,
    is_published boolean DEFAULT false, -- indica se a história está pronta para aparecer no modo leitor
    sort_order int DEFAULT 0, -- ordenação customizada dentro da coleção
    duration_seconds int, -- duração aproximada do áudio, quando existir
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS stories_collection_sort_idx ON stories (collection_id, sort_order);
CREATE INDEX IF NOT EXISTS stories_published_idx ON stories (is_published);

-- Função para atualizar automaticamente o campo updated_at em cada atualização
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para manter updated_at sincronizado em coleções e histórias
DROP TRIGGER IF EXISTS trg_collections_updated_at ON collections;
CREATE TRIGGER trg_collections_updated_at
BEFORE UPDATE ON collections
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_stories_updated_at ON stories;
CREATE TRIGGER trg_stories_updated_at
BEFORE UPDATE ON stories
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
