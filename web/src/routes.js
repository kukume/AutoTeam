// 路由表：导航项 + 页面/路径映射。
// 由 Sidebar.vue (items) 与 App.vue (pageFromPath / PATH_BY_PAGE) 共用。

export const ROUTES = [
  { key: 'dashboard', path: '/', icon: '📊', label: '仪表盘', mobileLabel: '仪表盘', hint: '概览账号池与状态' },
  { key: 'config', path: '/config', icon: '🧩', label: '配置面板', mobileLabel: '配置', hint: '统一编辑系统配置' },
  { key: 'team', path: '/team', icon: '👥', label: 'Team 成员', mobileLabel: '成员', hint: '查看与管理成员' },
  { key: 'pool', path: '/pool', icon: '🔁', label: '账号池操作', mobileLabel: '账号池', hint: '轮转、补位与清理' },
  { key: 'sync', path: '/sync', icon: '🔄', label: '同步中心', mobileLabel: '同步', hint: '同步本地、远端与状态' },
  { key: 'oauth', path: '/oauth', icon: '🔐', label: 'OAuth 登录', mobileLabel: 'OAuth', hint: '手动接管 OAuth 流程' },
  { key: 'tasks', path: '/tasks', icon: '📜', label: '任务历史', mobileLabel: '任务', hint: '追踪任务执行结果' },
  { key: 'logs', path: '/logs', icon: '📋', label: '日志', mobileLabel: '日志', hint: '查看实时运行日志' },
]

const KEY_BY_PATH = Object.fromEntries(ROUTES.map((item) => [item.path, item.key]))

export const PATH_BY_PAGE = Object.fromEntries(ROUTES.map((item) => [item.key, item.path]))

export function pageFromPath(pathname = window.location.pathname) {
  return KEY_BY_PATH[pathname] || 'dashboard'
}
