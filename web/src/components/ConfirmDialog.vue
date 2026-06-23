<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
    @click.self="handleCancel"
  >
    <div class="rounded-xl w-full max-w-md mx-4 overflow-hidden border shadow-xl"
         style="background: var(--card-bg); border-color: var(--card-border);">
      <!-- 标题 -->
      <div class="px-5 py-4 border-b" style="border-color: var(--card-border);">
        <h3 class="text-lg font-semibold" style="color: var(--text-strong);">{{ title }}</h3>
      </div>

      <!-- 内容 -->
      <div class="px-5 py-5 text-sm whitespace-pre-line" style="color: var(--page-text);">
        {{ message }}
      </div>

      <!-- 按钮区 -->
      <div class="px-5 py-4 border-t flex justify-end gap-3" style="border-color: var(--card-border); background: var(--secondary-bg);">
        <button
          @click="handleCancel"
          class="px-4 py-2 text-sm rounded-lg border transition"
          style="border-color: var(--field-border); color: var(--page-text);"
          @mouseover="e => e.target.style.background = 'var(--secondary-bg)'"
          @mouseout="e => e.target.style.background = ''"
        >
          {{ cancelText }}
        </button>
        <button
          @click="handleConfirm"
          class="px-4 py-2 text-sm rounded-lg font-medium text-white transition"
          :style="{ backgroundColor: confirmButtonStyle.bg }"
          @mouseover="e => e.target.style.backgroundColor = confirmButtonStyle.hover"
          @mouseout="e => e.target.style.backgroundColor = confirmButtonStyle.bg"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  confirmType: {
    type: String,
    default: 'danger'
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const visible = ref(false)
const title = ref('确认操作')
const message = ref('')
const confirmText = ref('确认')
const cancelText = ref('取消')
const confirmType = ref(props.confirmType)
const resolveFn = ref(null)

const confirmButtonStyle = computed(() => {
  if (confirmType.value === 'danger') {
    return { bg: '#e11d48', hover: '#be123c' }
  } else if (confirmType.value === 'warning') {
    return { bg: '#d97706', hover: '#b45309' }
  } else {
    return { bg: '#2563eb', hover: '#1d4ed8' }
  }
})

function show(options = {}) {
  return new Promise((resolve) => {
    title.value = options.title || '确认操作'
    message.value = options.message || ''
    confirmText.value = options.confirmText || '确认'
    cancelText.value = options.cancelText || '取消'
    confirmType.value = options.confirmType || 'danger'
    resolveFn.value = resolve
    visible.value = true
  })
}

function handleConfirm() {
  visible.value = false
  if (resolveFn.value) {
    resolveFn.value(true)
    resolveFn.value = null
  }
}

function handleCancel() {
  visible.value = false
  if (resolveFn.value) {
    resolveFn.value(false)
    resolveFn.value = null
  }
}

defineExpose({ show })
</script>