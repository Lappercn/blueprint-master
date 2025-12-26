const BASE_URL = import.meta.env.VITE_API_BASE_URL

export const submitFeedback = async (userId, username, content) => {
  const response = await fetch(`${BASE_URL}/feedback/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ user_id: userId, username, content })
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.message || 'Feedback submission failed')
  }

  return await response.json()
}
