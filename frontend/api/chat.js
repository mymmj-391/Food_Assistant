// api/chat.js
// RAG 对话 API 封装
import { request, BASE_URL } from '../utils/request'

/**
 * 流式聊天 - 使用 SSE (Server-Sent Events)
 * @param {string} query - 用户问题
 * @param {number} top_k - 检索文档数量
 * @param {string} session_id - 会话ID（可选）
 * @param {object} callbacks - 回调函数 { onContent, onToolCall, onDone, onError }
 * @returns {Function} - 取消函数
 */
export const streamChatMessage = (query, top_k = 5, session_id = null, callbacks = {}) => {
	const { onContent, onToolCall, onDone, onError } = callbacks

	let cancelled = false
	let abortController = null

	// 使用 fetch API 进行 SSE 流式请求
	const token = uni.getStorageSync('token')
	const headers = {
		'Content-Type': 'application/json',
		...(token ? { Authorization: `Bearer ${token}` } : {})
	}

	// 使用 uni.request 的流式响应（H5 环境）
	// 或者使用 fetch API
	const doRequest = async () => {
		try {
			// 检测环境：H5 浏览器 vs 小程序/APP
			// #ifdef H5
			// H5 环境使用 fetch API 读取流式响应
			abortController = new AbortController()

			const response = await fetch(`${BASE_URL}/api/chat/stream`, {
				method: 'POST',
				headers,
				body: JSON.stringify({ query, top_k, session_id }),
				signal: abortController.signal
			})

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`)
			}

			const reader = response.body.getReader()
			const decoder = new TextDecoder()
			let buffer = ''

			while (true) {
				if (cancelled) break

				const { done, value } = await reader.read()
				if (done) break

				buffer += decoder.decode(value, { stream: true })

				// 处理 SSE 格式数据
				const lines = buffer.split('\n')
				buffer = lines.pop() || ''

				for (const line of lines) {
					if (cancelled) break
					if (!line.startsWith('data: ')) continue

					const jsonStr = line.substring(6)
					if (!jsonStr.trim()) continue

					try {
						const data = JSON.parse(jsonStr)

						switch (data.type) {
							case 'content':
								if (onContent) onContent(data.content)
								break
							case 'tool_call':
								if (onToolCall) onToolCall(data.name)
								break
							case 'done':
								if (onDone) onDone(data)
								break
							case 'error':
								if (onError) onError(data.content || '未知错误')
								break
						}
					} catch (e) {
						console.error('[SSE] 解析消息失败:', e, jsonStr)
					}
				}
			}
			// #endif

			// #ifndef H5
			// 非 H5 环境（小程序/APP）使用 uni.request
			// 注意：uni.request 不支持真正的流式响应，这里使用非流式接口作为降级
			console.warn('[Chat] 非H5环境，使用非流式接口')
			try {
				const result = await request({
					url: '/api/chat/ask',
					method: 'POST',
					data: { query, top_k, session_id }
				})
				if (onContent) onContent(result.answer)
				if (onDone) onDone({
					session_id: result.session_id,
					sources: result.sources,
					dish_links: result.dish_links
				})
			} catch (err) {
				if (onError) onError(err.detail || err.message || '请求失败')
			}
			// #endif
		} catch (err) {
			if (cancelled) return
			console.error('[Chat] 请求失败:', err)
			if (onError) onError(err.message || '请求失败')
		}
	}

	doRequest()

	return () => {
		cancelled = true
		if (abortController) {
			abortController.abort()
		}
	}
}
