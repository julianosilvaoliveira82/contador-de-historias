"""Cliente Supabase com leitura via secrets do Streamlit Cloud."""

import streamlit as st


@st.cache_resource
def get_supabase_client():
    """Cria e reutiliza o cliente Supabase se as secrets estiverem configuradas.

    Retorna None quando as chaves não existem ou quando a biblioteca não está
    disponível, permitindo que o app continue funcionando sem integração.
    """

    # Tenta importar o cliente do pacote supabase; se não existir, seguimos sem erro.
    try:
        from supabase import create_client
    except Exception:
        return None

    supabase_url = st.secrets.get("SUPABASE_URL")
    supabase_key = st.secrets.get("SUPABASE_ANON_KEY")

    # Caso os secrets não estejam configurados, devolvemos None.
    if not supabase_url or not supabase_key:
        return None

    try:
        return create_client(supabase_url, supabase_key)
    except Exception:
        # Qualquer falha de criação retorna None para não interromper o app.
        return None
