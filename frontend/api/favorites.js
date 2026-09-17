import { request } from '../utils/request'

// 获取收藏列表
export const getFavorites = () => request({
	url: '/api/favorites/list'
})

// 添加收藏
export const addFavorite = (data) => request({
	url: '/api/favorites/add',
	method: 'POST',
	data
})

// 取消收藏
export const removeFavorite = (data) => request({
	url: '/api/favorites/remove',
	method: 'POST',
	data
})

// 获取饮食记录
export const getDietRecords = () => request({
	url: '/api/favorites/diet/list'
})

// 添加饮食记录
export const addDietRecord = (data) => request({
	url: '/api/favorites/diet/add',
	method: 'POST',
	data
})

// 删除饮食记录
export const deleteDietRecord = (id) => request({
	url: `/api/favorites/diet/delete?id=${id}`,
	method: 'DELETE'
})
