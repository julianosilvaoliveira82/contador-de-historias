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

> Observação: a conexão com o Supabase já é usada para listar e editar coleções e histórias. Funcionalidades futuras como upload de mídia e autenticação avançada serão tratadas em etapas seguintes.

## Secrets e Supabase no Streamlit Cloud
Para que o painel admin confirme a conexão com o Supabase, configure os secrets no Streamlit Cloud:

1. Acesse o painel do app no Streamlit Cloud.
2. Vá em **Settings → Secrets**.
3. Defina as chaves `SUPABASE_URL` e `SUPABASE_ANON_KEY` com os valores do seu projeto Supabase.
4. Salve e redeploye o app.

- O código lê esses valores via `st.secrets`; eles **não** devem ser colocados diretamente no código ou no README.
- Após configurar, o modo admin exibirá a mensagem “Conexão com Supabase OK”. Caso não estejam configurados, será mostrado um aviso para adicionar os secrets.

## Histórias no modo leitura (via Supabase)
Com o schema aplicado e os secrets configurados, você pode cadastrar dados pelo Table Editor do Supabase:

1. Em **collections**, crie uma coleção ativa (`is_active = true`), por exemplo “Histórias de coragem”, e ajuste `sort_order` se quiser definir a ordem de exibição.
2. Em **stories**, crie histórias vinculadas informando `collection_id`, `title` e `body`. Campos opcionais: `image_url`, `audio_url` e `duration_seconds`. Marque `is_published = true` e ajuste `sort_order` para controlar a ordem das histórias.
3. Acesse o app no modo leitor (`/` ou `?mode=reader`) e selecione a coleção. As histórias publicadas aparecerão para leitura.

Dicas:
- Se nada aparecer, confira se a coleção está com `is_active = true`, se as histórias estão com `is_published = true` e se os secrets estão configurados corretamente no Streamlit Cloud.
- O app exibe o título, o texto da história e a imagem (quando `image_url` estiver preenchido). O player de áudio ainda não está disponível; apenas mostramos uma mensagem informando que chegará em breve.

## Usando o painel admin (CRUD de coleções e histórias)
O painel admin permite criar e editar coleções e histórias diretamente nas tabelas `collections` e `stories` do Supabase.

Passo a passo:
1. Acesse o app com `?mode=admin`.
2. Faça login com `ADMIN_USERNAME` e `ADMIN_PASSWORD` definidos nos Secrets.
3. Em **Coleções**, crie uma nova coleção informando nome, `is_active` e `sort_order`.
4. Em **Histórias**, selecione a coleção desejada e cadastre histórias com título, texto, `image_url` opcional, `audio_url` opcional, `is_published` e `sort_order`.
5. Marque `is_published = true` para que a história apareça no modo leitor.

Dicas de solução de problemas:
- Se algo não aparecer no leitor, verifique se a coleção está ativa (`is_active = true`) e se a história está publicada (`is_published = true`).
- Em caso de erro ao salvar, tente novamente mais tarde e confira a conexão com o Supabase.
- Exclusões podem ser feitas no Table Editor do Supabase por enquanto; versões futuras podem incluir exclusão no painel com fluxos seguros.

Aviso de segurança doméstica: este CRUD é pensado para uso familiar. Para abrir ao público, será preciso revisar autenticação, segurança e trilhas de auditoria.

## PIN do leitor e login do admin
Proteções leves para organizar o acesso dentro da família:

- **PIN do leitor**: barreira simples para o Benício. Não é segurança forte, apenas conveniência.
- **Login do admin**: separa a área administrativa (cadastros futuros) da área de leitura.

Configuração dos secrets no Streamlit Cloud:

1. Acesse o painel do app no Streamlit Cloud.
2. Vá em **Settings → Secrets**.
3. Adicione as chaves (exemplo de nomes, não use estes valores em produção):
   - `READER_PIN = "1234"` (use um PIN numérico combinado com a família)
   - `ADMIN_USERNAME = "admin"`
   - `ADMIN_PASSWORD = "uma_senha_forte"`
4. Salve e redeploye o app.

Comportamento esperado:

- Sem `READER_PIN`: o modo leitor abre direto e mostra um aviso discreto sugerindo configurar o PIN.
- Com `READER_PIN`: o app pede o PIN uma vez por sessão; ao validar, libera as histórias. PIN incorreto mostra um erro amigável.
- Sem `ADMIN_USERNAME`/`ADMIN_PASSWORD`: ao acessar `?mode=admin`, o app alerta que o login não está configurado e não exibe o painel.
- Com `ADMIN_USERNAME`/`ADMIN_PASSWORD`: ao acessar `?mode=admin`, o app pede usuário e senha; após sucesso, mostra o status do Supabase.

Segurança:

- Nunca coloque PIN, usuário ou senha diretamente no código ou no README. Use apenas secrets do Streamlit Cloud.
- Para abrir o app ao público no futuro, será necessário um sistema de autenticação mais robusto (fora do escopo deste passo).

## Próximos Passos (TODO)
- Integrar storage de imagens/áudios no Supabase e adicionar autenticação mais robusta.
- Incluir player de áudio para cada história.
- Adicionar exclusão segura e trilhas de auditoria para coleções e histórias.

> Foco na simplicidade e na família brasileira: mensagens em português, sem anúncios e sem distrações.
