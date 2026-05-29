import { useEffect, useRef } from 'react'
import { useTaskStore } from '@/store/taskStore'
import { get_task_status } from '@/services/note.ts'
import toast from 'react-hot-toast'
import { notifyTaskSuccess, notifyTaskFailed } from '@/utils/notification'

export const useTaskPolling = (interval = 3000) => {
  const tasks = useTaskStore(state => state.tasks)
  const updateTaskContent = useTaskStore(state => state.updateTaskContent)

  const tasksRef = useRef(tasks)

  // 每次 tasks 更新，把最新的 tasks 同步进去
  useEffect(() => {
    tasksRef.current = tasks
  }, [tasks])

  useEffect(() => {
    const timer = setInterval(async () => {
      const pendingTasks = tasksRef.current.filter(
        task => task.status != 'SUCCESS' && task.status != 'FAILED'
      )

      for (const task of pendingTasks) {
        try {
          console.log('🔄 正在轮询任务：', task.id)
          const res = await get_task_status(task.id)
          const { status, result, message } = res

          if (status && status !== task.status) {
            if (status === 'SUCCESS') {
              if (!result?.markdown || !result?.transcript || !result?.audio_meta) {
                const errorMessage = message || '任务状态异常：已完成但结果数据不完整'
                console.error(`❌ 任务 ${task.id} 返回成功但结果缺失：`, res)
                updateTaskContent(task.id, { status: 'FAILED' })
                toast.error(errorMessage)
                notifyTaskFailed({ taskId: task.id, message: errorMessage })
                continue
              }

              const { markdown, transcript, audio_meta } = result
              toast.success('笔记生成成功')
              notifyTaskSuccess({
                taskId: task.id,
                title: audio_meta?.title,
                duration: audio_meta?.duration,
              })
              updateTaskContent(task.id, {
                status,
                markdown,
                transcript,
                audioMeta: audio_meta,
              })
            } else if (status === 'FAILED') {
              updateTaskContent(task.id, { status })
              console.warn(`⚠️ 任务 ${task.id} 失败`)
            } else {
              updateTaskContent(task.id, { status })
            }
          }
        } catch (e) {
          console.error('❌ 任务轮询失败：', e)
          updateTaskContent(task.id, { status: 'FAILED' })
          const msg = (e && (e.msg || e.message)) || ''
          notifyTaskFailed({ taskId: task.id, message: msg })
        }
      }
    }, interval)

    return () => clearInterval(timer)
  }, [interval])
}
