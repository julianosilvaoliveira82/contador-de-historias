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
            .select("id,title,body,image_url,audio_url,duration_seconds,sort_order")
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
            .select("id,title,body,image_url,audio_url,duration_seconds,sort_order")
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
                "duration_seconds,created_at,updated_at"
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
