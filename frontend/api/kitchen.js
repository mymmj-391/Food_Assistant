// api/kitchen.js
// 厨房技巧相关接口
import { request } from '../utils/request'

// 获取技巧列表
export const getKitchenTips = () => request({
	url: '/api/kitchen/tips'
})

// 获取技巧详情
export const getKitchenTipDetail = (tipName) => request({
	url: `/api/kitchen/tips/${encodeURIComponent(tipName)}`
})
