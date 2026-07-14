<template>
  <div class="mt-6 space-y-6">
    <div class="glass-card p-4">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="item in visualCategories"
          :key="item.key"
          @click="visualCategory = item.key"
          class="pill-tab flex items-center gap-2"
          :class="visualCategory === item.key
            ? 'pill-tab-active'
            : ''"
        >
          <span class="text-base">{{ item.icon }}</span>
          {{ item.label }}
        </button>
      </div>
    </div>

    <div
      v-if="selectedRuntimeCategory"
      class="glass-card p-5"
    >
      <div class="mb-4 flex items-center justify-between gap-3">
        <h2 class="text-lg font-semibold text-white">{{ currentRuntimeCategoryMeta?.title }}</h2>
        <span
          v-if="runtimeSaved"
          class="text-xs text-green-400"
        >已保存</span>
      </div>

      <div
        v-if="runtimeMessage"
        class="mb-4 rounded-2xl px-4 py-3 text-sm border"
        :class="runtimeMessageClass"
      >
        {{ runtimeMessage }}
      </div>

      <div v-if="runtimeLoading" class="text-sm text-slate-400">
        正在加载当前配置...
      </div>

      <div v-else-if="selectedRuntimeCategory === 'cloudmail'" class="space-y-4">
        <div class="flex items-center justify-between gap-3">
          <p class="text-xs text-slate-500">
            可同时添加多个 CloudMail / Cloudflare Temp Email 实例；默认服务用于新建账号。
          </p>
          <div class="flex flex-wrap gap-2">
            <button class="btn-secondary" @click="addMailService('cloudmail')">
              + 添加 CloudMail
            </button>
            <button class="btn-secondary" @click="addMailService('cloudflare_temp_email')">
              + 添加 Cloudflare Temp Email
            </button>
          </div>
        </div>

        <div
          v-if="!mailServices.length"
          class="rounded-2xl border border-dashed border-white/10 bg-white/5 px-4 py-5 text-sm text-slate-400"
        >
          还没有配置任何邮箱服务。先添加一个服务，再设置为默认服务。
        </div>

        <div
          v-for="service in mailServices"
          :key="service.id"
          class="rounded-lg border border-gray-800 bg-gray-800/60 p-3"
        >
          <div class="mb-3 flex flex-wrap items-center gap-2">
            <div class="text-sm font-medium text-white">{{ mailServiceCardTitle(service) }}</div>
            <span class="status-badge text-[11px] text-slate-300">
              {{ mailServiceTypeLabel(service.type) }}
            </span>
            <span
              v-if="mailServiceDefault === service.id"
              class="status-badge border-emerald-400/20 bg-emerald-500/10 text-[11px] text-emerald-200"
            >
              默认新建服务
            </span>
            <span
              v-if="!isMailServiceComplete(service)"
              class="status-badge border-amber-400/20 bg-amber-500/10 text-[11px] text-amber-200"
            >
              待补全
            </span>
            <div class="ml-auto flex flex-wrap gap-2">
              <button
                v-if="mailServiceDefault !== service.id"
                class="btn-secondary"
                @click="setDefaultMailService(service.id)"
              >
                设为默认
              </button>
              <button
                class="btn-secondary border-red-500/30 text-red-300 hover:border-red-400/40 hover:text-red-200"
                @click="removeMailService(service.id)"
              >
                删除
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <div>
              <label class="mb-1 block text-sm text-slate-400">
                服务名称<span class="ml-1 text-xs text-slate-600">（可选）</span>
              </label>
              <input
                v-model="service.name"
                type="text"
                placeholder="例如：CloudMail #1"
                class="input-dark"
              />
            </div>

            <div
              v-for="field in mailServiceFields(service)"
              :key="`${service.id}-${field.key}`"
            >
              <label class="mb-1 block text-sm text-slate-400">
                {{ field.label }}<span v-if="field.required" class="text-red-400">*</span>
              </label>
              <input
                v-model="service[field.key]"
                :type="field.inputType || 'text'"
                :placeholder="field.inputType === 'password' ? '留空则不修改' : (field.placeholder || '')"
                class="input-dark"
              />
              <div v-if="field.hint" class="mt-1 text-[11px] text-slate-500 break-all">
                {{ field.hint }}
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between gap-3">
          <p class="text-xs text-slate-500">
            保存后立即热加载；已有账号按 `mail_service_id` 或唯一邮箱域名匹配服务。
          </p>
          <button
            @click="saveRuntimeConfig"
            :disabled="runtimeSaving || runtimeLoading"
            class="btn-primary"
          >
            {{ runtimeSaving ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>

      <div v-else-if="selectedRuntimeCategory === 'sync'" class="space-y-4">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <div v-for="field in syncCpaFields" :key="field.key">
            <label class="mb-1 block text-sm text-slate-400">
              {{ field.prompt }}<span v-if="isRuntimeRequired(field)" class="text-red-400">*</span>
            </label>
            <input
              v-model="runtimeForm[field.key]"
              :type="fieldInputType(field.key)"
              :placeholder="fieldPlaceholder(field.key, field.default)"
              class="input-dark"
            />
          </div>
        </div>

        <div class="flex items-center justify-between gap-3">
          <p class="text-xs text-slate-500">
            保存后立即热加载；账号池操作按当前已启用远端决定后续同步行为。
          </p>
          <button
            @click="saveRuntimeConfig"
            :disabled="runtimeSaving || runtimeLoading"
            class="btn-primary"
          >
            {{ runtimeSaving ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>

      <div v-else-if="selectedRuntimeCategory === 'proxy'" class="space-y-4">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <div v-for="field in proxyProxyFields" :key="field.key">
            <label class="mb-2 block text-sm text-slate-400">
              {{ field.prompt }}<span v-if="isRuntimeRequired(field)" class="text-red-400">*</span>
            </label>
            <input
              v-model="runtimeForm[field.key]"
              :type="fieldInputType(field.key)"
              :placeholder="fieldPlaceholder(field.key, field.default)"
              class="input-dark"
            />
          </div>
        </div>

        <div>
          <label class="mb-2 block text-sm text-slate-400">
            {{ fieldByKey('PHONE_OTP_AUTO_SEND')?.prompt || '自动发送手机验证码' }}
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="opt in phoneOtpAutoSendOptions"
              :key="opt.value"
              @click="runtimeForm['PHONE_OTP_AUTO_SEND'] = opt.value"
              class="pill-tab"
              :class="runtimeForm['PHONE_OTP_AUTO_SEND'] === opt.value ? 'pill-tab-active' : ''"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <div class="flex items-center justify-between gap-3">
          <p class="text-xs text-slate-500">
            仅在需要代理 Playwright 浏览器流量时启用，并配合绕过列表避免本地回调误走代理。
          </p>
          <button
            @click="saveRuntimeConfig"
            :disabled="runtimeSaving || runtimeLoading"
            class="btn-primary"
          >
            {{ runtimeSaving ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>

      <div v-else class="space-y-4">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <div v-for="field in currentRuntimeFields" :key="field.key">
            <label class="mb-1 block text-sm text-slate-400">
              {{ field.prompt }}<span v-if="isRuntimeRequired(field)" class="text-red-400">*</span>
            </label>
            <input
              v-model="runtimeForm[field.key]"
              :type="fieldInputType(field.key)"
              :placeholder="fieldPlaceholder(field.key, field.default)"
              class="input-dark"
            />
          </div>
        </div>

        <div class="flex items-center justify-between gap-3">
          <p class="text-xs text-slate-500">
            {{ currentRuntimeCategoryMeta?.footer }}
          </p>
          <button
            @click="saveRuntimeConfig"
            :disabled="runtimeSaving || runtimeLoading"
            class="btn-primary"
          >
            {{ runtimeSaving ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>
    </div>

    <Settings
      v-else-if="visualCategory === 'admin'"
      :admin-status="adminStatus"
      section="admin"
      @refresh="$emit('refresh')"
      @admin-progress="$emit('admin-progress')"
    />

    <Settings
      v-else-if="visualCategory === 'auto-check'"
      :admin-status="adminStatus"
      section="auto-check"
      @refresh="$emit('refresh')"
      @admin-progress="$emit('admin-progress')"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { api } from '../api.js'
import Settings from './Settings.vue'

defineProps({
  adminStatus: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['refresh', 'admin-progress'])

const runtimeCategoryKeys = {
  cloudmail: ['MAIL_PROVIDER', 'CLOUDMAIL_BASE_URL', 'CLOUDMAIL_EMAIL', 'CLOUDMAIL_PASSWORD', 'CLOUDMAIL_DOMAIN', 'CF_TEMP_EMAIL_BASE_URL', 'CF_TEMP_EMAIL_ADMIN_PASSWORD', 'CF_TEMP_EMAIL_DOMAIN'],
  sync: [
    'CPA_URL',
    'CPA_KEY',
  ],
  proxy: ['PLAYWRIGHT_PROXY_URL', 'PLAYWRIGHT_PROXY_BYPASS', 'PHONE_OTP_AUTO_SEND'],
}

const runtimeCategoryMeta = {
  cloudmail: {
    icon: '📧',
    badge: 'Mail Services',
    title: '邮箱服务配置',
    description: '配置自动注册和收验证码所需的邮箱后端。现在支持同时维护多个 CloudMail / Cloudflare Temp Email 实例，并指定默认新建服务。',
    note: '已有账号会优先按账号自身保存的 mail_service_id 或唯一邮箱域名匹配服务；存在歧义时不会盲猜。',
    footer: '邮箱服务配置保存后会立即热加载；之后的新建、复用和验证码轮询都会按最新服务列表执行。',
  },
  sync: {
    icon: '☁️',
    badge: 'Remote Sync',
    title: '远端同步',
    description: '填写 CPA 远端连接地址和管理密钥。配置后会自动同步到已启用的远端。',
    note: 'Account pool operations sync to all configured remotes automatically.',
  },
  proxy: {
    icon: '🛰️',
    badge: 'Proxy / Advanced',
    title: '代理 / 高级',
    description: '用于单独配置 Playwright 浏览器流量代理。属于低频项，默认折叠，避免把主配置界面堆得过满。',
    note: '只有在代理 ChatGPT / Auth 页面访问时才建议配置；本地回调场景通常还需要设置 bypass。',
  },
}

const visualCategories = [
  { key: 'cloudmail', label: '邮箱服务', icon: '📧' },
  { key: 'sync', label: '远端同步', icon: '☁️' },
  { key: 'admin', label: '管理员 / 主号', icon: '👤' },
  { key: 'auto-check', label: '巡检设置', icon: '🔄' },
  { key: 'proxy', label: '代理 / 高级', icon: '🛰️' },
]

const visualCategory = ref('cloudmail')

const runtimeFields = ref([])
const runtimeForm = reactive({})
const mailServices = ref([])
const mailServiceDefault = ref('')
const runtimeLoading = ref(false)
const runtimeSaving = ref(false)
const runtimeSaved = ref(false)
const runtimeMessage = ref('')
const runtimeMessageClass = ref('')

// 切换分类时清掉“已保存”/消息提示，避免上个分类的提示串到新分类
watch(visualCategory, () => {
  runtimeSaved.value = false
  runtimeMessage.value = ''
})

const runtimeRequiredKeys = new Set(['API_KEY'])

const mailServiceFieldMeta = {
  cloudmail: [
    {
      key: 'base_url',
      label: 'CloudMail API 地址',
      required: true,
      placeholder: 'https://your-cloudmail.com/api',
    },
    {
      key: 'email',
      label: 'CloudMail 登录邮箱',
      required: true,
      placeholder: 'admin@example.com',
    },
    {
      key: 'password',
      label: 'CloudMail 登录密码',
      required: true,
      inputType: 'password',
    },
    {
      key: 'domain',
      label: 'CloudMail 邮箱域名',
      required: true,
      placeholder: 'example.com 或 @example.com',
      hint: '用于自动匹配已有账号所属邮箱服务',
    },
  ],
  cloudflare_temp_email: [
    {
      key: 'base_url',
      label: 'Cloudflare Temp Email API 地址',
      required: true,
      placeholder: 'https://temp-email-api.example.com',
    },
    {
      key: 'admin_password',
      label: '管理员密码',
      required: true,
      inputType: 'password',
    },
    {
      key: 'domain',
      label: '邮箱域名',
      required: true,
      placeholder: 'mail.example.com',
      hint: '用于自动匹配已有账号所属邮箱服务',
    },
  ],
}

const selectedRuntimeCategory = computed(() => runtimeCategoryKeys[visualCategory.value] ? visualCategory.value : '')
const currentRuntimeCategoryMeta = computed(() => runtimeCategoryMeta[selectedRuntimeCategory.value] || null)

function fieldByKey(key) {
  return runtimeFields.value.find(field => field.key === key) || null
}

function fieldsByKeys(keys) {
  return keys
    .map(key => fieldByKey(key))
    .filter(Boolean)
}

const proxyFields = computed(() => fieldsByKeys(runtimeCategoryKeys.proxy))
const proxyProxyFields = computed(() =>
  proxyFields.value.filter((field) => field.key !== 'PHONE_OTP_AUTO_SEND')
)

const phoneOtpAutoSendOptions = [
  { value: 'off', label: '关闭' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'sms', label: '短信' },
]
const syncCpaFields = computed(() => fieldsByKeys(['CPA_URL', 'CPA_KEY']))
const defaultMailService = computed(() => mailServices.value.find(service => service.id === mailServiceDefault.value) || null)

const currentRuntimeFields = computed(() => {
  return []
})

function setRuntimeMessage(text, type = 'success') {
  runtimeMessage.value = text
  runtimeMessageClass.value = type === 'success'
    ? 'bg-green-500/10 text-green-400 border-green-500/20'
    : 'bg-red-500/10 text-red-400 border-red-500/20'
  window.clearTimeout(setRuntimeMessage._timer)
  setRuntimeMessage._timer = window.setTimeout(() => {
    runtimeMessage.value = ''
  }, 8000)
}

function fieldInputType(key) {
  return key.includes('PASSWORD') || key.includes('KEY') ? 'password' : 'text'
}

function fieldIsSensitive(key) {
  return key.includes('PASSWORD') || key.includes('KEY')
}

function fieldPlaceholder(key, fallback = '') {
  return fieldIsSensitive(key) ? '留空则不修改' : (fallback || '')
}

function createMailService(type = 'cloudmail') {
  const normalizedType = String(type || '').toLowerCase() === 'cloudflare_temp_email'
    ? 'cloudflare_temp_email'
    : 'cloudmail'
  const randomPart = Math.random().toString(36).slice(2, 8)
  return {
    id: `mailsvc-${Date.now().toString(36)}-${randomPart}`,
    type: normalizedType,
    name: '',
    base_url: '',
    domain: '',
    email: '',
    password: '',
    admin_password: '',
  }
}

function normalizeMailService(service) {
  const template = createMailService(service?.type)
  return {
    ...template,
    id: String(service?.id || template.id),
    name: String(service?.name || ''),
    base_url: String(service?.base_url || ''),
    domain: String(service?.domain || ''),
    email: String(service?.email || ''),
    password: String(service?.password || ''),
    admin_password: String(service?.admin_password || ''),
  }
}

function sanitizeMailService(service) {
  const normalized = normalizeMailService(service)
  normalized.domain = normalized.domain.trim()
  if (normalized.type === 'cloudflare_temp_email') {
    delete normalized.email
    delete normalized.password
  } else {
    delete normalized.admin_password
  }
  return normalized
}

function mailServiceTypeLabel(type) {
  return type === 'cloudflare_temp_email' ? 'Cloudflare Temp Email' : 'CloudMail'
}

function mailServiceDescription(type) {
  return type === 'cloudflare_temp_email'
    ? '填写管理端 API 地址、管理员密码和对应邮箱域名。'
    : '填写 CloudMail API 地址、管理员账号密码和对应邮箱域名。'
}

function mailServiceFields(service) {
  return mailServiceFieldMeta[service?.type] || mailServiceFieldMeta.cloudmail
}

function isMailServiceComplete(service) {
  return mailServiceFields(service).every(field => {
    if (!field.required) {
      return true
    }
    return String(service?.[field.key] || '').trim() !== ''
  })
}

function mailServiceCardTitle(service) {
  const name = String(service?.name || '').trim()
  if (name) {
    return name
  }
  const label = mailServiceTypeLabel(service?.type)
  const domain = String(service?.domain || '').trim()
  return domain ? `${label} (${domain})` : label
}

function ensureMailServiceDefault() {
  const existingIds = new Set(mailServices.value.map(service => service.id))
  if (mailServiceDefault.value && existingIds.has(mailServiceDefault.value)) {
    return
  }
  mailServiceDefault.value = mailServices.value[0]?.id || ''
}

function addMailService(type) {
  mailServices.value = [...mailServices.value, createMailService(type)]
  ensureMailServiceDefault()
}

function removeMailService(id) {
  mailServices.value = mailServices.value.filter(service => service.id !== id)
  ensureMailServiceDefault()
}

function setDefaultMailService(id) {
  mailServiceDefault.value = id
}

function isRuntimeRequired(field) {
  return Boolean(field?.runtime_required) || runtimeRequiredKeys.has(field?.key)
}

function normalizeRuntimeFieldValue(field) {
  return field?.value ?? field?.default ?? ''
}

async function loadRuntimeConfig({ silent = false } = {}) {
  if (!silent) {
    runtimeLoading.value = true
  }
  try {
    const result = await api.getRuntimeConfig()
    runtimeFields.value = result.fields || []
    mailServices.value = Array.isArray(result.mail_services)
      ? result.mail_services.map(service => normalizeMailService(service))
      : []
    mailServiceDefault.value = String(result.mail_service_default || '')
    ensureMailServiceDefault()

    for (const key of Object.keys(runtimeForm)) {
      if (!runtimeFields.value.find(field => field.key === key)) {
        delete runtimeForm[key]
      }
    }
    for (const field of runtimeFields.value) {
      runtimeForm[field.key] = normalizeRuntimeFieldValue(field)
    }
  } catch (e) {
    console.error('加载运行时配置失败:', e)
    setRuntimeMessage('加载运行时配置失败: ' + e.message, 'error')
  } finally {
    if (!silent) {
      runtimeLoading.value = false
    }
  }
}

async function saveRuntimeConfig() {
  runtimeSaving.value = true
  runtimeSaved.value = false
  try {
    const payload = {}
    // 仅提交当前页面（分类）涉及的字段，其它分类保持不变
    const category = selectedRuntimeCategory.value
    const keysForCurrentPage = new Set(runtimeCategoryKeys[category] || [])
    for (const field of runtimeFields.value) {
      if (!keysForCurrentPage.has(field.key)) continue
      // 邮箱服务分类的凭证字段由下方结构化服务数据提交，这里不重复
      if (category === 'cloudmail' && field.key.startsWith('CLOUDMAIL_')) continue
      if (category === 'cloudmail' && field.key.startsWith('CF_TEMP_EMAIL_')) continue
      const value = runtimeForm[field.key]
      payload[field.key] = value == null ? '' : String(value)
    }
    if (category === 'cloudmail') {
      const sanitizedServices = mailServices.value.map(service => sanitizeMailService(service))
      const sanitizedDefault = sanitizedServices.some(service => service.id === mailServiceDefault.value)
        ? mailServiceDefault.value
        : sanitizedServices[0]?.id || ''
      payload.mail_services = sanitizedServices
      payload.mail_service_default = sanitizedDefault
    }
    const result = await api.saveRuntimeConfig(payload)
    runtimeSaved.value = true
    window.setTimeout(() => {
      runtimeSaved.value = false
    }, 3000)
    await loadRuntimeConfig({ silent: true })
    emit('refresh')
  } catch (e) {
    setRuntimeMessage(e.message, 'error')
  } finally {
    runtimeSaving.value = false
  }
}

onMounted(async () => {
  await loadRuntimeConfig()
})
</script>
