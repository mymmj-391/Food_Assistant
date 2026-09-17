// api/auth.js
// 认证相关接口
import { request } from '../utils/request'

// 登录
export const login = (data) => request({
	url: '/api/auth/login',
	method: 'POST',
	data
})

// 注册（后端注册成功即返回 token，可直接登录）
export const register = (data) => request({
	url: '/api/auth/register',
	method: 'POST',
	data
})
