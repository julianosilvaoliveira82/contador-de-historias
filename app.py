import streamlit as st


def get_mode_from_query_params() -> str:
    """Lê o parâmetro de querystring e define o modo atual."""
    params = st.experimental_get_query_params()
    mode_param = params.get("mode", ["reader"])[0].lower()
    if mode_param == "admin":
        return "admin"
    return "reader"


def render_reader_mode() -> None:
    """Renderiza a tela principal para leitura das histórias."""
    st.title("Histórias do Benício")

    st.markdown(
        """
        Bem-vindo! As histórias ainda estão em construção, mas em breve
        teremos áudio narrado, imagens em tela cheia e muito mais para curtir
        junto com a família.
        """
    )

    st.markdown(
        """
        Este app nasceu como um livro digital vivo, feito sob medida para o
        Benício. A proposta é simples: leitura tranquila, sem anúncios e sem
        distrações, para aproveitar momentos de imaginação e afeto.
        """
    )

    # TODO: Adicionar PIN para proteger a saída do modo leitor.
    # TODO: Integrar Supabase para coleções de histórias e storage de imagem/áudio.
    # TODO: Incluir player de áudio para cada história.


def render_admin_mode() -> None:
    """Renderiza a interface de administração."""
    st.title("Painel admin – Contador de Histórias")

    st.markdown(
        """
        Esta é a área de administração. Em breve, você poderá cadastrar,
        editar e organizar histórias com upload de imagens e áudio. Também
        teremos autenticação e permissões para manter o ambiente seguro.
        """
    )

    # TODO: Implementar CRUD completo das histórias no painel admin.
    # TODO: Conectar com Supabase para gerenciar dados e arquivos.


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
