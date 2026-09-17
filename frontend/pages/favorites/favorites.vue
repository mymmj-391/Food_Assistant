<template>
	<AppLayout ref="layout">
		<CursorTrail />
		<view class="favorites-container">
			<view v-if="loading" class="loading">
				<text>加载中...</text>
			</view>
			<view v-else-if="favorites.length === 0" class="empty">
				<text class="empty-icon">☆</text>
				<text class="empty-text">暂无收藏</text>
				<text class="empty-tip">点击菜品卡片上的五角星添加收藏</text>
			</view>
			<view v-else class="favorites-list">
				<view class="favorites-count">
					<text class="count-text">共 {{ favorites.length }} 条收藏</text>
				</view>
				<view
					v-for="item in favorites"
					:key="item.id"
					class="favorite-item"
					@click="goToDish(item)"
				>
					<image v-if="item.image" class="item-image" :src="item.image" mode="aspectFill"></image>
					<view v-else class="item-image placeholder">
						<text class="placeholder-text">🍽</text>
					</view>
					<view class="item-info">
						<text class="item-name">{{ item.dish_name }}</text>
						<text class="item-category">{{ item.category_name }}</text>
						<text class="item-time">{{ formatTime(item.created_at) }}</text>
					</view>
					<view class="item-action" @click.stop="removeFavorite(item)">
						<text class="star-filled">★</text>
					</view>
				</view>
			</view>
		</view>
	</AppLayout>
</template>

<script setup>
	import { ref, onMounted, nextTick } from 'vue'
	import AppLayout from '../../components/AppLayout.vue'
	import CursorTrail from '../../components/CursorTrail.vue'
	import { getFavorites, removeFavorite as removeFavoriteApi } from '../../api/favorites.js'

	const layout = ref(null)
	const favorites = ref([])
	const loading = ref(false)

	const formatTime = (timeStr) => {
		if (!timeStr) return ''
		const date = new Date(timeStr)
		const now = new Date()
		const diff = now - date
		if (diff < 60000) return '刚刚'
		if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
		if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
		if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
		return date.toLocaleDateString()
	}

	const fetchFavorites = async () => {
		loading.value = true
		try {
			const res = await getFavorites()
			favorites.value = res
		} catch (e) {
			uni.showToast({ title: '加载失败', icon: 'none' })
		} finally {
			loading.value = false
		}
	}

	const goToDish = (item) => {
		uni.navigateTo({
			url: `/pages/dish-detail/dish-detail?category=${item.category_id}&dish=${encodeURIComponent(item.dish_name)}`
		})
	}

	const removeFavorite = async (item) => {
	try {
		await removeFavoriteApi({ dish_name: item.dish_name })
		favorites.value = favorites.value.filter(f => f.id !== item.id)
			uni.showToast({ title: '已取消收藏', icon: 'none' })
		} catch (e) {
			uni.showToast({ title: '操作失败', icon: 'none' })
		}
	}

	onMounted(() => {
		nextTick(() => {
			layout.value?.setHeader({ greeting: '我的收藏', tip: '' })
			layout.value?.setSidebarSelection()
		})
		fetchFavorites()
	})
</script>

<style scoped>
	.favorites-container {
		padding: 20rpx;
		min-height: 80vh;
	}
	.loading {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 200rpx;
		color: rgba(92, 61, 30, 0.5);
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.empty {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 60vh;
	}
	.empty-icon {
		font-size: 100rpx;
		color: rgba(224, 122, 44, 0.3);
		margin-bottom: 20rpx;
	}
	.empty-text {
		font-size: 32rpx;
		color: rgba(92, 61, 30, 0.5);
		margin-bottom: 10rpx;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.empty-tip {
		font-size: 24rpx;
		color: rgba(92, 61, 30, 0.35);
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.favorites-list {
		display: flex;
		flex-direction: column;
		gap: 20rpx;
	}
	.favorites-count {
		padding: 16rpx 24rpx;
		background: linear-gradient(135deg, #fef5eb 0%, #fde8d0 100%);
		border-radius: 12rpx;
		border: 1px solid rgba(224, 122, 44, 0.12);
	}
	.count-text {
		font-size: 26rpx;
		color: #8b5e3c;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
		font-weight: 600;
	}
	.favorite-item {
		display: flex;
		align-items: center;
		padding: 20rpx;
		background-color: #ffffff;
		border: 1px solid rgba(224, 122, 44, 0.1);
		border-radius: 16rpx;
		box-shadow: 0 4rpx 16rpx rgba(140, 90, 50, 0.06);
	}
	.item-image {
		width: 120rpx;
		height: 120rpx;
		border-radius: 12rpx;
		margin-right: 20rpx;
	}
	.item-image.placeholder {
		background: linear-gradient(135deg, #fef5eb 0%, #fde8d0 100%);
		display: flex;
		justify-content: center;
		align-items: center;
	}
	.placeholder-text {
		font-size: 48rpx;
	}
	.item-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	.item-name {
		font-size: 30rpx;
		font-weight: bold;
		color: #3d2415;
		margin-bottom: 8rpx;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.item-category {
		font-size: 24rpx;
		color: rgba(92, 61, 30, 0.6);
		margin-bottom: 8rpx;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.item-time {
		font-size: 22rpx;
		color: rgba(92, 61, 30, 0.45);
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.item-action {
		padding: 20rpx;
	}
	.star-filled {
		font-size: 48rpx;
		color: #e07a2c;
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
