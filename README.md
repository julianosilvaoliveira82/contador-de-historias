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

## Próximos Passos (TODO)
- Adicionar PIN para proteger a saída do modo leitor.
- Integrar Supabase para coleções de histórias, storage de imagens e áudio, e autenticação.
- Incluir player de áudio para cada história.
- Implementar CRUD completo no painel admin.

> Foco na simplicidade e na família brasileira: mensagens em português, sem anúncios e sem distrações.
