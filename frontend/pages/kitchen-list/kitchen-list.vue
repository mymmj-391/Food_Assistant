<template>
	<AppLayout ref="layout">
		<CursorTrail />
		<scroll-view class="tip-scroll" scroll-y="true" enhanced="true">
			<view v-if="tipList.length === 0 && !loading" class="empty-state">
				<text class="empty-text">该分类暂无技巧</text>
			</view>

			<view v-else class="tip-list">
				<view
					v-for="tip in tipList"
					:key="tip.id"
					class="tip-card"
					@click="handleTipTap(tip)"
				>
					<view class="tip-header">
						<text class="tip-title">{{ tip.name }}</text>
						<text class="tip-arrow">›</text>
					</view>
				</view>
			</view>

			<view v-if="loading" class="loading-tip">
				<text>加载中...</text>
			</view>
		</scroll-view>
	</AppLayout>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import AppLayout from '../../components/AppLayout.vue'
import CursorTrail from '../../components/CursorTrail.vue'
import { getKitchenTips } from '../../api/kitchen'

const layout = ref(null)
const categoryId = ref('')
const categoryName = ref('')
const tipList = ref([])
const loading = ref(false)

onLoad((options) => {
	categoryId.value = options.categoryId || ''
	categoryName.value = options.categoryName || '厨房技巧'

	nextTick(() => {
		layout.value?.setHeader({
			greeting: categoryName.value,
			tip: ''
		})
		layout.value?.setSidebarSelection({ tipId: categoryId.value })
	})

	if (categoryId.value) {
		fetchTips()
	}
})

const fetchTips = async () => {
	loading.value = true
	try {
		const res = await getKitchenTips()
		tipList.value = res.list || []
		layout.value?.setHeader({
			greeting: categoryName.value,
			tip: `共 ${tipList.value.length} 个技巧`
		})
	} catch (e) {
		uni.showToast({
			title: '加载失败，请检查网络',
			icon: 'none'
		})
	} finally {
		loading.value = false
	}
}

const handleTipTap = (tip) => {
	uni.navigateTo({
		url: `/pages/kitchen-detail/kitchen-detail?tipId=${tip.id}&tipName=${tip.name}`
	})
}
</script>

<style scoped>
.tip-scroll {
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

.tip-list {
	display: flex;
	flex-wrap: wrap;
	margin: 0 -16rpx;
}

.tip-card {
	width: calc(25% - 40rpx);
	margin: 20rpx;
	background: #ffffff;
	border: 1px solid rgba(224, 122, 44, 0.12);
	border-radius: 20rpx;
	padding: 30rpx;
	box-sizing: border-box;
	box-shadow: 0 4rpx 20rpx rgba(140, 90, 50, 0.08);
	transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.tip-card:active {
	transform: scale(0.96);
	box-shadow: 0 2rpx 8rpx rgba(140, 90, 50, 0.1);
}

.tip-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}
.tip-title {
	font-size: 28rpx;
	font-weight: 600;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	letter-spacing: 2rpx;
}
.tip-arrow {
	font-size: 28rpx;
	color: rgba(224, 122, 44, 0.5);
}

.loading-tip {
	text-align: center;
	padding: 30rpx 0;
	width: 100%;
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
