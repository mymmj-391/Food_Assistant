<template>
	<AppLayout ref="layout">
		<CursorTrail />
		<scroll-view class="dish-scroll" scroll-y="true" enhanced="true">
			<view v-if="dishList.length === 0 && !loading" class="empty-state">
				<text class="empty-text">该分类暂无菜品</text>
			</view>

			<view v-else class="dish-grid">
				<view
					v-for="dish in dishList"
					:key="dish.id"
					class="dish-card"
					@click="handleDishTap(dish)"
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

						<view class="star-btn" @click.stop="toggleFavorite(dish)">
							<text class="star-icon" :class="{ 'star-active': dish.isFavorite }">★</text>
						</view>
					</view>

					<view class="dish-summary">
						<text>{{ cleanSummary(dish.summary) }}</text>
					</view>
				</view>
			</view>

			<view v-if="loading" class="loading-tip">
				<text>加载中...</text>
			</view>
			<view v-if="dishList.length > 0" class="loading-tip">
				<text>没有更多了</text>
			</view>
		</scroll-view>
	</AppLayout>
</template>

<script setup>
	import { ref, nextTick } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import AppLayout from '../../components/AppLayout.vue'
import CursorTrail from '../../components/CursorTrail.vue'
import { getDishesByCategory } from '../../api/dish'
import { addFavorite, removeFavorite, getFavorites } from '../../api/favorites'
import { cleanSummary, summaryTag } from '../../utils/dishText'

	const layout = ref(null)
	const categoryId = ref('')
	const categoryName = ref('')
	const dishList = ref([])
	const loading = ref(false)
	const favoriteLoading = ref(false)

	const dishTag = (dish) => summaryTag(dish.summary, categoryName.value)

	onLoad((options) => {
		categoryId.value = options.categoryId || ''
		categoryName.value = options.categoryName || '菜品列表'

		nextTick(() => {
			layout.value?.setSidebarSelection({ categoryId: categoryId.value })
		})

		fetchDishes()
	})

	const fetchDishes = async () => {
		if (!categoryId.value) return
		loading.value = true
		try {
			const res = await getDishesByCategory(categoryId.value)
			dishList.value = res.list || []
			layout.value?.setHeader({
			greeting: categoryName.value,
			tip: `共 ${dishList.value.length} 道菜品`
		})
		checkFavorites()
		} catch (e) {
			uni.showToast({
				title: '加载失败，请检查网络',
				icon: 'none'
			})
		} finally {
			loading.value = false
		}
	}

	const handleDishTap = (dish) => {
	uni.navigateTo({
		url: `/pages/dish-detail/dish-detail?category=${categoryId.value}&dish=${encodeURIComponent(dish.name)}`
	})
}

const toggleFavorite = async (dish) => {
	if (favoriteLoading.value) return
	favoriteLoading.value = true
	try {
		if (dish.isFavorite) {
			await removeFavorite({ dish_name: dish.name })
			dish.isFavorite = false
			uni.showToast({ title: '已取消收藏', icon: 'none' })
		} else {
			await addFavorite({
				dish_name: dish.name,
				category_id: categoryId.value,
				category_name: categoryName.value,
				image: dish.image || ''
			})
			dish.isFavorite = true
			uni.showToast({ title: '已添加收藏', icon: 'none' })
		}
	} catch (e) {
		uni.showToast({ title: '操作失败', icon: 'none' })
	} finally {
		favoriteLoading.value = false
	}
}

const checkFavorites = async () => {
	try {
		const favorites = await getFavorites()
		const favSet = new Set(favorites.map(f => f.dish_name))
		dishList.value.forEach(dish => {
			dish.isFavorite = favSet.has(dish.name)
		})
	} catch (e) {}
}
</script>

<style scoped>
	.dish-scroll {
		flex: 1;
		height: 100%;
		padding: 20rpx;
		box-sizing: border-box;
		-webkit-overflow-scrolling: touch;
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

	.dish-grid {
		display: flex;
		flex-wrap: wrap;
		margin: 0 -12rpx;
	}

	.dish-card {
		position: relative;
		display: flex;
		flex-direction: column;
		width: calc(25% - 24rpx);
		margin: 12rpx;
		box-sizing: border-box;
		background-color: #ffffff;
		border: 1rpx solid rgba(23, 23, 23, 0.06);
		border-radius: 20rpx;
		overflow: hidden;
		cursor: pointer;
		box-shadow: 0 8rpx 20rpx rgba(20, 10, 4, 0.05);
		transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s ease, border-color 0.35s ease;
	}
	.dish-card:hover {
		transform: translateY(-5rpx);
		box-shadow: 0 14rpx 34rpx rgba(140, 90, 50, 0.18);
		border-color: rgba(224, 122, 44, 0.35);
	}
	.dish-card:active {
		transform: translateY(-2rpx);
		box-shadow: 0 8rpx 20rpx rgba(140, 90, 50, 0.12);
	}

	.dish-cover {
		position: relative;
		flex: 0 0 auto;
		aspect-ratio: 4 / 3;
		overflow: hidden;
		background-color: #f0f0f0;
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
		padding: 0 12rpx 12rpx;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
	}

	.dish-name {
		max-width: 100%;
		font-size: 28rpx;
		font-weight: bold;
		color: #ffffff;
		text-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.5);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}

	.dish-tag {
		margin-top: 6rpx;
		padding: 2rpx 12rpx;
		font-size: 18rpx;
		color: #ffffff;
		background-color: rgba(255, 255, 255, 0.18);
		border: 1rpx solid rgba(255, 255, 255, 0.34);
		border-radius: 999rpx;
		opacity: 0.75;
		transition: opacity 0.3s ease, transform 0.3s ease, background-color 0.3s ease;
	}
	.dish-card:hover .dish-tag {
		opacity: 1;
		transform: translateY(-2rpx);
		background-color: rgba(255, 255, 255, 0.3);
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
		width: 64rpx;
		height: 64rpx;
		background-repeat: no-repeat;
		background-position: center;
		background-size: contain;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' fill='none' stroke='%238b5e3c' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 16h22a11 11 0 0 1-22 0z'/%3E%3Cpath d='M3 16h26'/%3E%3Cpath d='M20 4l7 7'/%3E%3Cpath d='M23.5 3l6 6'/%3E%3C/svg%3E");
	}

	.placeholder-name {
		margin-top: 10rpx;
		font-size: 28rpx;
		font-weight: bold;
		color: #8b5e3c;
		letter-spacing: 1rpx;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}

	.placeholder-tag {
		margin-top: 8rpx;
		color: #8b5e3c;
		background-color: rgba(255, 255, 255, 0.72);
		border-color: rgba(224, 122, 44, 0.28);
		opacity: 0.8;
	}
	.dish-card:hover .placeholder-tag {
		opacity: 1;
		background-color: rgba(255, 255, 255, 0.92);
	}

	.dish-summary {
		flex: 1 1 auto;
		padding: 14rpx 16rpx;
		box-sizing: border-box;
		overflow: hidden;
	}
	.dish-summary text {
		font-size: 20rpx;
		color: rgba(92, 61, 30, 0.62);
		line-height: 1.4;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}

	.star-btn {
		position: absolute;
		right: 10rpx;
		top: 10rpx;
		width: 44rpx;
		height: 44rpx;
		display: flex;
		justify-content: center;
		align-items: center;
		background-color: rgba(255, 255, 255, 0.85);
		border-radius: 50%;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.12);
		transition: transform 0.3s ease, background-color 0.3s ease;
	}
	.dish-card:hover .star-btn {
		transform: scale(1.12);
		background-color: rgba(255, 255, 255, 1);
	}
	.star-icon {
		font-size: 30rpx;
		color: #ddd;
		line-height: 1;
	}
	.star-active {
		color: #e07a2c;
	}

	.loading-tip {
		text-align: center;
		padding: 30rpx 0;
		font-size: 24rpx;
		color: rgba(92, 61, 30, 0.5);
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
