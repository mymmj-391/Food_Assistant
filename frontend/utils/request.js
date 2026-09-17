// utils/request.js
// 后端服务地址（FastAPI 默认端口 8000）
// 电脑浏览器调试用 127.0.0.1，手机/其他设备访问需改成电脑局域网 IP
const BASE_URL = 'http://127.0.0.1:8000'

const requestCache = new Map()
const pendingRequests = new Map()

const getCacheKey = (url, data) => {
	return url + JSON.stringify(data || {})
}

const clearAllCache = () => {
	requestCache.clear()
}

/**
 * 封装 uni.request
 * - 自动携带登录 token（Bearer）
 * - 统一处理 401 / 网络错误
 * - 自动去重相同请求
 * - 支持缓存
 */
export const request = (options) => {
	const cacheKey = getCacheKey(options.url, options.data)
	if (options.method === 'GET' && requestCache.has(cacheKey)) {
		return Promise.resolve(requestCache.get(cacheKey))
	}
	if (pendingRequests.has(cacheKey)) {
		return pendingRequests.get(cacheKey)
	}

	const token = uni.getStorageSync('token')

	const promise = new Promise((resolve, reject) => {
		uni.request({
			url: BASE_URL + options.url,
			method: options.method || 'GET',
			data: options.data || {},
			timeout: 10000,
			header: {
				'Content-Type': 'application/json',
				...(token ? { Authorization: `Bearer ${token}` } : {})
			},
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					if (options.method === 'GET') {
						requestCache.set(cacheKey, res.data)
					} else {
						// 写操作后清空缓存，避免返回过期数据
						clearAllCache()
					}
					resolve(res.data)
					return
				}
				if (res.statusCode === 401) {
					uni.removeStorageSync('token')
					uni.removeStorageSync('user')
					uni.reLaunch({ url: '/pages/login/login' })
				}
				let msg = '请求失败'
				const data = res.data

				if (data && data.detail) {
					if (typeof data.detail === 'string') {
						msg = data.detail
					}
					else if (Array.isArray(data.detail) && data.detail.length > 0) {
						const firstError = data.detail[0]
						const rawMsg = firstError.msg || ''

						if (rawMsg.includes('String should have at least')) {
							const num = rawMsg.match(/\d+/)[0]
							const field = firstError.loc?.[1] || '输入内容'

							if (field === 'username') msg = `用户名长度至少为 ${num} 个字符`
							else if (field === 'nickname') msg = `昵称长度至少为 ${num} 个字符`
							else if (field === 'password') msg = `密码长度至少为 ${num} 位`
							else msg = `${field} 长度不能少于 ${num} 个字符`
						} else {
							msg = rawMsg || '数据格式校验失败'
						}
					}
				}
				uni.showToast({
					title: msg,
					icon: 'none',
					duration: 2000
				})
				reject(res.data)
			},
			fail: (err) => {
				uni.showToast({
					title: '网络请求失败，请确认后端已启动',
					icon: 'none'
				})
				reject(err)
			},
			complete: () => {
				pendingRequests.delete(cacheKey)
			}
		})
	})

	pendingRequests.set(cacheKey, promise)
	return promise
}

export { BASE_URL }
