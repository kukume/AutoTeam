<template>
  <!-- 桌面端侧边栏 -->
  <nav class="hidden h-screen w-72 shrink-0 flex-col border-r border-white/10 bg-slate-950/65 p-5 md:flex">
    <div class="mb-4 flex items-center gap-3 pb-4 border-b border-white/5">
      <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500/30 to-cyan-500/20 text-2xl shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
        ⚡
      </div>
      <div class="min-w-0 flex-1">
        <h1 class="text-lg font-semibold tracking-tight text-white">AutoTeam</h1>
        <p class="mt-0.5 text-xs text-slate-400">账号轮转管理中心</p>
      </div>
      <ThemeToggle />
    </div>

    <div class="flex-1 space-y-2 overflow-y-auto sidebar-scroll">
      <a v-for="item in items" :key="item.key"
        :href="item.path"
        @click.prevent="$emit('navigate', item.key)"
        class="group flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-left transition"
        :class="active === item.key
          ? 'bg-blue-500/15 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] ring-1 ring-blue-400/20'
          : 'text-slate-400 hover:bg-white/5 hover:text-white'"
      >
        <span
          class="flex h-11 w-11 items-center justify-center rounded-2xl border text-lg transition"
          :class="active === item.key
            ? 'border-blue-400/20 bg-blue-500/15 text-blue-200'
            : 'border-white/10 bg-white/5 text-slate-300 group-hover:border-white/20 group-hover:bg-white/10'"
        >
          {{ item.icon }}
        </span>
        <span class="min-w-0 flex-1">
          <span class="block text-sm font-medium">{{ item.label }}</span>
          <span class="mt-0.5 block text-xs text-slate-500 group-hover:text-slate-400">{{ item.hint }}</span>
        </span>
      </a>
    </div>

    <div class="mt-2 space-y-2 border-t border-white/10 pt-5">
      <button @click="$emit('refresh')" :disabled="loading"
        class="btn-secondary w-full justify-start gap-3 rounded-2xl px-3 py-3 text-left disabled:opacity-50">
        <span class="text-base">🔄</span>
        {{ loading ? '刷新中...' : '刷新数据' }}
      </button>
      <button v-if="authRequired" @click="$emit('logout')"
        class="btn-danger w-full justify-start gap-3 rounded-2xl px-3 py-3 text-left">
        <span class="text-base">🚪</span>
        登出
      </button>
    </div>
  </nav>

  <!-- 移动端底部 tab 栏 -->
  <nav class="fixed bottom-3 left-3 right-3 z-50 flex rounded-3xl border border-white/10 bg-slate-950/80 p-1.5 shadow-[0_20px_40px_-20px_rgba(15,23,42,0.9)] backdrop-blur-2xl md:hidden">
    <a v-for="item in items" :key="item.key"
      :href="item.path"
      @click.prevent="$emit('navigate', item.key)"
      class="flex-1 rounded-2xl px-1 py-2 text-xs transition"
      :class="active === item.key
        ? 'bg-blue-500/15 text-blue-300'
        : 'text-slate-500'">
      <div class="flex flex-col items-center">
        <span class="text-lg">{{ item.icon }}</span>
        <span class="mt-0.5">{{ item.mobileLabel || item.label }}</span>
      </div>
    </a>
  </nav>
</template>

<script setup>
import { ROUTES as items } from '../routes.js'
import ThemeToggle from './ThemeToggle.vue'
defineProps({
  active: String,
  loading: Boolean,
  authRequired: Boolean,
})
defineEmits(['navigate', 'refresh', 'logout'])
</script>

<style scoped>
.sidebar-scroll {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.sidebar-scroll::-webkit-scrollbar {
  display: none;
}
</style>
