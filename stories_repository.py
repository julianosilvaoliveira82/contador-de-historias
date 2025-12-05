"""Consultas e operações de histórias armazenadas no Supabase."""

from typing import List, Optional, Dict, Any
import random


Story = Dict[str, Any]
Collection = Dict[str, Any]


def get_active_collections(client) -> List[Collection]:
    """Retorna coleções ativas ordenadas por sort_order e nome.

    Em caso de erro, registra no log e devolve lista vazia para não quebrar a UI.
    """

    try:
        response = (
            client.table("collections")
            .select("id,name,description,sort_order")
            .eq("is_active", True)
            .order("sort_order")
            .order("name")
            .execute()
        )
        return response.data or []
    except Exception as exc:  # pragma: no cover - log simples para debug
        print(f"[Supabase] Erro ao buscar coleções ativas: {exc}")
        return []


def get_published_stories_by_collection(client, collection_id: str) -> List[Story]:
    """Retorna histórias publicadas de uma coleção específica, ordenadas por sort_order e título."""

    try:
        response = (
            client.table("stories")
            .select(
                "id,title,body,image_url,audio_url,duration_seconds,sort_order,collection_id"
            )
            .eq("is_published", True)
            .eq("collection_id", collection_id)
            .order("sort_order")
            .order("title")
            .execute()
        )
        return response.data or []
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao buscar histórias publicadas: {exc}")
        return []


def get_random_published_story(client, collection_id: Optional[str] = None) -> Optional[Story]:
    """Escolhe aleatoriamente uma história publicada, opcionalmente filtrada por coleção."""

    try:
        query = (
            client.table("stories")
            .select(
                "id,title,body,image_url,audio_url,duration_seconds,sort_order,collection_id"
            )
            .eq("is_published", True)
        )

        if collection_id:
            query = query.eq("collection_id", collection_id)

        response = query.execute()
        stories = response.data or []
        if not stories:
            return None

        return random.choice(stories)
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao sortear história publicada: {exc}")
        return None


def get_all_published_stories(client) -> List[Story]:
    """Retorna todas as histórias publicadas, usadas para o sorteio geral no modo leitor."""

    try:
        response = (
            client.table("stories")
            .select(
                "id,title,body,image_url,audio_url,duration_seconds,sort_order,collection_id"
            )
            .eq("is_published", True)
            .order("sort_order")
            .order("title")
            .execute()
        )
        return response.data or []
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao listar histórias publicadas: {exc}")
        return []


# Funções administrativas (CRUD básico)

def list_collections_for_admin(client) -> List[Collection]:
    """Lista todas as coleções para administração, sem filtrar por is_active."""

    try:
        response = (
            client.table("collections")
            .select("id,name,description,sort_order,is_active,created_at,updated_at")
            .order("sort_order")
            .order("name")
            .execute()
        )
        return response.data or []
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao listar coleções (admin): {exc}")
        return []


def create_collection(client, data: Dict[str, Any]) -> Optional[Collection]:
    """Cria uma nova coleção com valores fornecidos."""

    payload = {
        "name": data.get("name"),
        "description": data.get("description"),
        "sort_order": data.get("sort_order", 0),
        "is_active": data.get("is_active", True),
    }

    try:
        response = client.table("collections").insert(payload).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao criar coleção: {exc}")
        return None


def update_collection(client, collection_id: str, data: Dict[str, Any]) -> Optional[Collection]:
    """Atualiza campos de uma coleção específica."""

    payload = {key: value for key, value in data.items()}

    try:
        response = (
            client.table("collections")
            .update(payload)
            .eq("id", collection_id)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao atualizar coleção: {exc}")
        return None


def list_stories_for_collection_admin(client, collection_id: str) -> List[Story]:
    """Lista histórias de uma coleção para administração, sem filtrar por publicação."""

    try:
        response = (
            client.table("stories")
            .select(
                "id,title,body,image_url,audio_url,is_published,sort_order,"
                "duration_seconds,created_at,updated_at,collection_id"
            )
            .eq("collection_id", collection_id)
            .order("sort_order")
            .order("title")
            .execute()
        )
        return response.data or []
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao listar histórias (admin): {exc}")
        return []


def create_story(client, data: Dict[str, Any]) -> Optional[Story]:
    """Cria uma nova história vinculada a uma coleção."""

    payload = {
        "collection_id": data.get("collection_id"),
        "title": data.get("title"),
        "body": data.get("body"),
        "image_url": data.get("image_url"),
        "audio_url": data.get("audio_url"),
        "is_published": data.get("is_published", False),
        "sort_order": data.get("sort_order", 0),
        "duration_seconds": data.get("duration_seconds"),
    }

    try:
        response = client.table("stories").insert(payload).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao criar história: {exc}")
        return None


def update_story(client, story_id: str, data: Dict[str, Any]) -> Optional[Story]:
    """Atualiza campos de uma história específica."""

    payload = {key: value for key, value in data.items()}

    try:
        response = (
            client.table("stories")
            .update(payload)
            .eq("id", story_id)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao atualizar história: {exc}")
        return None


def update_story_media(
    client, story_id: str, image_url: Optional[str] = None, audio_url: Optional[str] = None
) -> Optional[Story]:
    """Atualiza campos de mídia de uma história específica, preservando os demais dados."""

    payload: Dict[str, Any] = {}

    if image_url is not None:
        payload["image_url"] = image_url
    if audio_url is not None:
        payload["audio_url"] = audio_url

    if not payload:
        return None

    try:
        response = (
            client.table("stories")
            .update(payload)
            .eq("id", story_id)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao atualizar mídia da história: {exc}")
        return None


def delete_story(client, story_id: str) -> bool:
    """Exclui uma história pelo id. Retorna True em sucesso."""

    try:
        client.table("stories").delete().eq("id", story_id).execute()
        return True
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao excluir história: {exc}")
        return False


def log_story_read(client, story_id: str, collection_id: Optional[str], source: str) -> bool:
    """Registra uma leitura no histórico, sem interromper a UI em caso de falha."""

    normalized_source = source if source in {"random", "manual"} else "manual"
    payload = {
        "story_id": story_id,
        "collection_id": collection_id,
        "source": normalized_source,
    }

    try:
        client.table("reading_log").insert(payload).execute()
        return True
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao registrar leitura: {exc}")
        return False


def get_recent_reads(client, limit: int = 20) -> List[Dict[str, Any]]:
    """Busca leituras recentes, tentando trazer título e coleção quando disponíveis."""

    try:
        response = (
            client.table("reading_log")
            .select("story_id,collection_id,source,created_at,stories(title),collections(name)")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        rows = response.data or []

        story_titles: Dict[str, str] = {}
        collection_names: Dict[str, str] = {}

        # Preenche mapas com dados aninhados (quando suportado)
        for row in rows:
            story_data = row.get("stories") or {}
            collection_data = row.get("collections") or {}
            if row.get("story_id") and story_data.get("title"):
                story_titles[row["story_id"]] = story_data.get("title")
            if row.get("collection_id") and collection_data.get("name"):
                collection_names[row["collection_id"]] = collection_data.get("name")

        # Busca títulos faltantes, caso a seleção aninhada não esteja habilitada
        missing_story_ids = {
            row.get("story_id")
            for row in rows
            if row.get("story_id") and row.get("story_id") not in story_titles
        }
        if missing_story_ids:
            stories_response = (
                client.table("stories")
                .select("id,title")
                .in_("id", list(missing_story_ids))
                .execute()
            )
            for story in stories_response.data or []:
                story_titles[story.get("id")] = story.get("title")

        missing_collection_ids = {
            row.get("collection_id")
            for row in rows
            if row.get("collection_id") and row.get("collection_id") not in collection_names
        }
        if missing_collection_ids:
            collections_response = (
                client.table("collections")
                .select("id,name")
                .in_("id", list(missing_collection_ids))
                .execute()
            )
            for col in collections_response.data or []:
                collection_names[col.get("id")] = col.get("name")

        formatted_rows: List[Dict[str, Any]] = []
        for row in rows:
            formatted_rows.append(
                {
                    "title": story_titles.get(row.get("story_id"), "—"),
                    "collection_name": collection_names.get(row.get("collection_id"), "—"),
                    "source": row.get("source"),
                    "created_at": row.get("created_at"),
                }
            )

        return formatted_rows
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao buscar histórico de leituras: {exc}")
        return []


def get_read_count_by_story(client) -> List[Dict[str, Any]]:
    """Retorna um ranking simples das histórias mais lidas."""

    try:
        response = client.table("reading_log").select("story_id").execute()
        rows = response.data or []
        counts: Dict[str, int] = {}
        for row in rows:
            story_id = row.get("story_id")
            if story_id:
                counts[story_id] = counts.get(story_id, 0) + 1

        if not counts:
            return []

        story_ids = list(counts.keys())
        titles: Dict[str, str] = {}
        stories_response = (
            client.table("stories").select("id,title").in_("id", story_ids).execute()
        )
        for story in stories_response.data or []:
            titles[story.get("id")] = story.get("title")

        ranking = [
            {
                "story_id": story_id,
                "title": titles.get(story_id, "História"),
                "read_count": count,
            }
            for story_id, count in counts.items()
        ]

        ranking.sort(key=lambda item: item.get("read_count", 0), reverse=True)
        return ranking
    except Exception as exc:  # pragma: no cover
        print(f"[Supabase] Erro ao montar ranking de leituras: {exc}")
        return []
