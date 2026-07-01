<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="handleCancel"
      >
        <Transition name="dialog-pop" appear>
          <div
            v-if="visible"
            class="w-full max-w-md rounded-2xl border shadow-2xl overflow-hidden"
            style="background: var(--card-bg); border-color: var(--card-border);"
          >
            <!-- Title with icon -->
            <div class="px-6 py-4 border-b flex items-center gap-3" style="border-color: var(--card-border);">
              <!-- Icon by mode -->
              <div v-if="mode === 'confirm'"
                class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
                :style="{ backgroundColor: titleIconBg }">
                <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 9v4M12 17h.01M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                </svg>
              </div>
              <div v-else-if="mode === 'phone-send'"
                class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center" style="background-color: #7c3aed;">
                <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.36 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.34 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
              </div>
              <div v-else-if="mode === 'phone-code'"
                class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center" style="background-color: #7c3aed;">
                <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12l2 2 4-4M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z"/>
                </svg>
              </div>
              <h3 class="text-lg font-semibold flex-1" style="color: var(--text-strong);">{{ title }}</h3>
            </div>

            <!-- Mode: confirm (default) -->
            <div v-if="mode === 'confirm'" class="px-6 py-5 text-sm leading-relaxed whitespace-pre-line" style="color: var(--page-text);">
              {{ message }}
            </div>

            <!-- Mode: phone-send -->
            <div v-else-if="mode === 'phone-send'" class="px-6 py-5">
              <p class="text-sm mb-4" style="color: var(--page-text);">选择发送验证码的方式：</p>
              <div v-if="phoneNumber"
                class="flex items-center gap-2 mb-5 px-4 py-2.5 rounded-xl border"
                style="border-color: var(--card-border); background: var(--secondary-bg);">
                <svg class="w-4 h-4 flex-shrink-0" style="color: var(--page-text);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="5" y="2" width="14" height="20" rx="2"/>
                  <line x1="12" y1="18" x2="12" y2="18"/>
                </svg>
                <span class="text-sm font-mono tracking-wide" style="color: var(--text-strong);">{{ phoneNumber }}</span>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <button
                  @click="handlePhoneSelect('sms')"
                  class="group flex flex-col items-center justify-center gap-1.5 px-4 py-4 rounded-xl border-2 transition-all text-sm font-medium"
                  style="border-color: var(--card-border); color: var(--page-text);"
                  @mouseover="e => { e.currentTarget.style.background = 'var(--secondary-bg)'; e.currentTarget.style.borderColor = '#a78bfa' }"
                  @mouseout="e => { e.currentTarget.style.background = ''; e.currentTarget.style.borderColor = 'var(--card-border)' }"
                >
                  <svg class="w-6 h-6 transition-colors group-hover:text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                  短信
                </button>
                <button
                  @click="handlePhoneSelect('whatsapp')"
                  class="group flex flex-col items-center justify-center gap-1.5 px-4 py-4 rounded-xl border-2 transition-all text-sm font-medium"
                  style="border-color: var(--card-border); color: var(--page-text);"
                  @mouseover="e => { e.currentTarget.style.background = 'var(--secondary-bg)'; e.currentTarget.style.borderColor = '#25D366' }"
                  @mouseout="e => { e.currentTarget.style.background = ''; e.currentTarget.style.borderColor = 'var(--card-border)' }"
                >
                  <svg class="w-6 h-6 transition-colors" style="color: #25D366;" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 2.99.97 4.29L1 23l6.84-1.9c1.25.55 2.66.9 4.16.9 5.52 0 10-4.48 10-10S17.52 2 12 2z"/>
                  </svg>
                  WhatsApp
                </button>
              </div>
            </div>

            <!-- Mode: phone-code -->
            <div v-else-if="mode === 'phone-code'" class="px-6 py-5">
              <div v-if="phoneNumber"
                class="flex items-center justify-center gap-2 mb-4 text-sm"
                style="color: var(--page-text);">
                <svg class="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="5" y="2" width="14" height="20" rx="2"/>
                  <line x1="12" y1="18" x2="12" y2="18"/>
                </svg>
                {{ phoneNumber }}
              </div>
              <p class="text-sm mb-3" style="color: var(--page-text);">请输入收到的验证码：</p>
              <input
                ref="codeInput"
                v-model="phoneCode"
                type="text"
                inputmode="numeric"
                placeholder="— — — —"
                maxlength="10"
                class="w-full px-4 py-3 text-lg text-center tracking-[0.3em] rounded-xl border-2 outline-none transition-colors"
                style="background: var(--secondary-bg); border-color: var(--card-border); color: var(--text-strong);"
                @focus="e => e.target.style.borderColor = '#a78bfa'"
                @blur="e => e.target.style.borderColor = 'var(--card-border)'"
                @keyup.enter="handlePhoneCodeSubmit"
              />
              <div v-if="phoneInvalid" class="mt-2 text-sm text-red-400 text-center flex items-center justify-center gap-1">
                <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12" y2="16"/>
                </svg>
                验证码无效，请重新输入（{{ phoneAttempts }}/3）
              </div>
            </div>

            <!-- Footer -->
            <div class="px-6 py-4 border-t flex justify-end gap-3"
                 style="border-color: var(--card-border); background: var(--secondary-bg);">
              <button
                @click="handleCancel"
                class="px-4 py-2 text-sm rounded-lg border transition"
                style="border-color: var(--card-border); color: var(--page-text);"
                @mouseover="e => e.target.style.background = 'var(--card-bg)'"
                @mouseout="e => e.target.style.background = ''"
              >
                {{ cancelText }}
              </button>
              <button
                v-if="mode === 'confirm'"
                @click="handleConfirm"
                class="px-5 py-2 text-sm rounded-lg font-medium text-white transition shadow-sm"
                :style="{ backgroundColor: confirmButtonStyle.bg }"
                @mouseover="e => e.target.style.backgroundColor = confirmButtonStyle.hover"
                @mouseout="e => e.target.style.backgroundColor = confirmButtonStyle.bg"
              >
                {{ confirmText }}
              </button>
              <button
                v-else-if="mode === 'phone-code'"
                @click="handlePhoneCodeSubmit"
                :disabled="!phoneCode.trim()"
                class="px-5 py-2 text-sm rounded-lg font-medium text-white transition shadow-sm"
                style="background-color: #7c3aed;"
                :style="{ opacity: phoneCode.trim() ? 1 : 0.4, cursor: phoneCode.trim() ? 'pointer' : 'not-allowed' }"
                @mouseover="e => { if(phoneCode.trim()) e.target.style.backgroundColor = '#6d28d9' }"
                @mouseout="e => { if(phoneCode.trim()) e.target.style.backgroundColor = '#7c3aed' }"
              >
                确定
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  confirmType: {
    type: String,
    default: 'danger'
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const visible = ref(false)
const mode = ref('confirm')
const title = ref('确认操作')
const message = ref('')
const confirmText = ref('确认')
const cancelText = ref('取消')
const confirmType = ref(props.confirmType)
const resolveFn = ref(null)

const phoneNumber = ref('')
const phoneCode = ref('')
const phoneInvalid = ref(false)
const phoneAttempts = ref(0)
const codeInput = ref(null)

const confirmButtonStyle = computed(() => {
  if (confirmType.value === 'danger') {
    return { bg: '#e11d48', hover: '#be123c' }
  } else if (confirmType.value === 'warning') {
    return { bg: '#d97706', hover: '#b45309' }
  } else {
    return { bg: '#2563eb', hover: '#1d4ed8' }
  }
})

const titleIconBg = computed(() => {
  if (confirmType.value === 'danger') return '#e11d48'
  if (confirmType.value === 'warning') return '#d97706'
  return '#2563eb'
})

// --- Mode: confirm ---
function show(options = {}) {
  return new Promise((resolve) => {
    mode.value = 'confirm'
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
    if (mode.value === 'confirm') {
      resolveFn.value(false)
    } else {
      resolveFn.value({ action: 'cancel' })
    }
    resolveFn.value = null
  }
}

// --- Mode: phone-send ---
function showPhoneSend(phone = '') {
  return new Promise((resolve) => {
    mode.value = 'phone-send'
    title.value = '发送验证码'
    phoneNumber.value = phone || ''
    cancelText.value = '取消'
    resolveFn.value = resolve
    visible.value = true
  })
}

function handlePhoneSelect(method) {
  visible.value = false
  if (resolveFn.value) {
    resolveFn.value({ action: 'send', method })
    resolveFn.value = null
  }
}

// --- Mode: phone-code ---
function showPhoneCode(phone = '', currentAttempts = 0, isInvalid = false) {
  return new Promise((resolve) => {
    mode.value = 'phone-code'
    title.value = '输入验证码'
    phoneNumber.value = phone || ''
    phoneCode.value = ''
    phoneInvalid.value = isInvalid
    phoneAttempts.value = currentAttempts
    cancelText.value = '取消'
    resolveFn.value = resolve
    visible.value = true
    nextTick(() => {
      codeInput.value?.focus()
    })
  })
}

function handlePhoneCodeSubmit() {
  const trimmed = phoneCode.value.trim()
  if (!trimmed) return
  visible.value = false
  if (resolveFn.value) {
    resolveFn.value({ action: 'submit', code: trimmed })
    resolveFn.value = null
  }
}

defineExpose({ show, showPhoneSend, showPhoneCode })
</script>

<style scoped>
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.2s ease;
}
.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-pop-enter-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.dialog-pop-leave-active {
  transition: transform 0.15s ease, opacity 0.15s ease;
}
.dialog-pop-enter-from {
  transform: scale(0.92) translateY(-20px);
  opacity: 0;
}
.dialog-pop-leave-to {
  transform: scale(0.95);
  opacity: 0;
}
</style>
