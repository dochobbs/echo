"""Supabase client for Echo."""

from functools import lru_cache
from typing import Optional

from supabase import create_client, Client

from ..config import get_settings


@lru_cache
def get_supabase_client() -> Client:
  """Get cached Supabase client."""
  settings = get_settings()
  if not settings.supabase_url or not settings.supabase_anon_key:
    raise RuntimeError(
      "Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY."
    )
  return create_client(settings.supabase_url, settings.supabase_anon_key)


@lru_cache
def get_supabase_admin() -> Client:
  """Get Supabase client with service role key for admin operations."""
  settings = get_settings()
  if not settings.supabase_url or not settings.supabase_service_key:
    raise RuntimeError(
      "Supabase admin not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY."
    )
  return create_client(settings.supabase_url, settings.supabase_service_key)
