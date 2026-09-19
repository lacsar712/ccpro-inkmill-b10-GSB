<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { api } from '../lib/api';
  import type { RecentMillEvent } from '../lib/types';

  export let open = false;

  const dispatch = createEventDispatcher<{
    close: void;
    navigate: { page: 'mills' | 'samples' | 'passes' };
  }>();

  let rows: RecentMillEvent[] = [];
  let loading = false;
  let error = '';

  const actionLabels: Record<string, string> = {
    'mill.created': '新增研磨机',
    'mill.updated': '更新研磨机',
    'mill.deleted': '删除研磨机',
    'sample.created': '新增取样',
    'sample.updated': '更新取样',
    'sample.deleted': '删除取样',
    'pass.created': '新增遍次',
    'pass.updated': '更新遍次',
    'pass.deleted': '删除遍次',
  };

  async function load() {
    loading = true;
    error = '';
    try {
      rows = await api<RecentMillEvent[]>('/recent-mill-events');
    } catch (e) {
      error = e instanceof Error ? e.message : '加载失败';
    } finally {
      loading = false;
    }
  }

  // 每次打开抽屉都拉取最近事件
  $: if (open) load();

  function targetPage(action: string): 'mills' | 'samples' | 'passes' | null {
    if (action.startsWith('mill.')) return 'mills';
    if (action.startsWith('sample.')) return 'samples';
    if (action.startsWith('pass.')) return 'passes';
    return null;
  }

  function pick(row: RecentMillEvent) {
    const page = targetPage(row.action);
    if (!page) return;
    dispatch('navigate', { page });
  }
</script>

{#if open}
  <button class="scrim" aria-label="关闭" on:click={() => dispatch('close')}></button>
  <aside class="drawer" role="dialog" aria-label="最近事件">
    <div class="drawer-head">
      <div>
        <h2>最近事件</h2>
        <span class="hint">仅显示最近 20 条</span>
      </div>
      <div class="head-ops">
        <button class="icon-btn" title="刷新" on:click={load}>刷新</button>
        <button class="icon-btn" title="关闭" on:click={() => dispatch('close')}>×</button>
      </div>
    </div>

    <div class="drawer-body">
      {#if loading}
        <div class="state">加载中…</div>
      {:else if error}
        <div class="state err">{error}</div>
      {:else if rows.length === 0}
        <div class="state">暂无事件</div>
      {:else}
        <ul>
          {#each rows as row (row.id)}
            {@const page = targetPage(row.action)}
            <li>
              <button
                class="event"
                class:linkable={!!page}
                disabled={!page}
                on:click={() => pick(row)}
              >
                <span class="tag">{actionLabels[row.action] || row.action}</span>
                <span class="summary">{row.summary}</span>
                <span class="meta">
                  {row.actorName || '未知用户'} · {row.createdAt}
                </span>
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  </aside>
{/if}

<style>
  .scrim {
    position: fixed;
    inset: 0;
    z-index: 40;
    border: none;
    background: rgba(0, 0, 0, 0.5);
  }

  .drawer {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    z-index: 41;
    width: min(380px, 92vw);
    display: flex;
    flex-direction: column;
    background: var(--ink-900);
    border-left: 1px solid var(--line);
    box-shadow: -12px 0 40px rgba(0, 0, 0, 0.55);
  }

  .drawer-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.1rem;
    border-bottom: 1px solid var(--line);
  }

  .drawer-head h2 {
    margin: 0;
    font-family: var(--font-display);
    letter-spacing: 0.06em;
    font-size: 1.15rem;
  }

  .hint {
    font-size: 0.72rem;
    color: var(--steel);
  }

  .head-ops {
    display: flex;
    gap: 0.4rem;
  }

  .icon-btn {
    border: 1px solid var(--line);
    background: transparent;
    color: var(--steel);
    padding: 0.3rem 0.6rem;
    cursor: pointer;
  }

  .icon-btn:hover {
    border-color: var(--vermillion-700);
    color: white;
  }

  .drawer-body {
    flex: 1;
    overflow: auto;
    padding: 0.6rem 0.8rem 1rem;
  }

  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .event {
    width: 100%;
    text-align: left;
    display: grid;
    gap: 0.3rem;
    padding: 0.65rem 0.7rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--line);
    color: var(--mist);
    cursor: default;
  }

  .event.linkable {
    cursor: pointer;
  }

  .event.linkable:hover {
    border-color: var(--vermillion-700);
    background: rgba(192, 57, 43, 0.08);
  }

  .tag {
    justify-self: start;
    font-size: 0.72rem;
    color: var(--vermillion-400);
    border: 1px solid rgba(231, 76, 60, 0.35);
    padding: 0.05rem 0.4rem;
  }

  .summary {
    font-size: 0.9rem;
  }

  .meta {
    font-size: 0.72rem;
    color: var(--steel);
  }

  .state {
    padding: 1.5rem 0.5rem;
    text-align: center;
    color: var(--steel);
    font-size: 0.85rem;
  }

  .state.err {
    color: var(--vermillion-400);
  }
</style>
