<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 dark:bg-black/60"
    @click.self="handleCancel"
  >
    <div class="bg-white border border-gray-200 dark:bg-gray-900 dark:border-gray-800 rounded-xl w-full max-w-md mx-4 overflow-hidden">
      <!-- 标题 -->
      <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-800">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ title }}</h3>
      </div>

      <!-- 内容 -->
      <div class="px-5 py-5 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
        {{ message }}
      </div>

      <!-- 按钮区 -->
      <div class="px-5 py-4 border-t border-gray-200 dark:border-gray-800 flex justify-end gap-3 bg-gray-50 dark:bg-transparent">
        <button
          @click="handleCancel"
          class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
        >
          {{ cancelText }}
        </button>
        <button
          @click="handleConfirm"
          :class="confirmButtonClass"
          class="px-4 py-2 text-sm rounded-lg font-medium transition"
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

const confirmButtonClass = computed(() => {
  if (confirmType.value === 'danger') {
    return 'bg-rose-600 hover:bg-rose-500 text-white'
  } else if (confirmType.value === 'warning') {
    return 'bg-amber-600 hover:bg-amber-500 text-white'
  } else {
    return 'bg-blue-600 hover:bg-blue-500 text-white'
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
