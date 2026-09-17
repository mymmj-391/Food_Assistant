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
					<view v-if="images.length" class="image-swiper" :style="{ height: imageHeight + 'rpx' }">
						<swiper :indicator-dots="images.length > 1" :autoplay="images.length > 1" :interval="3000" :duration="500" class="swiper">
							<swiper-item v-for="(img, idx) in images" :key="idx">
								<image class="swiper-image" :src="img" mode="aspectFill" @error="onImageError(idx)" @load="onImageLoad($event, idx)"></image>
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
							<view v-if="parsed.ingredients" class="content-card">
								<view class="section-list">
									<view v-for="(block, idx) in ingredientBlocks" :key="idx" class="block-item">
										<view v-if="block.type === 'text'" class="block-text">{{ block.text }}</view>
										<view v-else-if="block.type === 'list'" class="block-list">
											<view v-for="(item, i) in block.items" :key="i" class="list-row">
												<text class="list-bullet"></text>
												<text class="list-text">{{ item }}</text>
											</view>
										</view>
										<view v-else-if="block.type === 'subtitle'" class="block-subtitle">{{ block.text }}</view>
									</view>
								</view>
							</view>
							<view v-else class="empty-panel">
								<text class="empty-panel-text">暂无食材信息</text>
							</view>
						</view>

						<view v-if="activeTab === 'steps'" class="tab-panel">
							<view v-if="stepBlocks.length" class="content-card">
								<view class="step-list">
									<view v-for="(block, idx) in stepBlocks" :key="idx" class="step-block">
										<view v-if="block.type === 'text'" class="step-text">{{ block.text }}</view>
										<view v-else-if="block.type === 'list'" class="step-ordered-list">
											<view v-for="(item, i) in block.items" :key="i" class="step-item">
												<view class="step-number">{{ i + 1 }}</view>
												<text class="step-item-text">{{ item }}</text>
											</view>
										</view>
										<view v-else-if="block.type === 'subtitle'" class="step-subtitle">{{ block.text }}</view>
									</view>
								</view>
							</view>
							<view v-else class="empty-panel">
								<text class="empty-panel-text">暂无步骤信息</text>
							</view>
						</view>

						<view v-if="activeTab === 'tips'" class="tab-panel">
							<view v-if="parsed.tips" class="content-card tip-card">
								<view class="tip-header">
									<text class="tip-icon">💡</text>
									<text class="tip-title">小贴士</text>
								</view>
								<view class="section-list">
									<view v-for="(block, idx) in tipBlocks" :key="idx" class="block-item">
										<view v-if="block.type === 'text'" class="block-text">{{ block.text }}</view>
										<view v-else-if="block.type === 'list'" class="block-list">
											<view v-for="(item, i) in block.items" :key="i" class="list-row">
												<text class="list-bullet tip-bullet"></text>
												<text class="list-text">{{ item }}</text>
											</view>
										</view>
										<view v-else-if="block.type === 'subtitle'" class="block-subtitle">{{ block.text }}</view>
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
import { parseDishContent, mdToBlocks } from '../../utils/mdParser'

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

const parsed = computed(() => {
	if (!dish.value?.content) return { ingredients: '', steps: '', tips: '' }
	return parseDishContent(dish.value.content)
})

const ingredientBlocks = computed(() => mdToBlocks(parsed.value.ingredients))
const stepBlocks = computed(() => mdToBlocks(parsed.value.steps))
const tipBlocks = computed(() => mdToBlocks(parsed.value.tips))

const onImageLoad = (e, idx) => {
	if (idx === 0) {
		const { width, height } = e.detail
		if (width > 0 && height > 0) {
			imageHeight.value = Math.min(Math.max(height / width * 600, 300), 800)
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
	overflow: hidden;
	box-shadow: 0 8rpx 32rpx rgba(140, 90, 50, 0.12);
}
.swiper {
	width: 100%;
	height: 100%;
}
.swiper-image {
	width: 100%;
	height: 100%;
}

.tab-container {
	background: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 8rpx 32rpx rgba(140, 90, 50, 0.08);
	overflow: hidden;
	border: 1px solid rgba(224, 122, 44, 0.1);
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

.content-card {
	background: #fffdf9;
	border-radius: 16rpx;
	padding: 30rpx;
	border: 1px solid rgba(224, 122, 44, 0.06);
}

.section-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.block-item {
	line-height: 1.8;
}

.block-text {
	font-size: 28rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.8;
	white-space: pre-wrap;
	word-break: break-word;
}

.block-subtitle {
	font-size: 30rpx;
	font-weight: bold;
	color: #4a2c1a;
	margin-top: 16rpx;
	margin-bottom: 8rpx;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.block-list {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.list-row {
	display: flex;
	align-items: flex-start;
	gap: 12rpx;
}

.list-bullet {
	width: 8rpx;
	height: 8rpx;
	border-radius: 50%;
	background-color: #e07a2c;
	margin-top: 18rpx;
	flex-shrink: 0;
}

.list-text {
	flex: 1;
	font-size: 28rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.7;
}

.tip-bullet {
	background-color: #f5a623;
}

.step-list {
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.step-block {
	line-height: 1.8;
}

.step-text {
	font-size: 28rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	white-space: pre-wrap;
	word-break: break-word;
}

.step-subtitle {
	font-size: 30rpx;
	font-weight: bold;
	color: #4a2c1a;
	margin-top: 16rpx;
	margin-bottom: 8rpx;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.step-ordered-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.step-item {
	display: flex;
	align-items: flex-start;
	gap: 16rpx;
}

.step-number {
	width: 44rpx;
	height: 44rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #e07a2c, #f5a623);
	color: #fff;
	font-size: 24rpx;
	font-weight: bold;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-shrink: 0;
	margin-top: 4rpx;
}

.step-item-text {
	flex: 1;
	font-size: 28rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.7;
}

.tip-card {
	background: linear-gradient(135deg, #fff9f0 0%, #fef5eb 100%);
	border-color: rgba(245, 166, 35, 0.2);
}

.tip-header {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 20rpx;
	padding-bottom: 16rpx;
	border-bottom: 1rpx dashed rgba(245, 166, 35, 0.3);
}
.tip-icon {
	font-size: 36rpx;
}
.tip-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #e07a2c;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

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
