const BASE_URL = import.meta.env.VITE_API_BASE_URL
const SSE_BASE_URL = import.meta.env.VITE_SSE_API_BASE_URL || BASE_URL
const STREAM_DONE_MARKER = '[[__STREAM_DONE__]]'

export const analyzeBlueprintStream = async (file, customPrompt, methodologies, customMethodologies, userInfo, signal, onChunk, onError, onComplete) => {
  const formData = new FormData()
  formData.append('file', file)
  if (customPrompt) {
    formData.append('custom_prompt', customPrompt)
  }
  
  if (userInfo) {
    formData.append('user_id', userInfo.user_id)
    formData.append('username', userInfo.username)
    if (userInfo.role) {
      formData.append('role', userInfo.role)
    }
  }
  
  if (methodologies && methodologies.length > 0) {
    methodologies.forEach(m => formData.append('methodologies', m))
  }

  if (customMethodologies && customMethodologies.length > 0) {
    customMethodologies.forEach(cm => formData.append('custom_methodologies', cm))
  }

  try {
    const response = await fetch(`${SSE_BASE_URL}/blueprint/analyze`, {
      method: 'POST',
      body: formData,
      signal // 传递 AbortSignal
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        console.log('Stream done')
        break
      }
      const chunk = decoder.decode(value, { stream: true })
      console.log('Received chunk:', chunk.length, 'chars')
      buffer += chunk

      const markerIndex = buffer.indexOf(STREAM_DONE_MARKER)
      if (markerIndex !== -1) {
        const before = buffer.slice(0, markerIndex)
        if (before) onChunk(before)
        try {
          await reader.cancel()
        } catch (e) {
        }
        if (onComplete) onComplete()
        return
      }

      if (buffer.length > STREAM_DONE_MARKER.length) {
        const flushLen = buffer.length - STREAM_DONE_MARKER.length
        const out = buffer.slice(0, flushLen)
        buffer = buffer.slice(flushLen)
        if (out) onChunk(out)
      }
    }
    if (buffer) onChunk(buffer)
    
    if (onComplete) onComplete()

  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Stream aborted by user')
      // 用户手动停止，不视为错误，但需要调用完成回调以重置状态（或者在外部处理）
      if (onComplete) onComplete()
      return
    }
    if (onError) onError(error)
    console.error('Stream error:', error)
  }
}

export const getAnalysisHistory = async (userId, page = 1, pageSize = 10) => {
  const params = new URLSearchParams()
  params.set('user_id', userId)
  params.set('page', String(page))
  params.set('page_size', String(pageSize))

  const response = await fetch(`${BASE_URL}/blueprint/history?${params.toString()}`, {
    method: 'GET'
  })

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error((data && data.message) || `HTTP error! status: ${response.status}`)
  }
  if (!data || data.code !== 200) {
    throw new Error((data && data.message) || 'Failed to fetch history')
  }
  return data
}

export const getAnalysisHistoryDetail = async (userId, historyId) => {
  const params = new URLSearchParams()
  params.set('user_id', userId)

  const response = await fetch(`${BASE_URL}/blueprint/history/${historyId}?${params.toString()}`, {
    method: 'GET'
  })

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error((data && data.message) || `HTTP error! status: ${response.status}`)
  }
  if (!data || data.code !== 200) {
    throw new Error((data && data.message) || 'Failed to fetch history detail')
  }
  return data
}

export const exportDocx = async (content, filename) => {
  const response = await fetch(`${BASE_URL}/blueprint/export/docx`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ content, filename })
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.message || 'Export failed')
  }

  const blob = await response.blob()
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename || 'report.docx'
  link.click()
  URL.revokeObjectURL(link.href)
}

export const generateSmartMindmapStream = async (file, onChunk, onError, onComplete) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${BASE_URL}/blueprint/smart_mindmap`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const markerIndex = buffer.indexOf(STREAM_DONE_MARKER)
      if (markerIndex !== -1) {
        const before = buffer.slice(0, markerIndex)
        if (before) onChunk(before)
        try {
          await reader.cancel()
        } catch (e) {
        }
        if (onComplete) onComplete()
        return
      }

      if (buffer.length > STREAM_DONE_MARKER.length) {
        const flushLen = buffer.length - STREAM_DONE_MARKER.length
        const out = buffer.slice(0, flushLen)
        buffer = buffer.slice(flushLen)
        if (out) onChunk(out)
      }
    }
    if (buffer) onChunk(buffer)
    
    if (onComplete) onComplete()

  } catch (error) {
    if (onError) onError(error)
    console.error('Smart Mindmap stream error:', error)
  }
}

export const generateMindmapStream = async (content, onChunk, onError, onComplete) => {
  try {
    const response = await fetch(`${BASE_URL}/blueprint/generate_mindmap`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const markerIndex = buffer.indexOf(STREAM_DONE_MARKER)
      if (markerIndex !== -1) {
        const before = buffer.slice(0, markerIndex)
        if (before) onChunk(before)
        try {
          await reader.cancel()
        } catch (e) {
        }
        if (onComplete) onComplete()
        return
      }

      if (buffer.length > STREAM_DONE_MARKER.length) {
        const flushLen = buffer.length - STREAM_DONE_MARKER.length
        const out = buffer.slice(0, flushLen)
        buffer = buffer.slice(flushLen)
        if (out) onChunk(out)
      }
    }
    if (buffer) onChunk(buffer)
    
    if (onComplete) onComplete()

  } catch (error) {
    if (onError) onError(error)
    console.error('Mindmap stream error:', error)
  }
}

export const analyzeBlueprintToMindmapStream = async (file, onChunk, onError, onComplete) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${BASE_URL}/blueprint/analyze_mindmap`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const markerIndex = buffer.indexOf(STREAM_DONE_MARKER)
      if (markerIndex !== -1) {
        const before = buffer.slice(0, markerIndex)
        if (before) onChunk(before)
        try {
          await reader.cancel()
        } catch (e) {
        }
        if (onComplete) onComplete()
        return
      }

      if (buffer.length > STREAM_DONE_MARKER.length) {
        const flushLen = buffer.length - STREAM_DONE_MARKER.length
        const out = buffer.slice(0, flushLen)
        buffer = buffer.slice(flushLen)
        if (out) onChunk(out)
      }
    }
    if (buffer) onChunk(buffer)
    
    if (onComplete) onComplete()

  } catch (error) {
    if (onError) onError(error)
    console.error('Diagnosis Mindmap stream error:', error)
  }
}

export const generateProposalStream = async (clientNeeds, userIdeas, methodologies, customMethodologies, referenceFile, onChunk, onError, onComplete) => {
  try {
    const requestInit = {
      method: 'POST'
    }

    if (referenceFile) {
      const formData = new FormData()
      formData.append('client_needs', clientNeeds)
      formData.append('user_ideas', userIdeas || '')
      formData.append('reference_file', referenceFile)

      if (methodologies && methodologies.length > 0) {
        methodologies.forEach(m => formData.append('methodologies', m))
      }

      if (customMethodologies && customMethodologies.length > 0) {
        customMethodologies.forEach(cm => formData.append('custom_methodologies', cm))
      }

      requestInit.body = formData
    } else {
      requestInit.headers = {
        'Content-Type': 'application/json'
      }
      requestInit.body = JSON.stringify({
        client_needs: clientNeeds,
        user_ideas: userIdeas,
        methodologies: methodologies,
        custom_methodologies: customMethodologies
      })
    }

    const response = await fetch(`${BASE_URL}/blueprint/generate_proposal`, requestInit)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const markerIndex = buffer.indexOf(STREAM_DONE_MARKER)
      if (markerIndex !== -1) {
        const before = buffer.slice(0, markerIndex)
        if (before) onChunk(before)
        try {
          await reader.cancel()
        } catch (e) {
        }
        if (onComplete) onComplete()
        return
      }

      if (buffer.length > STREAM_DONE_MARKER.length) {
        const flushLen = buffer.length - STREAM_DONE_MARKER.length
        const out = buffer.slice(0, flushLen)
        buffer = buffer.slice(flushLen)
        if (out) onChunk(out)
      }
    }
    if (buffer) onChunk(buffer)
    
    if (onComplete) onComplete()

  } catch (error) {
    if (onError) onError(error)
    console.error('Proposal generation stream error:', error)
  }
}

export const generateSubProposalStream = async (parentPlanFile, subPlanTitle, subPlanDetails, methodologies, customMethodologies, onChunk, onError, onComplete) => {
  try {
    const formData = new FormData()
    formData.append('parent_file', parentPlanFile)
    formData.append('sub_plan_title', subPlanTitle)
    formData.append('sub_plan_details', subPlanDetails || '')

    if (methodologies && methodologies.length > 0) {
      methodologies.forEach(m => formData.append('methodologies', m))
    }

    if (customMethodologies && customMethodologies.length > 0) {
      customMethodologies.forEach(cm => formData.append('custom_methodologies', cm))
    }

    const response = await fetch(`${BASE_URL}/blueprint/generate_sub_proposal`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const markerIndex = buffer.indexOf(STREAM_DONE_MARKER)
      if (markerIndex !== -1) {
        const before = buffer.slice(0, markerIndex)
        if (before) onChunk(before)
        try {
          await reader.cancel()
        } catch (e) {
        }
        if (onComplete) onComplete()
        return
      }

      if (buffer.length > STREAM_DONE_MARKER.length) {
        const flushLen = buffer.length - STREAM_DONE_MARKER.length
        const out = buffer.slice(0, flushLen)
        buffer = buffer.slice(flushLen)
        if (out) onChunk(out)
      }
    }
    if (buffer) onChunk(buffer)

    if (onComplete) onComplete()
  } catch (error) {
    if (onError) onError(error)
    console.error('Sub proposal generation stream error:', error)
  }
}
