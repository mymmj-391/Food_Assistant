<template>
	<AppLayout ref="layout">
		<CursorTrail />
		<scroll-view class="detail-scroll" scroll-y="true">
			<view v-if="loading" class="loading-state">
				<text>加载中...</text>
			</view>

			<view v-else-if="!dish" class="empty-state">
				<text class="empty-text">该菜品不存在</text>
			</view>

			<view v-else class="detail-container">
				<view class="dish-header">
					<text class="dish-name">{{ dish.name }}</text>
					<view v-if="images.length" class="image-swiper">
						<swiper :indicator-dots="images.length > 1" :autoplay="images.length > 1" :interval="3000" :duration="500" class="swiper" :style="{ height: imageHeight + 'rpx' }">
							<swiper-item v-for="(img, idx) in images" :key="idx">
								<image class="swiper-image" :src="img" mode="aspectFit" @error="onImageError(idx)" @load="onImageLoad($event, idx)"></image>
							</swiper-item>
						</swiper>
					</view>
				</view>

				<view class="tab-container">
					<view class="tab-header">
						<view
							v-for="tab in tabs"
							:key="tab.key"
							class="tab-item"
							:class="{ 'tab-active': activeTab === tab.key }"
							@click="activeTab = tab.key"
						>
							<text class="tab-icon">{{ tab.icon }}</text>
							<text class="tab-label">{{ tab.label }}</text>
						</view>
					</view>

					<view class="tab-content">
						<view v-if="activeTab === 'ingredients'" class="tab-panel">
							<view v-if="ingredients.main.length || ingredients.seasoning.length" class="ingredients-wrapper">
								<view v-if="ingredients.main.length" class="ingredient-section">
									<view class="section-header">
										<text class="section-icon">🥩</text>
										<text class="section-title">主料</text>
									</view>
									<view class="card-grid">
										<view v-for="(item, idx) in ingredients.main" :key="idx" class="ingredient-card main-card">
											<text class="ingredient-name">{{ item.name }}</text>
											<text class="ingredient-amount">{{ item.amount }}</text>
										</view>
									</view>
								</view>
								<view v-if="ingredients.seasoning.length" class="ingredient-section">
									<view class="section-header">
										<text class="section-icon">🧂</text>
										<text class="section-title">调料</text>
									</view>
									<view class="card-grid seasoning-grid">
										<view v-for="(item, idx) in ingredients.seasoning" :key="idx" class="ingredient-card seasoning-card">
											<text class="ingredient-name">{{ item.name }}</text>
											<text class="ingredient-amount">{{ item.amount }}</text>
										</view>
									</view>
								</view>
							</view>
							<view v-else class="empty-panel">
								<text class="empty-panel-text">暂无食材信息</text>
							</view>
						</view>

						<view v-if="activeTab === 'steps'" class="tab-panel">
							<view v-if="stepsList.length" class="steps-wrapper">
								<view class="steps-header-bar">
									<text class="steps-count">共 {{ stepsList.length }} 步</text>
								</view>
								<view v-for="(step, idx) in stepsList" :key="idx" class="step-row">
									<view class="step-badge">
										<text class="step-badge-text">{{ idx + 1 }}</text>
									</view>
									<view class="step-content-card">
										<text class="step-content-text">{{ step.text }}</text>
									</view>
								</view>
							</view>
							<view v-else class="empty-panel">
								<text class="empty-panel-text">暂无步骤信息</text>
							</view>
						</view>

						<view v-if="activeTab === 'tips'" class="tab-panel">
							<view v-if="tipsList.length" class="tips-wrapper">
								<view class="tips-card-container">
									<view class="tips-header">
										<text class="tips-icon">💡</text>
										<text class="tips-title">小贴士</text>
									</view>
									<view class="tips-divider"></view>
									<view class="tips-list">
										<view v-for="(tip, idx) in tipsList" :key="idx" class="tip-row">
											<view class="tip-bullet"></view>
											<text class="tip-text">{{ tip }}</text>
										</view>
									</view>
								</view>
							</view>
							<view v-else class="empty-panel">
								<text class="empty-panel-text">暂无贴士信息</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
	</AppLayout>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import AppLayout from '../../components/AppLayout.vue'
import CursorTrail from '../../components/CursorTrail.vue'
import { getDishDetail, getDishImages } from '../../api/dish'
import { addDietRecord } from '../../api/favorites'
import { parseIngredients, parseSteps, parseTips } from '../../utils/mdParser'

const layout = ref(null)
const dish = ref(null)
const images = ref([])
const loading = ref(false)
const imageHeight = ref(500)
const activeTab = ref('ingredients')

const tabs = [
	{ key: 'ingredients', label: '食材', icon: '🥬' },
	{ key: 'steps', label: '步骤', icon: '👩‍🍳' },
	{ key: 'tips', label: '贴士', icon: '💡' }
]

const ingredients = computed(() => {
	if (!dish.value?.content) return { main: [], seasoning: [] }
	return parseIngredients(dish.value.content)
})

const stepsList = computed(() => {
	if (!dish.value?.content) return []
	return parseSteps(dish.value.content)
})

const tipsList = computed(() => {
	if (!dish.value?.content) return []
	return parseTips(dish.value.content)
})

const onImageLoad = (e, idx) => {
	if (idx === 0) {
		const { width, height } = e.detail
		if (width > 0 && height > 0) {
			const systemInfo = uni.getSystemInfoSync()
			const containerWidth = systemInfo.windowWidth - 80
			const ratio = height / width
			let calcHeight = containerWidth * ratio
			const minH = 300
			const maxH = 700
			imageHeight.value = Math.round(Math.max(minH, Math.min(maxH, calcHeight)))
		}
	}
}

const onImageError = (idx) => {
	images.value.splice(idx, 1)
}

onLoad((options) => {
	const category = options.category || ''
	const dishName = decodeURIComponent(options.dish || '')

	nextTick(() => {
		layout.value?.setHeader({ greeting: dishName, tip: '' })
		layout.value?.setSidebarSelection({ categoryId: category })
	})

	if (category && dishName) {
		fetchDishDetail(category, dishName)
	}
})

const fetchDishDetail = async (category, dishName) => {
	loading.value = true
	try {
		const [detailRes, imagesRes] = await Promise.all([
			getDishDetail(category, dishName),
			getDishImages(category, dishName)
		])
		if (detailRes && detailRes.content) {
			dish.value = { name: detailRes.name, content: detailRes.content }
		}
		if (imagesRes && imagesRes.images) {
			images.value = imagesRes.images
		}
		addDietRecord({
			dish_name: dishName,
			category_id: category,
			category_name: '',
			image: imagesRes && imagesRes.images && imagesRes.images[0] || ''
		}).catch(() => {})
	} catch (e) {
		uni.showToast({ title: '加载失败，请检查网络', icon: 'none' })
	} finally {
		loading.value = false
	}
}
</script>

<style scoped>
.detail-scroll {
	flex: 1;
	height: 100%;
	box-sizing: border-box;
	-webkit-overflow-scrolling: touch;
}

.loading-state {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 60vh;
	font-size: 28rpx;
	color: rgba(92, 61, 30, 0.5);
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.empty-state {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 60vh;
}
.empty-text {
	font-size: 28rpx;
	color: rgba(92, 61, 30, 0.5);
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.detail-container {
	padding: 20rpx 20rpx 40rpx;
}

.dish-header {
	text-align: center;
	margin-bottom: 30rpx;
}
.dish-name {
	font-size: 44rpx;
	font-weight: bold;
	color: #4a2c1a;
	font-family: 'Ma Shan Zheng', 'ZCOOL XiaoWei', 'STXingkai', serif;
	letter-spacing: 4rpx;
	display: block;
	margin-bottom: 24rpx;
}

.image-swiper {
	width: 100%;
	border-radius: 24rpx;
	border: 6rpx solid #fdf8f0;
	overflow: hidden;
	box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
	background: #fef5eb;
}
.swiper {
	width: 100%;
}
.swiper-image {
	width: 100%;
	height: 100%;
	object-fit: contain;
	border-radius: 20rpx;
	border: 4rpx solid #fef5eb;
	background: #fdf8f0;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.tab-container {
	background: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 8rpx 32rpx rgba(140, 90, 50, 0.08);
	overflow: hidden;
	border: 1px solid rgba(224, 122, 44, 0.1);
	margin-top: 30rpx;
}

.tab-header {
	display: flex;
	background: linear-gradient(135deg, #fef5eb 0%, #fde8d0 100%);
	border-bottom: 2rpx solid rgba(224, 122, 44, 0.12);
}

.tab-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 28rpx 0;
	transition: all 0.2s ease;
	position: relative;
}
.tab-item:active {
	background-color: rgba(224, 122, 44, 0.08);
}
.tab-active {
	background-color: #ffffff;
}
.tab-active::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 50%;
	transform: translateX(-50%);
	width: 60rpx;
	height: 4rpx;
	background: linear-gradient(90deg, #e07a2c, #f5a623);
	border-radius: 2rpx;
}

.tab-icon {
	font-size: 36rpx;
	margin-bottom: 8rpx;
}
.tab-label {
	font-size: 26rpx;
	color: #8b7355;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	font-weight: 500;
}
.tab-active .tab-label {
	color: #e07a2c;
	font-weight: bold;
}

.tab-content {
	min-height: 400rpx;
}

.tab-panel {
	padding: 30rpx;
}

/* ========== 食材区域 ========== */
.ingredients-wrapper {
	display: flex;
	flex-direction: column;
	gap: 32rpx;
}

.ingredient-section {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.section-header {
	display: flex;
	align-items: center;
	gap: 8rpx;
	margin-bottom: 8rpx;
}

.section-icon {
	font-size: 28rpx;
}

.section-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #e07a2c;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.card-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.seasoning-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.ingredient-card {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 16rpx 20rpx;
	border-radius: 12rpx;
	min-width: 140rpx;
	flex: none;
	max-width: 100%;
}

.main-card {
	background: #fff3e6;
}

.seasoning-card {
	background: #fafafa;
	flex-basis: auto;
	flex: none;
	min-width: 0;
}

.ingredient-name {
	font-size: 26rpx;
	color: #4a2c1a;
	font-weight: 600;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	flex: 1;
}

.ingredient-amount {
	font-size: 24rpx;
	color: #b8860b;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	margin-left: 12rpx;
}

/* ========== 步骤区域 ========== */
.steps-wrapper {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.steps-header-bar {
	display: flex;
	justify-content: flex-end;
}

.steps-count {
	font-size: 24rpx;
	color: #8b7355;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.step-row {
	display: flex;
	gap: 20rpx;
	align-items: flex-start;
}

.step-badge {
	width: 48rpx;
	height: 48rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #e07a2c 0%, #f5a623 100%);
	display: flex;
	justify-content: center;
	align-items: center;
	flex-shrink: 0;
}

.step-badge-text {
	font-size: 22rpx;
	color: #fff;
	font-weight: bold;
}

.step-content-card {
	flex: 1;
	background: #fffdf9;
	border-radius: 12rpx;
	padding: 20rpx 24rpx;
	border: 1px solid rgba(224, 122, 44, 0.06);
}

.step-content-text {
	font-size: 26rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.7;
}

/* ========== 贴士区域 ========== */
.tips-wrapper {
	display: flex;
	flex-direction: column;
}

.tips-card-container {
	background: linear-gradient(135deg, #fff9f0 0%, #fef5eb 100%);
	border-radius: 16rpx;
	border: 1px solid rgba(245, 166, 35, 0.15);
	padding: 28rpx;
}

.tips-header {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 16rpx;
}

.tips-icon {
	font-size: 32rpx;
}

.tips-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #e07a2c;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.tips-divider {
	height: 1rpx;
	border-top: 1rpx dashed rgba(245, 166, 35, 0.25);
	margin-bottom: 20rpx;
}

.tips-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.tip-row {
	display: flex;
	align-items: flex-start;
	gap: 14rpx;
}

.tip-bullet {
	width: 10rpx;
	height: 10rpx;
	border-radius: 50%;
	background: #f5a623;
	margin-top: 14rpx;
	flex-shrink: 0;
}

.tip-text {
	flex: 1;
	font-size: 26rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.7;
}

/* ========== 通用 ========== */
.empty-panel {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 300rpx;
}
.empty-panel-text {
	font-size: 26rpx;
	color: rgba(92, 61, 30, 0.4);
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}
</style>

<style>
@import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+SC:wght@200;400;600&family=ZCOOL+XiaoWei&family=Cormorant+Garamond:wght@300;400&display=swap');

.main-content {
	background: linear-gradient(180deg, #fdf8f0 0%, #fef5eb 30%, #f5e6d3 100%) !important;
}

::-webkit-scrollbar {
	width: 8px;
}
::-webkit-scrollbar-track {
	background: transparent;
}
::-webkit-scrollbar-thumb {
	background: rgba(224, 122, 44, 0.2);
	border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
	background: rgba(224, 122, 44, 0.4);
}
</style>
