// api/dish.js
// 菜品相关接口
import { request } from '../utils/request'

// 获取所有分类
export const getCategories = () => request({
	url: '/api/dishes/categories'
})

// 根据分类 id 获取菜品列表
export const getDishesByCategory = (categoryId) => request({
	url: `/api/dishes/category/${categoryId}`
})

// 获取菜品详情（.md 内容）
export const getDishDetail = (categoryId, dishName) => request({
	url: `/api/dishes/detail/${categoryId}/${encodeURIComponent(dishName)}`
})

// 获取菜品图片列表
export const getDishImages = (categoryId, dishName) => request({
	url: `/api/dishes/images/${categoryId}/${encodeURIComponent(dishName)}`
})
