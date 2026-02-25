import { Transcript } from '@/store/taskStore'

const toSrtTime = (seconds: number) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  const ms = Math.floor((seconds - Math.floor(seconds)) * 1000)
  const hh = h.toString().padStart(2, '0')
  const mm = m.toString().padStart(2, '0')
  const ss = s.toString().padStart(2, '0')
  const mss = ms.toString().padStart(3, '0')
  return `${hh}:${mm}:${ss},${mss}`
}

export const buildSrtFromTranscript = (t: Transcript) => {
  const segments = t?.segments || []
  return segments
    .map(
      (seg, i) =>
        `${i + 1}\n${toSrtTime(seg.start)} --> ${toSrtTime(seg.end)}\n${seg.text}`,
    )
    .join('\n\n')
}

export const buildMarkdownFromTranscript = (t: Transcript) => {
  const full = t?.full_text || ''
  if (full) return full
  const segments = t?.segments || []
  return segments.map(seg => seg.text).join('\n')
}
