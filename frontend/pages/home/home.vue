<template>
	<AppLayout ref="layout" :show-back="false">
		<CursorTrail />

		<view class="home-root">

			<!-- Hero Section -->
			<view class="hero-section">
				<view class="hero-glow hero-glow-1"></view>
				<view class="hero-glow hero-glow-2"></view>
				<view class="hero-deco-line"></view>
				<text class="hero-title">食　光</text>
				<text class="hero-subtitle">SAVOR THE MOMENT</text>
				<view class="hero-deco-line"></view>
			</view>

			<!-- Today Recommended -->
			<view class="content-section">
				<view class="section-header">
					<text class="section-label">今日推荐</text>
					<view class="section-line"></view>
				</view>
				<view class="featured-grid">
					<view
						class="dish-card"
						v-for="(dish, index) in featuredDishes"
						:key="index"
						@click="goToDish(dish)"
					>
						<view class="dish-cover">
							<template v-if="dish.image">
								<image class="dish-image" :src="dish.image" mode="aspectFill" @error="dish.image = ''"></image>
								<view class="dish-scrim"></view>
								<view class="dish-meta">
									<text class="dish-name">{{ dish.name }}</text>
									<text class="dish-tag">#{{ dishTag(dish) }}</text>
								</view>
							</template>
							<view v-else class="dish-placeholder">
								<view class="placeholder-icon"></view>
								<text class="placeholder-name">{{ dish.name }}</text>
								<text class="dish-tag placeholder-tag">#{{ dishTag(dish) }}</text>
							</view>

							<text class="dish-fav">♡</text>
						</view>

						<view class="dish-info">
							<text class="dish-title">{{ dish.name }}</text>
							<text class="dish-desc">{{ cleanSummary(dish.summary) }}</text>
						</view>
					</view>
				</view>
			</view>
		</view>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import CursorTrail from '../../components/CursorTrail.vue'
import { getCategories, getDishesByCategory } from '../../api/dish'
import { cleanSummary, summaryTag } from '../../utils/dishText'

const layout = ref(null)
const featuredDishes = ref([])
const featuredSeed = ref(null)

const dishTag = (dish) => summaryTag(dish.summary, dish.categoryName)

const getTodayKey = () => {
	const now = new Date()
	return `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`
}

const shouldRefreshRecommendations = () => {
	const todayKey = getTodayKey()
	const lastRefresh = localStorage.getItem('lastFeaturedRefresh')
	if (lastRefresh !== todayKey) {
		const now = new Date()
		if (now.getHours() >= 6) {
			return true
		}
	}
	return false
}

const markRefreshed = () => {
	localStorage.setItem('lastFeaturedRefresh', getTodayKey())
}

const pickRandom = (arr, count, seed) => {
	const shuffled = [...arr]
	const random = seed != null ? mulberry32(seed) : Math.random
	for (let i = shuffled.length - 1; i > 0; i--) {
		const j = Math.floor(random() * (i + 1));
		[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
	}
	return shuffled.slice(0, count)
}

function mulberry32(a) {
	return function() {
		a |= 0; a = a + 0x6D2B79F5 | 0
		let t = Math.imul(a ^ a >>> 15, 1 | a)
		t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t
		return ((t ^ t >>> 14) >>> 0) / 4294967296
	}
}

async function loadFeaturedDishes() {
	try {
		const categories = await getCategories()
		if (!categories || categories.length === 0) return

		const allDishes = []
		const categoryPromises = categories.map(cat =>
			getDishesByCategory(cat.id).then(res => {
				const list = res.list || []
				list.forEach(dish => {
					allDishes.push({
						name: dish.name,
						summary: dish.summary || '',
						image: dish.image || '',
						categoryId: cat.id,
						categoryName: cat.name,
					})
				})
			})
		)

		await Promise.all(categoryPromises)

		const seed = shouldRefreshRecommendations() ? Date.now() : (featuredSeed.value || Date.now())
		featuredSeed.value = seed
		featuredDishes.value = pickRandom(allDishes, 4, seed)
		markRefreshed()
	} catch (e) {
		console.error('加载今日推荐失败:', e)
	}
}

const refreshIfNeeded = () => {
	if (shouldRefreshRecommendations()) {
		loadFeaturedDishes()
	}
}

const goToDish = (dish) => {
	uni.navigateTo({
		url: `/pages/dish-detail/dish-detail?category=${dish.categoryId}&dish=${encodeURIComponent(dish.name)}`
	})
}

let refreshTimer = null

onMounted(() => {
	nextTick(() => {
		layout.value?.setSidebarSelection()
	})
	loadFeaturedDishes()

	refreshTimer = setInterval(refreshIfNeeded, 60000)
})

onUnmounted(() => {
	if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.home-root {
	min-height: 100%;
	padding-bottom: 40rpx;
}

/* ===== Hero ===== */
.hero-section {
	position: relative;
	height: 320rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.hero-glow {
	position: absolute;
	border-radius: 50%;
	pointer-events: none;
}

.hero-glow-1 {
	width: 400rpx;
	height: 400rpx;
	top: -80rpx;
	left: 50%;
	margin-left: -200rpx;
	background: radial-gradient(circle, rgba(224, 122, 44, 0.12) 0%, transparent 70%);
}

.hero-glow-2 {
	width: 240rpx;
	height: 240rpx;
	bottom: -40rpx;
	right: 60rpx;
	background: radial-gradient(circle, rgba(224, 122, 44, 0.08) 0%, transparent 70%);
}

.hero-deco-line {
	width: 80rpx;
	height: 2rpx;
	background: linear-gradient(90deg, transparent, rgba(224, 122, 44, 0.5), transparent);
	margin-bottom: 24rpx;
}

.hero-title {
	font-family: 'Ma Shan Zheng', 'STXingkai', 'Xingkai SC', cursive;
	font-size: 96rpx;
	color: #4a2c1a;
	letter-spacing: 36rpx;
	line-height: 1;
	text-shadow: 0 4rpx 16rpx rgba(140, 90, 50, 0.15), 0 0 80rpx rgba(224, 122, 44, 0.08);
}

.hero-subtitle {
	font-family: 'Cormorant Garamond', 'Noto Serif SC', serif;
	font-size: 22rpx;
	font-weight: 300;
	color: #b8763e;
	letter-spacing: 18rpx;
	margin-top: 12rpx;
	text-transform: uppercase;
}

.hero-deco-line:last-child {
	margin-top: 20rpx;
	margin-bottom: 0;
}

/* ===== Section Header ===== */
.content-section {
	padding: 0 32rpx;
	margin-top: 12rpx;
}

.section-header {
	display: flex;
	align-items: center;
	gap: 16rpx;
	margin-bottom: 16rpx;
}

.section-label {
	font-family: 'Ma Shan Zheng', 'ZCOOL XiaoWei', 'STXingkai', 'Xingkai SC', serif;
	font-size: 36rpx;
	color: #4a2c1a;
	font-weight: 400;
	white-space: nowrap;
	letter-spacing: 6rpx;
	text-shadow: 0 2rpx 8rpx rgba(140, 90, 50, 0.1);
}

.section-line {
	flex: 1;
	height: 2rpx;
	background: linear-gradient(90deg, rgba(224, 122, 44, 0.3), transparent);
}

/* ===== Featured Dishes Grid ===== */
.featured-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 12rpx;
}

.dish-card {
	position: relative;
	display: flex;
	flex-direction: row;
	box-sizing: border-box;
	background: #ffffff;
	border: 1rpx solid rgba(23, 23, 23, 0.06);
	border-radius: 16rpx;
	overflow: hidden;
	cursor: pointer;
	box-shadow: 0 6rpx 16rpx rgba(20, 10, 4, 0.05);
	transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s ease, border-color 0.35s ease;
}

.dish-card:hover {
	border-color: rgba(224, 122, 44, 0.35);
	box-shadow: 0 10rpx 24rpx rgba(140, 90, 50, 0.15);
	transform: translateY(-4rpx);
}

.dish-card:active {
	transform: translateY(-2rpx) scale(0.99);
}

.dish-cover {
	position: relative;
	flex: 0 0 30%;
	aspect-ratio: 1 / 1;
	overflow: hidden;
	background: linear-gradient(135deg, #fef5eb 0%, #fde8d0 100%);
}

.dish-image {
	display: block;
	width: 100%;
	height: 100%;
	transition: transform 0.45s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.dish-card:hover .dish-image {
	transform: scale(1.08);
}

.dish-scrim {
	position: absolute;
	left: 0;
	right: 0;
	top: 0;
	bottom: 0;
	background: linear-gradient(180deg, rgba(28, 14, 4, 0) 30%, rgba(28, 14, 4, 0.34) 58%, rgba(28, 14, 4, 0.82) 100%);
}

.dish-meta {
	position: absolute;
	left: 0;
	right: 0;
	bottom: 0;
	padding: 0 14rpx 12rpx;
	display: flex;
	flex-direction: column;
	align-items: flex-start;
}

.dish-name {
	max-width: 100%;
	font-family: 'Noto Serif SC', 'Songti SC', 'STSong', serif;
	font-size: 24rpx;
	color: #ffffff;
	font-weight: 600;
	letter-spacing: 1rpx;
	text-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.5);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.dish-tag {
	margin-top: 4rpx;
	padding: 1rpx 10rpx;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	font-size: 16rpx;
	letter-spacing: 1rpx;
	color: #ffffff;
	background-color: rgba(255, 255, 255, 0.18);
	border: 1rpx solid rgba(255, 255, 255, 0.34);
	border-radius: 999rpx;
}

.dish-placeholder {
	position: absolute;
	left: 0;
	right: 0;
	top: 0;
	bottom: 0;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background: linear-gradient(135deg, #fef5eb 0%, #fde8d0 100%);
}

.placeholder-icon {
	width: 48rpx;
	height: 48rpx;
	background-repeat: no-repeat;
	background-position: center;
	background-size: contain;
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' fill='none' stroke='%238b5e3c' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 16h22a11 11 0 0 1-22 0z'/%3E%3Cpath d='M3 16h26'/%3E%3Cpath d='M20 4l7 7'/%3E%3Cpath d='M23.5 3l6 6'/%3E%3C/svg%3E");
}

.placeholder-name {
	margin-top: 6rpx;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	font-size: 20rpx;
	font-weight: 600;
	color: #8b5e3c;
	letter-spacing: 1rpx;
}

.placeholder-tag {
	margin-top: 4rpx;
	color: #8b5e3c;
	background-color: rgba(255, 255, 255, 0.72);
	border-color: rgba(224, 122, 44, 0.28);
	font-size: 14rpx;
	padding: 1rpx 8rpx;
	border-radius: 999rpx;
	border: 1rpx solid;
}

.dish-fav {
	position: absolute;
	right: 8rpx;
	top: 8rpx;
	width: 36rpx;
	height: 36rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 22rpx;
	line-height: 1;
	color: rgba(224, 122, 44, 0.75);
	background-color: rgba(255, 255, 255, 0.85);
	border-radius: 50%;
	box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.12);
}

.dish-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	justify-content: center;
	padding: 10rpx 14rpx;
	box-sizing: border-box;
	min-width: 0;
}

.dish-title {
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	font-size: 24rpx;
	font-weight: 600;
	color: #4a2c1a;
	letter-spacing: 1rpx;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.dish-desc {
	margin-top: 4rpx;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	font-size: 18rpx;
	color: rgba(92, 61, 30, 0.62);
	line-height: 1.3;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}


</style>

<style>
/* Google Fonts — Artistic Chinese & Latin typefaces */
@import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+SC:wght@200;400;600&family=ZCOOL+XiaoWei&family=Cormorant+Garamond:wght@300;400&display=swap');

/* Global bright warm background */
.main-content {
	background: linear-gradient(180deg, #fdf8f0 0%, #fef5eb 30%, #f5e6d3 100%) !important;
}

:deep(.header) {
	background:
		radial-gradient(ellipse at 80% 20%, rgba(255, 210, 160, 0.5) 0%, transparent 45%),
		radial-gradient(ellipse at 10% 80%, rgba(255, 190, 140, 0.3) 0%, transparent 40%),
		linear-gradient(180deg, #fffaf5 0%, #fef3e6 100%) !important;
	backdrop-filter: none !important;
	-webkit-backdrop-filter: none !important;
	border-radius: 0 0 40rpx 40rpx !important;
	border-bottom: 3rpx solid transparent !important;
	border-image: linear-gradient(90deg, #f0b088, #e07a2c, #d4804a) 1 !important;
	box-shadow: 0 8rpx 32rpx rgba(224, 122, 44, 0.12), 0 2rpx 8rpx rgba(0, 0, 0, 0.04) !important;
	padding: 40rpx 32rpx 80rpx !important;
}
:deep(.greeting) {
	font-family: 'Ma Shan Zheng', 'ZCOOL XiaoWei', 'STXingkai', serif !important;
	color: #5c3d1e !important;
	letter-spacing: 4rpx !important;
	text-shadow: 0 1rpx 2rpx rgba(140, 90, 50, 0.08) !important;
}
:deep(.tips) {
	font-family: 'Cormorant Garamond', 'Noto Serif SC', serif !important;
	color: #8b5e3c !important;
	letter-spacing: 2rpx !important;
	font-weight: 300 !important;
}
:deep(.hamburger-btn) {
	border-radius: 50% !important;
	background: linear-gradient(135deg, #fef5eb, #fde8d0) !important;
	border: 1.5rpx solid rgba(224, 122, 44, 0.2) !important;
	box-shadow: 0 4rpx 16rpx rgba(224, 122, 44, 0.1) !important;
}
:deep(.hamburger-btn:active) { background: linear-gradient(135deg, #fde8d0, #f5d5b8) !important; }
:deep(.hamburger-icon) { color: #d4804a !important; }
:deep(.back-btn) {
	border-radius: 50% !important;
	background: linear-gradient(135deg, #fef5eb, #fde8d0) !important;
	border: 1.5rpx solid rgba(224, 122, 44, 0.2) !important;
	box-shadow: 0 4rpx 16rpx rgba(224, 122, 44, 0.1) !important;
}
:deep(.back-btn:active) { background: linear-gradient(135deg, #fde8d0, #f5d5b8) !important; }
:deep(.back-icon) { color: #d4804a !important; }

/* Override sidebar to warm tones — match preview details */
:deep(.sidebar-drawer) {
	background-color: #fffaf5 !important;
	box-shadow: 4rpx 0 24rpx rgba(140, 90, 50, 0.1) !important;
}
:deep(.drawer-header) {
	background-color: #fef5eb !important;
	border-bottom: 2rpx solid rgba(224, 122, 44, 0.12) !important;
}
:deep(.drawer-title) {
	font-family: 'Ma Shan Zheng', 'ZCOOL XiaoWei', serif !important;
	color: #4a2c1a !important;
	letter-spacing: 4rpx !important;
}
:deep(.section-title) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #4a2c1a !important;
	font-weight: 600 !important;
	letter-spacing: 2rpx !important;
}
:deep(.title-bar) { background-color: #e07a2c !important; }
:deep(.menu-item-text) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #8b5e3c !important;
}
:deep(.parent-text) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #4a2c1a !important;
	font-weight: 600 !important;
}
:deep(.menu-item-selected) {
	background-color: rgba(224, 122, 44, 0.1) !important;
}
:deep(.menu-item-selected .parent-text) { color: #c45d1a !important; }
:deep(.section-divider) { background-color: #fef0e0 !important; }
:deep(.sub-text) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #a07050 !important;
}
:deep(.arrow-icon) { color: rgba(224, 122, 44, 0.5) !important; }
:deep(.expand-drawer) { background-color: #fff7f0 !important; }
:deep(.user-panel) {
	background-color: #fef5eb !important;
	border-top: 2rpx solid rgba(224, 122, 44, 0.12) !important;
}
:deep(.user-name) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #4a2c1a !important;
	font-weight: 600 !important;
}
:deep(.user-action) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #a07050 !important;
}
:deep(.home-btn) {
	background-color: #e07a2c !important;
	box-shadow: 0 4rpx 12rpx rgba(224, 122, 44, 0.3) !important;
}
:deep(.home-btn:active) { background-color: #c45d1a !important; }
:deep(.home-icon) { color: #ffffff !important; }
:deep(.bottom-sheet) { background-color: #fffaf5 !important; }
:deep(.sheet-username) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #4a2c1a !important;
	font-weight: 600 !important;
}
:deep(.sheet-name) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #4a2c1a !important;
}
:deep(.sheet-divider) { background-color: #fef0e0 !important; }
:deep(.logout-item .sheet-name) {
	font-family: 'Noto Serif SC', 'Songti SC', serif !important;
	color: #d44040 !important;
}
:deep(.panel-arrow) { color: rgba(224, 122, 44, 0.5) !important; }
:deep(.close-arrow) { color: #a07050 !important; }

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
