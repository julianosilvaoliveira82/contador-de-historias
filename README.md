# Contador de Histórias

Um livro digital vivo e personalizado para o Benício, feito em Streamlit. O objetivo é oferecer uma experiência simples, acolhedora e sem anúncios para leitura de histórias em família.

## Modos do app
- **Leitor (padrão)**: abre automaticamente quando nenhum parâmetro é informado ou quando `?mode=reader` está presente na URL.
- **Admin**: modo de administração acessível via `?mode=admin`.

URLs de exemplo:
- Leitor: `https://meu-app.streamlit.app/` ou `https://meu-app.streamlit.app/?mode=reader`
- Admin: `https://meu-app.streamlit.app/?mode=admin`

## Como rodar localmente
1. Clonar o repositório.
2. Instalar dependências: `pip install -r requirements.txt`
3. Executar: `streamlit run app.py`
4. Abrir o navegador na URL indicada pelo terminal (por padrão, `http://localhost:8501`).

## Publicação no Streamlit Cloud
1. Conectar este repositório no Streamlit Cloud.
2. Selecionar `app.py` como arquivo principal.
3. Confirmar a instalação automática via `requirements.txt`.
4. Quando houver integrações (ex.: Supabase), adicionar secrets em `.streamlit/secrets.toml` diretamente na interface do Streamlit Cloud.

## Configuração do Supabase
O Supabase será usado para armazenar coleções e histórias, incluindo textos, imagens e áudios. Siga os passos para criar o schema inicial:

1. Acesse o painel do Supabase do seu projeto.
2. Abra o **SQL Editor**.
3. Copie o conteúdo de `supabase/schema.sql` deste repositório.
4. Execute o script para criar as tabelas e índices.
5. Verifique no menu **Table Editor** se as tabelas `collections` e `stories` foram criadas corretamente.

> Segurança: nunca coloque `<SUPABASE_URL>`, `<SUPABASE_ANON_KEY>` ou senhas diretamente no código ou neste README. Quando a integração com Supabase for implementada, use apenas secrets/variáveis de ambiente.

> Próximos passos: a integração do app Streamlit com o Supabase (leitura de coleções/histórias, upload de mídia e autenticação) será feita em etapa futura.

## Próximos Passos (TODO)
- Adicionar PIN para proteger a saída do modo leitor.
- Integrar Supabase para coleções de histórias, storage de imagens e áudio, e autenticação.
- Incluir player de áudio para cada história.
- Implementar CRUD completo no painel admin.

> Foco na simplicidade e na família brasileira: mensagens em português, sem anúncios e sem distrações.
