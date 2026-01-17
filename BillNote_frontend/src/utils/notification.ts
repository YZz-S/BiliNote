type NotifyOptions = {
  title?: string
  body?: string
  icon?: string
  tag?: string
}

const canUseNotification = () => typeof window !== 'undefined' && 'Notification' in window

export const requestNotificationPermission = async () => {
  if (!canUseNotification()) return false
  if (Notification.permission === 'granted') return true
  if (Notification.permission === 'denied') return false
  const perm = await Notification.requestPermission()
  return perm === 'granted'
}

export const showNotification = async (options: NotifyOptions) => {
  const allowed = await requestNotificationPermission()
  if (!allowed) return false
  const { title, body, icon, tag } = options
  const t = title || '通知'
  const n = new Notification(t, { body, icon, tag })
  return !!n
}

export const notifyTaskSuccess = async (params: {
  taskId: string
  title?: string
  duration?: number
}) => {
  const title = params.title || '笔记总结完成'
  const body = params.duration
    ? `任务 ${params.taskId} 已完成，时长 ${Math.round(params.duration)} 秒`
    : `任务 ${params.taskId} 已完成`
  return showNotification({ title, body, tag: `task-${params.taskId}` })
}

export const notifyTaskFailed = async (params: { taskId: string; message?: string }) => {
  const title = '笔记总结失败'
  const body = params.message ? `任务 ${params.taskId} 失败：${params.message}` : `任务 ${params.taskId} 失败`
  return showNotification({ title, body, tag: `task-${params.taskId}` })
}
