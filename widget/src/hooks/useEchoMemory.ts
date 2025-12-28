/**
 * Hook for persisting Echo interactions in browser storage (IndexedDB)
 */

import { useState, useEffect, useCallback } from 'react';
import { get, set, del, keys, createStore } from 'idb-keyval';
import type { EchoMemoryItem, EchoSource } from '../types';

// Custom store for Echo memory
const echoStore = createStore('echo-memory', 'interactions');

interface UseEchoMemoryReturn {
  memories: EchoMemoryItem[];
  isLoading: boolean;
  saveInteraction: (query: string, response: string, context?: {
    source?: EchoSource;
    patientId?: string;
    patientName?: string;
  }) => Promise<EchoMemoryItem>;
  deleteInteraction: (id: string) => Promise<void>;
  toggleStar: (id: string) => Promise<void>;
  addTag: (id: string, tag: string) => Promise<void>;
  removeTag: (id: string, tag: string) => Promise<void>;
  searchMemories: (query: string) => EchoMemoryItem[];
  getStarred: () => EchoMemoryItem[];
  clearAll: () => Promise<void>;
  refresh: () => Promise<void>;
}

export function useEchoMemory(): UseEchoMemoryReturn {
  const [memories, setMemories] = useState<EchoMemoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load all memories from IndexedDB
  const loadMemories = useCallback(async () => {
    setIsLoading(true);
    try {
      const allKeys = await keys(echoStore);
      const items: EchoMemoryItem[] = [];

      for (const key of allKeys) {
        const item = await get<EchoMemoryItem>(key, echoStore);
        if (item) {
          // Ensure date is properly parsed
          item.timestamp = new Date(item.timestamp);
          items.push(item);
        }
      }

      // Sort by timestamp, newest first
      items.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      setMemories(items);
    } catch (err) {
      console.error('Failed to load Echo memories:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load on mount
  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  const saveInteraction = useCallback(async (
    query: string,
    response: string,
    context?: {
      source?: EchoSource;
      patientId?: string;
      patientName?: string;
    }
  ): Promise<EchoMemoryItem> => {
    const item: EchoMemoryItem = {
      id: crypto.randomUUID(),
      timestamp: new Date(),
      query,
      response,
      context: context ? {
        source: context.source || 'unknown',
        patientId: context.patientId,
        patientName: context.patientName,
      } : undefined,
      tags: [],
      starred: false,
    };

    await set(item.id, item, echoStore);
    setMemories(prev => [item, ...prev]);
    return item;
  }, []);

  const deleteInteraction = useCallback(async (id: string) => {
    await del(id, echoStore);
    setMemories(prev => prev.filter(m => m.id !== id));
  }, []);

  const toggleStar = useCallback(async (id: string) => {
    const item = await get<EchoMemoryItem>(id, echoStore);
    if (item) {
      item.starred = !item.starred;
      await set(id, item, echoStore);
      setMemories(prev => prev.map(m => m.id === id ? { ...m, starred: item.starred } : m));
    }
  }, []);

  const addTag = useCallback(async (id: string, tag: string) => {
    const item = await get<EchoMemoryItem>(id, echoStore);
    if (item) {
      item.tags = [...new Set([...(item.tags || []), tag])];
      await set(id, item, echoStore);
      setMemories(prev => prev.map(m => m.id === id ? { ...m, tags: item.tags } : m));
    }
  }, []);

  const removeTag = useCallback(async (id: string, tag: string) => {
    const item = await get<EchoMemoryItem>(id, echoStore);
    if (item) {
      item.tags = (item.tags || []).filter(t => t !== tag);
      await set(id, item, echoStore);
      setMemories(prev => prev.map(m => m.id === id ? { ...m, tags: item.tags } : m));
    }
  }, []);

  const searchMemories = useCallback((query: string): EchoMemoryItem[] => {
    const lower = query.toLowerCase();
    return memories.filter(m =>
      m.query.toLowerCase().includes(lower) ||
      m.response.toLowerCase().includes(lower) ||
      m.tags?.some(t => t.toLowerCase().includes(lower))
    );
  }, [memories]);

  const getStarred = useCallback((): EchoMemoryItem[] => {
    return memories.filter(m => m.starred);
  }, [memories]);

  const clearAll = useCallback(async () => {
    const allKeys = await keys(echoStore);
    for (const key of allKeys) {
      await del(key, echoStore);
    }
    setMemories([]);
  }, []);

  return {
    memories,
    isLoading,
    saveInteraction,
    deleteInteraction,
    toggleStar,
    addTag,
    removeTag,
    searchMemories,
    getStarred,
    clearAll,
    refresh: loadMemories,
  };
}
