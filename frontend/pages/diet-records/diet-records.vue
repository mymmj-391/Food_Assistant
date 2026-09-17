<template>
	<AppLayout ref="layout">
		<CursorTrail />
		<view class="records-container">
			<view v-if="loading" class="loading">
				<text>加载中...</text>
			</view>
			<view v-else-if="records.length === 0" class="empty">
				<text class="empty-icon">📋</text>
				<text class="empty-text">暂无浏览记录</text>
				<text class="empty-tip">浏览过的菜品会自动记录在这里</text>
			</view>
			<view v-else class="records-list">
			<view class="list-header">
				<text class="list-count">共 {{ records.length }} 条记录</text>
				<view class="clear-btn" @click="clearAllRecords">
					<text class="clear-text">清空全部</text>
				</view>
			</view>
			<view v-for="group in groupedRecords" :key="group.date" class="record-group">
					<text class="group-date">{{ group.date }}</text>
					<view
						v-for="item in group.items"
						:key="item.id"
						class="record-item"
					>
						<view class="item-main" @click="goToDish(item)">
							<image v-if="item.image" class="item-image" :src="item.image" mode="aspectFill"></image>
							<view v-else class="item-image placeholder">
								<text class="placeholder-text">🍽</text>
							</view>
							<view class="item-info">
								<text class="item-name">{{ item.dish_name }}</text>
								<text class="item-category">{{ item.category_name }}</text>
							</view>
							<text class="item-time">{{ formatTime(item.viewed_at) }}</text>
						</view>
						<view class="item-delete" @click.stop="deleteRecord(item)">
							<text class="delete-icon">×</text>
						</view>
					</view>
				</view>
			</view>
		</view>
	</AppLayout>
</template>

<script setup>
	import { ref, computed, onMounted, nextTick } from 'vue'
	import AppLayout from '../../components/AppLayout.vue'
	import CursorTrail from '../../components/CursorTrail.vue'
	import { getDietRecords, deleteDietRecord } from '../../api/favorites.js'

	const layout = ref(null)
	const records = ref([])
	const loading = ref(false)

	const groupedRecords = computed(() => {
		const groups = {}
		records.value.forEach(item => {
			const date = (item.viewed_at || '').split(' ')[0] || '未知日期'
			if (!groups[date]) {
				groups[date] = { date, items: [] }
			}
			groups[date].items.push(item)
		})
		return Object.values(groups).sort((a, b) => b.date.localeCompare(a.date))
	})

	const formatTime = (viewedAt) => {
		if (!viewedAt) return ''
		const parts = viewedAt.split(' ')
		return parts[1] ? parts[1].slice(0, 5) : viewedAt
	}

	const fetchRecords = async () => {
		loading.value = true
		try {
			const res = await getDietRecords()
			records.value = res
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

	const deleteRecord = async (item) => {
		uni.showModal({
			title: '提示',
			content: '确定要删除这条记录吗？',
			success: async (res) => {
				if (res.confirm) {
					try {
						await deleteDietRecord(item.id)
						records.value = records.value.filter(r => r.id !== item.id)
						uni.showToast({ title: '已删除', icon: 'none' })
					} catch (e) {
						uni.showToast({ title: '删除失败', icon: 'none' })
					}
				}
			}
		})
	}

	const clearAllRecords = () => {
		if (records.value.length === 0) {
			uni.showToast({ title: '暂无记录可清除', icon: 'none' })
			return
		}
		uni.showModal({
			title: '确认清空',
			content: '确定要清除全部浏览记录吗？此操作不可撤销。',
			success: async (res) => {
				if (res.confirm) {
					try {
						const ids = records.value.map(r => r.id)
						await Promise.all(ids.map(id => deleteDietRecord(id)))
						records.value = []
						uni.showToast({ title: '已清空', icon: 'none' })
					} catch (e) {
						uni.showToast({ title: '清空失败', icon: 'none' })
					}
				}
			}
		})
	}

	onMounted(() => {
		nextTick(() => {
			layout.value?.setHeader({ greeting: '饮食记录', tip: '' })
			layout.value?.setSidebarSelection()
		})
		fetchRecords()
	})
</script>

<style scoped>
	.records-container {
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
	.records-list {
		display: flex;
		flex-direction: column;
		gap: 30rpx;
	}
	.list-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 10rpx 10rpx 0;
	}
	.list-count {
		font-size: 24rpx;
		color: rgba(92, 61, 30, 0.5);
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.clear-btn {
		padding: 8rpx 20rpx;
		border-radius: 20rpx;
		background-color: rgba(224, 122, 44, 0.1);
		border: 1rpx solid rgba(224, 122, 44, 0.2);
		transition: all 0.2s;
	}
	.clear-btn:active {
		background-color: rgba(224, 122, 44, 0.2);
		transform: scale(0.96);
	}
	.clear-text {
		font-size: 22rpx;
		color: #e07a2c;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.record-group {
		display: flex;
		flex-direction: column;
		gap: 16rpx;
	}
	.group-date {
		font-size: 26rpx;
		color: #8b5e3c;
		padding: 0 10rpx;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
		font-weight: 600;
	}
	.record-item {
		display: flex;
		align-items: center;
		padding: 20rpx;
		background-color: #ffffff;
		border: 1px solid rgba(224, 122, 44, 0.1);
		border-radius: 16rpx;
		box-shadow: 0 4rpx 16rpx rgba(140, 90, 50, 0.06);
	}
	.item-main {
		flex: 1;
		display: flex;
		align-items: center;
	}
	.item-delete {
		flex-shrink: 0;
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-left: 16rpx;
		border-radius: 50%;
		background-color: rgba(224, 122, 44, 0.08);
	}
	.item-delete:active {
		background-color: rgba(224, 122, 44, 0.15);
	}
	.delete-icon {
		font-size: 36rpx;
		color: #e07a2c;
		font-weight: bold;
	}
	.item-image {
		width: 100rpx;
		height: 100rpx;
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
		font-size: 40rpx;
	}
	.item-info {
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	.item-name {
		font-size: 28rpx;
		font-weight: bold;
		color: #3d2415;
		margin-bottom: 6rpx;
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.item-category {
		font-size: 22rpx;
		color: rgba(92, 61, 30, 0.6);
		font-family: 'Noto Serif SC', 'Songti SC', serif;
	}
	.item-time {
		font-size: 22rpx;
		color: rgba(92, 61, 30, 0.45);
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
