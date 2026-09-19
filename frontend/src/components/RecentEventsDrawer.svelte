<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { api } from '../lib/api';
  import type { RecentMillEvent } from '../lib/types';

  export let open = false;

  const dispatch = createEventDispatcher<{ close: void; navigate: string }>();

  let rows: RecentMillEvent[] = [];
  let loading = false;
  let error = '';
  let loaded = false;

  async function load() {
    loading = true;
    error = '';
    try {
      rows = await api<RecentMillEvent[]>('/recent-mill-events');
      loaded = true;
    } catch (e) {
      error = e instanceof Error ? e.message : '加载失败';
    } finally {
      loading = false;
    }
  }

  // 每次打开时拉取最新 20 条（仅依赖 open，避免 loading 变化反复触发）
  $: if (open) load();

  function pageFor(action: string): string {
    if (action.startsWith('sample.')) return 'samples';
    if (action.startsWith('pass.')) return 'passes';
    return 'mills';
  }

  function pick(row: RecentMillEvent) {
    dispatch('navigate', pageFor(row.action));
    dispatch('close');
  }

  const kindLabel: Record<string, string> = {
    mill: '机台',
    sample: '粘度',
    pass: '遍次',
  };

  function kind(action: string): string {
    return kindLabel[action.split('.')[0]] || '事件';
  }
</script>

{#if open}
  <button class="backdrop" aria-label="关闭" on:click={() => dispatch('close')}></button>
  <aside class="drawer" aria-label="最近事件">
    <header>
      <div>
        <h2>最近事件</h2>
        <p class="hint">最近 20 条机台操作流水</p>
      </div>
      <button class="x" on:click={() => dispatch('close')}>×</button>
    </header>

    <div class="body">
      {#if loading && !loaded}
        <div class="muted">加载中…</div>
      {:else if error}
        <div class="err">{error}</div>
      {:else if rows.length === 0}
        <div class="muted empty">暂无事件</div>
      {:else}
        <ul>
          {#each rows as row (row.id)}
            <li>
              <button class="item" on:click={() => pick(row)}>
                <span class="tag">{kind(row.action)}</span>
                <span class="content">
                  <span class="summary">{row.summary}</span>
                  <span class="meta">
                    {row.actorName || '未知操作人'} · {row.createdAt}
                  </span>
                </span>
                <span class="go">→</span>
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  </aside>
{/if}

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    padding: 0;
    border: none;
    background: rgba(0, 0, 0, 0.55);
    z-index: 40;
  }

  .drawer {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: min(380px, 92vw);
    z-index: 41;
    display: flex;
    flex-direction: column;
    background: linear-gradient(180deg, var(--ink-900), var(--ink-950));
    border-left: 1px solid var(--line);
    box-shadow: -12px 0 40px rgba(0, 0, 0, 0.55);
    animation: slide-in 0.18s ease;
  }

  @keyframes slide-in {
    from {
      transform: translateX(24px);
      opacity: 0.4;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 1.1rem 1.1rem 0.9rem;
    border-bottom: 1px solid var(--line);
  }

  h2 {
    margin: 0;
    font-family: var(--font-display);
    letter-spacing: 0.06em;
    font-size: 1.15rem;
  }

  .hint {
    margin: 0.2rem 0 0;
    font-size: 0.78rem;
    color: var(--steel);
  }

  .x {
    background: none;
    border: none;
    color: var(--steel);
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
    padding: 0 0.2rem;
  }

  .x:hover {
    color: white;
  }

  .body {
    overflow-y: auto;
    padding: 0.5rem 0.6rem 1rem;
    flex: 1;
  }

  ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .item {
    width: 100%;
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.65rem;
    align-items: start;
    text-align: left;
    background: none;
    border: 1px solid transparent;
    padding: 0.65rem 0.55rem;
    cursor: pointer;
    color: var(--mist);
  }

  .item:hover {
    background: rgba(192, 57, 43, 0.12);
    border-color: var(--line);
  }

  .item:hover .go {
    color: var(--vermillion-400);
  }

  .tag {
    margin-top: 0.1rem;
    font-size: 0.7rem;
    color: var(--vermillion-400);
    border: 1px solid rgba(231, 76, 60, 0.4);
    border-radius: 2px;
    padding: 0.1rem 0.4rem;
    white-space: nowrap;
  }

  .content {
    display: grid;
    gap: 0.25rem;
    min-width: 0;
  }

  .summary {
    font-size: 0.9rem;
    line-height: 1.4;
    word-break: break-word;
  }

  .meta {
    font-size: 0.75rem;
    color: var(--steel);
  }

  .go {
    color: var(--steel);
    font-size: 0.95rem;
  }

  .empty {
    padding: 2rem 0;
    text-align: center;
  }

  .err {
    color: var(--vermillion-400);
    padding: 0.5rem;
  }
</style>
