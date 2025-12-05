import random
from pathlib import Path

import streamlit as st

from stories_repository import (
    get_active_collections,
    get_all_published_stories,
    get_published_stories_by_collection,
    list_collections_for_admin,
    create_collection,
    update_collection,
    list_stories_for_collection_admin,
    create_story,
    update_story,
    update_story_media,
    delete_story,
    log_story_read,
    get_recent_reads,
    get_read_count_by_story,
)
from supabase_client import get_supabase_client


def upload_media_file(client, bucket: str, path: str, file_obj):
    """Envia um arquivo para o bucket indicado e retorna a URL pública ou None em falha."""

    try:
        data = file_obj.read()
        storage = client.storage.from_(bucket)
        storage.upload(path, data, {
            "content-type": file_obj.type or "application/octet-stream",
            "upsert": True,
        })
        public_url = storage.get_public_url(path)
        if isinstance(public_url, dict):
            return public_url.get("publicUrl") or public_url.get("public_url")
        return public_url
    except Exception as exc:  # pragma: no cover - feedback simples
        print(f"[Supabase] Erro ao enviar arquivo para {bucket}/{path}: {exc}")
        return None


def get_mode_from_query_params() -> str:
    """Lê o parâmetro de querystring e define o modo atual."""
    params = st.experimental_get_query_params()
    mode_param = params.get("mode", ["reader"])[0].lower()
    if mode_param == "admin":
        return "admin"
    return "reader"


def reader_pin_gate() -> bool:
    """Valida o PIN do modo leitor usando secrets e session_state."""

    try:
        configured_pin = st.secrets.get("READER_PIN")
    except Exception:
        st.warning(
            "Não foi possível verificar o PIN nos secrets. O acesso está liberado,"
            " mas configure READER_PIN em Settings → Secrets para ativar o bloqueio"
            " leve."
        )
        return True

    if not configured_pin:
        st.info(
            "PIN do leitor não configurado. Defina READER_PIN em Settings → Secrets"
            " para ativar o bloqueio leve."
        )
        return True

    if st.session_state.get("reader_authenticated") is True:
        return True

    st.subheader("Digite o PIN para continuar")
    pin_input = st.text_input("PIN", type="password")

    if st.button("Entrar"):
        if pin_input == str(configured_pin):
            st.session_state["reader_authenticated"] = True
            st.rerun()
        else:
            st.error("PIN incorreto. Tente novamente.")

    return False


def admin_login_gate() -> bool:
    """Valida as credenciais do modo admin usando secrets e session_state."""

    try:
        username = st.secrets.get("ADMIN_USERNAME")
        password = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        st.warning(
            "Não foi possível ler as credenciais de admin nos secrets. Configure"
            " ADMIN_USERNAME e ADMIN_PASSWORD em Settings → Secrets no"
            " Streamlit Cloud."
        )
        return False

    if not username or not password:
        st.warning(
            "Login do admin não configurado. Defina ADMIN_USERNAME e"
            " ADMIN_PASSWORD em Settings → Secrets para proteger o painel."
        )
        return False

    if st.session_state.get("admin_authenticated") is True:
        return True

    st.subheader("Login do admin")
    input_user = st.text_input("Usuário")
    input_password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if input_user == str(username) and input_password == str(password):
            st.session_state["admin_authenticated"] = True
            st.success("Login realizado com sucesso.")
            return True
        else:
            st.error("Credenciais inválidas. Tente novamente.")

    return False


def render_story_content(story: dict) -> None:
    """Exibe título, corpo, imagem e mensagens auxiliares da história."""
    st.header(story.get("title", "História"))

    image_url = story.get("image_url")
    if image_url:
        st.image(image_url, use_column_width=True)
        button_key = f"view_image_{story.get('id', 'story')}"
        if st.button("Ver imagem em tela cheia", key=button_key):
            with st.modal("Imagem da história"):
                st.image(image_url, use_column_width=True)

    body = story.get("body", "") or ""
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [body]

    for paragraph in paragraphs:
        st.write(paragraph)

    audio_url = story.get("audio_url")
    if audio_url:
        st.audio(audio_url)
        st.caption("Ouvir esta história")
    else:
        st.info("Áudio desta história ainda não está disponível.")


def render_reader_mode() -> None:
    """Renderiza a tela principal para leitura das histórias."""
    st.title("Histórias do Benício")

    st.markdown(
        """
        Bem-vindo! As histórias estão ganhando vida. Em breve teremos áudio
        narrado, imagens em tela cheia e muito mais para curtir junto com a
        família.
        """
    )

    st.markdown(
        """
        Este app nasceu como um livro digital vivo, feito sob medida para o
        Benício. A proposta é simples: leitura tranquila, sem anúncios e sem
        distrações, para aproveitar momentos de imaginação e afeto.
        """
    )

    if not reader_pin_gate():
        return

    st.session_state.setdefault("current_collection_id", None)
    st.session_state.setdefault("current_story_id", None)
    st.session_state.setdefault("last_random_story_id", None)
    st.session_state.setdefault("reader_focus_mode", False)

    client = get_supabase_client()

    if client is None:
        st.info(
            "Histórias ainda não disponíveis porque o Supabase não está "
            "configurado. Adicione SUPABASE_URL e SUPABASE_ANON_KEY em Settings "
            "→ Secrets no Streamlit Cloud."
        )
        return

    def fetch_story_by_id(story_id: str):
        try:
            all_published = get_all_published_stories(client)
            return next((s for s in all_published if s.get("id") == story_id), None)
        except Exception as exc:  # pragma: no cover - log simples
            print(f"[Supabase] Erro ao buscar história por id: {exc}")
            return None

    # Modo focado: mostra apenas a história escolhida e um botão de voltar
    if st.session_state.get("reader_focus_mode") and st.session_state.get("current_story_id"):
        story = fetch_story_by_id(st.session_state.get("current_story_id"))
        if st.button("Voltar para lista"):
            st.session_state["reader_focus_mode"] = False
            st.rerun()
            return

        if story:
            render_story_content(story)
            return

        st.info(
            "Não encontramos esta história agora. Voltamos para a lista para você tentar novamente."
        )
        st.session_state["reader_focus_mode"] = False
        st.session_state["current_story_id"] = None

    collections = get_active_collections(client)

    if not collections:
        st.info("Nenhuma coleção disponível ainda. Cadastre novas coleções no Supabase.")
        return

    selected_collection = next(
        (c for c in collections if c.get("id") == st.session_state.get("current_collection_id")),
        None,
    )

    st.markdown("### Escolha uma coleção")
    cols_per_row = min(3, len(collections)) or 1
    for start in range(0, len(collections), cols_per_row):
        row = st.columns(cols_per_row)
        for col, collection in zip(row, collections[start : start + cols_per_row]):
            with col:
                st.markdown(f"#### {collection.get('name', 'Coleção')}")
                if collection.get("description"):
                    st.caption(collection.get("description"))

                is_selected = selected_collection and collection.get("id") == selected_collection.get("id")
                button_label = "Coleção selecionada" if is_selected else "Ler esta coleção"
                if st.button(button_label, key=f"collection_btn_{collection.get('id')}", use_container_width=True):
                    st.session_state["current_collection_id"] = collection.get("id")
                    st.session_state["current_story_id"] = None
                    st.session_state["last_random_story_id"] = None
                    st.session_state["reader_focus_mode"] = False
                    selected_collection = collection
                    st.rerun()

    if selected_collection:
        st.success(f"Coleção escolhida: {selected_collection.get('name')}")
    else:
        st.info("Escolha uma coleção acima ou use o botão de sorteio.")

    stories_in_collection = []
    if selected_collection:
        stories_in_collection = get_published_stories_by_collection(
            client, selected_collection.get("id")
        )
        for story in stories_in_collection:
            story.setdefault("collection_id", selected_collection.get("id"))

    st.markdown("---")
    st.markdown("### História da noite")
    if st.button("História da noite", use_container_width=True):
        candidate_stories = (
            stories_in_collection if selected_collection else get_all_published_stories(client)
        )

        if not candidate_stories:
            st.info(
                "Ainda não há histórias publicadas para sortear. Cadastre e publique histórias no painel admin."
            )
        else:
            last_id = st.session_state.get("last_random_story_id")
            pool = [s for s in candidate_stories if s.get("id") != last_id] or candidate_stories
            chosen_story = random.choice(pool)
            st.session_state["last_random_story_id"] = chosen_story.get("id")
            st.session_state["current_story_id"] = chosen_story.get("id")
            chosen_collection_id = chosen_story.get("collection_id")
            if chosen_collection_id:
                st.session_state["current_collection_id"] = chosen_collection_id

            st.session_state["reader_focus_mode"] = True
            log_story_read(client, chosen_story.get("id"), chosen_collection_id, source="random")
            st.success("História sorteada! Aproveitem a leitura.")
            st.rerun()

    st.markdown("---")
    st.markdown("### Escolher história manualmente")
    if not selected_collection:
        st.info("Selecione uma coleção acima para navegar pelas histórias ou use o sorteio.")
    else:
        if not stories_in_collection:
            st.info("Nenhuma história publicada nesta coleção ainda. Cadastre novas histórias no painel admin.")
        else:
            st.caption(
                "Toque em uma das histórias abaixo ou use o botão de sorteio para descobrir a história da noite."
            )
            cols_per_row = 2
            for start in range(0, len(stories_in_collection), cols_per_row):
                row = st.columns(cols_per_row)
                for col, story in zip(row, stories_in_collection[start : start + cols_per_row]):
                    with col:
                        st.markdown(f"**{story.get('title', 'História')}**")
                        if st.button("Ler esta história", key=f"story_btn_{story.get('id')}", use_container_width=True):
                            st.session_state["current_story_id"] = story.get("id")
                            st.session_state["last_random_story_id"] = None
                            st.session_state["reader_focus_mode"] = True
                            log_story_read(
                                client,
                                story.get("id"),
                                st.session_state.get("current_collection_id"),
                                source="manual",
                            )
                            st.rerun()

    # Caso o usuário já tenha uma história selecionada, exibe o conteúdo padrão
    if st.session_state.get("current_story_id"):
        story_to_display = fetch_story_by_id(st.session_state.get("current_story_id"))
        if story_to_display:
            st.markdown("---")
            render_story_content(story_to_display)
        else:
            st.info("Escolha ou sorteie uma história para começar a leitura.")
    else:
        st.info("Escolha ou sorteie uma história para começar a leitura.")


def render_collections_admin(client) -> None:
    """Interface de criação e edição de coleções."""

    st.header("Coleções")
    collections = list_collections_for_admin(client)

    if collections:
        st.table(
            [
                {
                    "id": c.get("id"),
                    "nome": c.get("name"),
                    "ativa": c.get("is_active"),
                    "ordem": c.get("sort_order"),
                }
                for c in collections
            ]
        )
    else:
        st.info("Nenhuma coleção encontrada.")

    st.subheader("Nova coleção")
    with st.form("create_collection_form"):
        name = st.text_input("Nome", key="create_collection_name")
        description = st.text_area("Descrição", key="create_collection_description")
        sort_order = st.number_input("Ordem", value=0, step=1, key="create_collection_sort")
        is_active = st.checkbox("Coleção ativa", value=True, key="create_collection_active")
        submitted = st.form_submit_button("Criar coleção")

        if submitted:
            if not name.strip():
                st.error("Informe um nome para a coleção.")
            else:
                created = create_collection(
                    client,
                    {
                        "name": name.strip(),
                        "description": description.strip() if description else None,
                        "sort_order": int(sort_order),
                        "is_active": is_active,
                    },
                )
                if created:
                    st.success("Coleção criada com sucesso!")
                    st.rerun()
                else:
                    st.error("Não foi possível criar a coleção agora. Tente novamente.")

    st.subheader("Editar coleção")
    if not collections:
        st.info("Cadastre uma coleção para editar aqui.")
        return

    with st.form("edit_collection_form"):
        collection_index = st.selectbox(
            "Selecione a coleção",
            range(len(collections)),
            format_func=lambda idx: collections[idx].get("name", "Coleção"),
            key="edit_collection_select",
        )
        selected_collection = collections[collection_index]

        edit_name = st.text_input(
            "Nome", value=selected_collection.get("name", ""), key="edit_collection_name"
        )
        edit_description = st.text_area(
            "Descrição",
            value=selected_collection.get("description", "") or "",
            key="edit_collection_description",
        )
        edit_sort_order = st.number_input(
            "Ordem",
            value=int(selected_collection.get("sort_order") or 0),
            step=1,
            key="edit_collection_sort",
        )
        edit_is_active = st.checkbox(
            "Coleção ativa",
            value=bool(selected_collection.get("is_active", True)),
            key="edit_collection_active",
        )

        save_changes = st.form_submit_button("Salvar alterações")
        if save_changes:
            if not edit_name.strip():
                st.error("Informe um nome para a coleção.")
            else:
                updated = update_collection(
                    client,
                    selected_collection.get("id"),
                    {
                        "name": edit_name.strip(),
                        "description": edit_description.strip() if edit_description else None,
                        "sort_order": int(edit_sort_order),
                        "is_active": edit_is_active,
                    },
                )
                if updated:
                    st.success("Coleção atualizada com sucesso!")
                    st.rerun()
                else:
                    st.error("Não foi possível atualizar a coleção. Tente novamente.")


def render_stories_admin(client, collections) -> None:
    """Interface de criação e edição de histórias."""

    st.subheader("Histórias")

    if not collections:
        st.info("Cadastre uma coleção para gerenciar histórias aqui.")
        return

    collection_index = st.selectbox(
        "Coleção para gerenciar histórias",
        range(len(collections)),
        format_func=lambda idx: collections[idx].get("name", "Coleção"),
        key="stories_collection_select",
    )
    selected_collection = collections[collection_index]
    collection_id = selected_collection.get("id")

    stories = list_stories_for_collection_admin(client, collection_id)

    if stories:
        st.table(
            [
                {
                    "título": s.get("title"),
                    "publicada": s.get("is_published"),
                    "ordem": s.get("sort_order"),
                }
                for s in stories
            ]
        )
    else:
        st.info("Nenhuma história cadastrada nesta coleção ainda.")

    st.markdown("---")

    st.markdown("### Nova história")
    with st.form("create_story_form"):
        title = st.text_input("Título", key="create_story_title")
        body = st.text_area("Texto", key="create_story_body")
        image_url = st.text_input("URL da imagem (opcional)", key="create_story_image")
        audio_url = st.text_input("URL do áudio (opcional)", key="create_story_audio")
        image_file = st.file_uploader(
            "Imagem da história (opcional)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="create_story_image_upload",
        )
        audio_file = st.file_uploader(
            "Áudio da história (opcional)",
            type=["mp3", "wav", "m4a", "ogg"],
            accept_multiple_files=False,
            key="create_story_audio_upload",
        )
        sort_order = st.number_input("Ordem", value=0, step=1, key="create_story_sort")
        is_published = st.checkbox("História publicada", value=False, key="create_story_published")
        create_submit = st.form_submit_button("Criar história")

        if create_submit:
            if not title.strip() or not body.strip():
                st.error("Informe título e texto para criar a história.")
            else:
                created = create_story(
                    client,
                    {
                        "collection_id": collection_id,
                        "title": title.strip(),
                        "body": body.strip(),
                        "image_url": image_url.strip() if image_url else None,
                        "audio_url": audio_url.strip() if audio_url else None,
                        "sort_order": int(sort_order),
                        "is_published": is_published,
                    },
                )
                if created:
                    upload_errors = False
                    story_id = created.get("id")

                    if image_file and story_id:
                        image_ext = Path(image_file.name).suffix or ".png"
                        image_path = f"stories/{story_id}/cover{image_ext}"
                        image_public_url = upload_media_file(
                            client, "story-images", image_path, image_file
                        )
                        if image_public_url:
                            update_story_media(client, story_id, image_url=image_public_url)
                        else:
                            upload_errors = True
                            st.error("Não foi possível enviar a imagem. Tente novamente.")

                    if audio_file and story_id:
                        audio_ext = Path(audio_file.name).suffix or ".mp3"
                        audio_path = f"stories/{story_id}/audio{audio_ext}"
                        audio_public_url = upload_media_file(
                            client, "story-audio", audio_path, audio_file
                        )
                        if audio_public_url:
                            update_story_media(client, story_id, audio_url=audio_public_url)
                        else:
                            upload_errors = True
                            st.error("Não foi possível enviar o áudio. Tente novamente.")

                    if not upload_errors:
                        st.success("História criada com sucesso!")
                        st.rerun()
                else:
                    st.error("Não foi possível criar a história. Tente novamente.")

    st.markdown("### Editar história")
    if not stories:
        st.info("Cadastre uma história para editar aqui.")
        return

    with st.form("edit_story_form"):
        story_index = st.selectbox(
            "Selecione a história",
            range(len(stories)),
            format_func=lambda idx: stories[idx].get("title", "História"),
            key="edit_story_select",
        )
        selected_story = stories[story_index]

        collection_options = {c.get("name", "Coleção"): c.get("id") for c in collections}
        current_collection_id = selected_story.get("collection_id") or collection_id
        edit_collection_name = next(
            (name for name, cid in collection_options.items() if cid == current_collection_id), None
        )

        edit_title = st.text_input(
            "Título",
            value=selected_story.get("title", ""),
            key="edit_story_title",
        )
        edit_body = st.text_area(
            "Texto",
            value=selected_story.get("body", "") or "",
            key="edit_story_body",
        )
        edit_collection = st.selectbox(
            "Coleção desta história",
            list(collection_options.keys()),
            index=list(collection_options.keys()).index(edit_collection_name)
            if edit_collection_name in collection_options
            else 0,
            key="edit_story_collection",
        )
        edit_image_url = st.text_input(
            "URL da imagem (opcional)",
            value=selected_story.get("image_url", "") or "",
            key="edit_story_image",
        )
        edit_audio_url = st.text_input(
            "URL do áudio (opcional)",
            value=selected_story.get("audio_url", "") or "",
            key="edit_story_audio",
        )
        new_image_file = st.file_uploader(
            "Imagem da história (opcional)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="edit_story_image_upload",
        )
        new_audio_file = st.file_uploader(
            "Áudio da história (opcional)",
            type=["mp3", "wav", "m4a", "ogg"],
            accept_multiple_files=False,
            key="edit_story_audio_upload",
        )
        edit_sort_order = st.number_input(
            "Ordem",
            value=int(selected_story.get("sort_order") or 0),
            step=1,
            key="edit_story_sort",
        )
        edit_is_published = st.checkbox(
            "História publicada",
            value=bool(selected_story.get("is_published", False)),
            key="edit_story_published",
        )

        save_story = st.form_submit_button("Salvar alterações")
        delete_confirm = st.checkbox(
            "Quero excluir esta história (ação permanente)", key="delete_story_confirm"
        )
        delete_story_btn = st.form_submit_button("Excluir história")

        if save_story:
            if not edit_title.strip() or not edit_body.strip():
                st.error("Informe título e texto para atualizar a história.")
            else:
                updated = update_story(
                    client,
                    selected_story.get("id"),
                    {
                        "title": edit_title.strip(),
                        "body": edit_body.strip(),
                        "image_url": edit_image_url.strip() if edit_image_url else None,
                        "audio_url": edit_audio_url.strip() if edit_audio_url else None,
                        "sort_order": int(edit_sort_order),
                        "is_published": edit_is_published,
                        "collection_id": collection_options.get(edit_collection),
                    },
                )
                if updated:
                    upload_errors = False
                    story_id = selected_story.get("id")

                    if new_image_file and story_id:
                        image_ext = Path(new_image_file.name).suffix or ".png"
                        image_path = f"stories/{story_id}/cover{image_ext}"
                        image_public_url = upload_media_file(
                            client, "story-images", image_path, new_image_file
                        )
                        if image_public_url:
                            update_story_media(client, story_id, image_url=image_public_url)
                        else:
                            upload_errors = True
                            st.error("Não foi possível enviar a nova imagem. Tente novamente.")

                    if new_audio_file and story_id:
                        audio_ext = Path(new_audio_file.name).suffix or ".mp3"
                        audio_path = f"stories/{story_id}/audio{audio_ext}"
                        audio_public_url = upload_media_file(
                            client, "story-audio", audio_path, new_audio_file
                        )
                        if audio_public_url:
                            update_story_media(client, story_id, audio_url=audio_public_url)
                        else:
                            upload_errors = True
                            st.error("Não foi possível enviar o novo áudio. Tente novamente.")

                    if not upload_errors:
                        st.success("História atualizada com sucesso!")
                        st.rerun()
                else:
                    st.error("Não foi possível atualizar a história. Tente novamente.")

        if delete_story_btn:
            if not delete_confirm:
                st.warning("Marque a caixa de confirmação antes de excluir.")
            else:
                if delete_story(client, selected_story.get("id")):
                    st.success("História excluída com sucesso.")
                    st.rerun()
                else:
                    st.error("Não foi possível excluir a história agora. Tente novamente.")


def render_admin_mode() -> None:
    """Renderiza a interface de administração."""
    st.title("Painel admin – Contador de Histórias")

    st.markdown(
        """
        Esta é a área de administração. Você pode criar e editar coleções e
        histórias que serão apresentadas no modo leitor. Para abrir ao público,
        no futuro vamos avaliar autenticação e permissões mais fortes.
        """
    )

    if not admin_login_gate():
        return

    # Botão para encerrar sessão admin de forma clara
    logout_col, _ = st.columns([1, 3])
    with logout_col:
        if st.button("Sair do painel admin"):
            st.session_state["admin_authenticated"] = False
            st.rerun()

    supabase_client = get_supabase_client()
    if supabase_client is None:
        st.warning(
            "Supabase não configurado. Defina SUPABASE_URL e SUPABASE_ANON_KEY"
            " em Settings → Secrets no Streamlit Cloud."
        )
        return

    st.success("Conexão com Supabase OK")

    render_collections_admin(supabase_client)
    st.markdown("---")
    render_stories_admin(supabase_client, list_collections_for_admin(supabase_client))

    st.markdown("---")
    st.subheader("Histórico de leitura")

    recent = get_recent_reads(supabase_client, limit=20)
    if recent:
        friendly_source = {"random": "História da noite", "manual": "Escolha manual"}
        st.table(
            [
                {
                    "Quando": str(item.get("created_at")),
                    "Coleção": item.get("collection_name") or "—",
                    "História": item.get("title") or "—",
                    "Origem": friendly_source.get(item.get("source"), "Escolha manual"),
                }
                for item in recent
            ]
        )
    else:
        st.info("Nenhuma leitura registrada ainda.")

    ranking = get_read_count_by_story(supabase_client)
    if ranking:
        st.markdown("### Histórias mais lidas")
        for item in ranking:
            st.write(f"{item.get('title')} – {item.get('read_count')} leitura(s)")
    else:
        st.info("O ranking aparecerá após as primeiras leituras.")


def main() -> None:
    """Função principal que organiza os modos do app."""
    st.set_page_config(page_title="Contador de Histórias", page_icon=None, layout="wide")

    mode = get_mode_from_query_params()

    if mode == "admin":
        render_admin_mode()
    else:
        render_reader_mode()


if __name__ == "__main__":
    main()
