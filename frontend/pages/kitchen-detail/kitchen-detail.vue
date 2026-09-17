<template>
	<AppLayout ref="layout">
		<CursorTrail />
		<scroll-view class="detail-scroll" scroll-y="true">
			<view v-if="loading" class="loading-state">
				<text>加载中...</text>
			</view>

			<view v-else-if="!tip" class="empty-state">
				<text class="empty-text">该技巧不存在</text>
			</view>

			<view v-else class="detail-container">
				<view class="tip-header">
					<view class="header-icon">🧑‍🍳</view>
					<text class="tip-name">{{ tip.name }}</text>
					<text class="tip-subtitle">厨房技巧</text>
				</view>

				<view v-if="parsed.utensils" class="card utensil-card">
					<view class="card-header">
						<view class="header-icon-wrap">
							<text class="card-icon">🍳</text>
						</view>
						<view class="header-text">
							<text class="card-title">器具准备</text>
							<text class="card-desc">开始之前，先确认这些</text>
						</view>
					</view>
					<view class="card-body">
						<view class="utensil-list">
							<view v-for="(block, idx) in utensilBlocks" :key="idx" class="block-item">
								<view v-if="block.type === 'text'" class="block-text">{{ block.text }}</view>
								<view v-else-if="block.type === 'list'" class="utensil-grid">
									<view v-for="(item, i) in block.items" :key="i" class="utensil-item">
										<text class="utensil-bullet">·</text>
										<text class="utensil-text">{{ item }}</text>
									</view>
								</view>
								<view v-else-if="block.type === 'subtitle'" class="block-subtitle">{{ block.text }}</view>
							</view>
						</view>
					</view>
				</view>

				<view v-if="parsed.process" class="card process-card">
					<view class="card-header">
						<view class="header-icon-wrap process-icon-wrap">
							<text class="card-icon">📋</text>
						</view>
						<view class="header-text">
							<text class="card-title">操作流程</text>
							<text class="card-desc">按顺序执行以下步骤</text>
						</view>
					</view>
					<view class="card-body">
						<view class="timeline">
							<view v-for="(block, idx) in processBlocks" :key="idx" class="timeline-block">
								<view v-if="block.type === 'text'" class="timeline-text">{{ block.text }}</view>
								<view v-else-if="block.type === 'list'" class="timeline-list">
									<view v-for="(item, i) in block.items" :key="i" class="timeline-item">
										<view class="timeline-dot">{{ i + 1 }}</view>
										<view class="timeline-content">
											<text class="timeline-item-text">{{ item }}</text>
										</view>
									</view>
								</view>
								<view v-else-if="block.type === 'subtitle'" class="timeline-subtitle">{{ block.text }}</view>
							</view>
						</view>
					</view>
				</view>

				<view v-if="parsed.warnings" class="card warning-card">
					<view class="card-header">
						<view class="header-icon-wrap warning-icon-wrap">
							<text class="card-icon">⚠️</text>
						</view>
						<view class="header-text">
							<text class="card-title">注意事项</text>
							<text class="card-desc">安全操作，避免意外</text>
						</view>
					</view>
					<view class="card-body">
						<view class="warning-box">
							<view v-for="(block, idx) in warningBlocks" :key="idx" class="block-item">
								<view v-if="block.type === 'text'" class="warning-text">{{ block.text }}</view>
								<view v-else-if="block.type === 'list'" class="warning-list">
									<view v-for="(item, i) in block.items" :key="i" class="warning-row">
										<text class="warning-icon">!</text>
										<text class="warning-item-text">{{ item }}</text>
									</view>
								</view>
								<view v-else-if="block.type === 'subtitle'" class="warning-subtitle">{{ block.text }}</view>
							</view>
						</view>
					</view>
				</view>

				<view v-for="(section, idx) in parsed.extra" :key="idx" class="card extra-card">
					<view class="card-header">
						<view class="header-icon-wrap extra-icon-wrap">
							<text class="card-icon">📖</text>
						</view>
						<view class="header-text">
							<text class="card-title">{{ section.title }}</text>
						</view>
					</view>
					<view class="card-body">
						<view v-for="(block, bIdx) in getExtraBlocks(section.content)" :key="bIdx" class="block-item">
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
			</view>
		</scroll-view>
	</AppLayout>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import AppLayout from '../../components/AppLayout.vue'
import CursorTrail from '../../components/CursorTrail.vue'
import { getKitchenTipDetail } from '../../api/kitchen'
import { parseTipContent, mdToBlocks } from '../../utils/mdParser'

const layout = ref(null)
const tip = ref(null)
const loading = ref(false)

const parsed = computed(() => {
	if (!tip.value?.content) return { utensils: '', process: '', warnings: '', extra: [] }
	return parseTipContent(tip.value.content)
})

const utensilBlocks = computed(() => mdToBlocks(parsed.value.utensils))
const processBlocks = computed(() => mdToBlocks(parsed.value.process))
const warningBlocks = computed(() => mdToBlocks(parsed.value.warnings))

const getExtraBlocks = (content) => mdToBlocks(content)

onLoad((options) => {
	const tipId = options.tipId || ''
	const tipName = decodeURIComponent(options.tipName || '')

	nextTick(() => {
		layout.value?.setHeader({ greeting: tipName || '厨房技巧', tip: '' })
		layout.value?.setSidebarSelection({ tipId: tipId || tipName })
	})

	if (tipName) {
		fetchTipDetail(tipName)
	}
})

const fetchTipDetail = async (tipName) => {
	loading.value = true
	try {
		const res = await getKitchenTipDetail(tipName)
		if (res && res.name) {
			tip.value = { name: res.name, content: res.content }
		}
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

.tip-header {
	text-align: center;
	margin-bottom: 30rpx;
	padding: 20rpx 0;
}
.header-icon {
	font-size: 60rpx;
	margin-bottom: 12rpx;
}
.tip-name {
	font-size: 44rpx;
	font-weight: bold;
	color: #4a2c1a;
	font-family: 'Ma Shan Zheng', 'ZCOOL XiaoWei', 'STXingkai', serif;
	letter-spacing: 4rpx;
	display: block;
}
.tip-subtitle {
	font-size: 24rpx;
	color: #8b7355;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	margin-top: 8rpx;
	display: block;
}

.card {
	background: #ffffff;
	border-radius: 24rpx;
	margin-bottom: 24rpx;
	box-shadow: 0 8rpx 32rpx rgba(140, 90, 50, 0.06);
	overflow: hidden;
	border: 1px solid rgba(224, 122, 44, 0.08);
}

.card-header {
	display: flex;
	align-items: center;
	padding: 30rpx 30rpx 20rpx;
	gap: 16rpx;
}

.header-icon-wrap {
	width: 64rpx;
	height: 64rpx;
	border-radius: 16rpx;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-shrink: 0;
	background: linear-gradient(135deg, #fef5eb, #fde8d0);
}
.process-icon-wrap {
	background: linear-gradient(135deg, #e8f4fd, #d4e8f7);
}
.warning-icon-wrap {
	background: linear-gradient(135deg, #fff3e0, #ffe0b2);
}
.extra-icon-wrap {
	background: linear-gradient(135deg, #f3e8ff, #e0d4f5);
}

.card-icon {
	font-size: 32rpx;
}

.header-text {
	flex: 1;
}
.card-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #4a2c1a;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	display: block;
}
.card-desc {
	font-size: 22rpx;
	color: #8b7355;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	margin-top: 4rpx;
	display: block;
}

.card-body {
	padding: 0 30rpx 30rpx;
}

.utensil-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.utensil-grid {
	display: flex;
	flex-direction: column;
	gap: 10rpx;
}

.utensil-item {
	display: flex;
	align-items: flex-start;
	gap: 8rpx;
	padding: 8rpx 16rpx;
	background: #fffdf9;
	border-radius: 8rpx;
}
.utensil-bullet {
	color: #e07a2c;
	font-size: 28rpx;
	font-weight: bold;
}
.utensil-text {
	flex: 1;
	font-size: 28rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.6;
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

.timeline {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
	position: relative;
}

.timeline-block {
	line-height: 1.8;
}

.timeline-text {
	font-size: 28rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	white-space: pre-wrap;
	word-break: break-word;
}

.timeline-subtitle {
	font-size: 30rpx;
	font-weight: bold;
	color: #4a2c1a;
	margin-top: 16rpx;
	margin-bottom: 8rpx;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.timeline-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
	padding-left: 10rpx;
}

.timeline-item {
	display: flex;
	gap: 20rpx;
	position: relative;
}

.timeline-item::before {
	content: '';
	position: absolute;
	left: 20rpx;
	top: 56rpx;
	bottom: -20rpx;
	width: 2rpx;
	background: linear-gradient(180deg, rgba(224, 122, 44, 0.3), rgba(224, 122, 44, 0.05));
}

.timeline-item:last-child::before {
	display: none;
}

.timeline-dot {
	width: 44rpx;
	height: 44rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #4a90d9, #357abd);
	color: #fff;
	font-size: 22rpx;
	font-weight: bold;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-shrink: 0;
	margin-top: 4rpx;
	z-index: 1;
}

.timeline-content {
	flex: 1;
	background: #f8fbfe;
	padding: 16rpx 20rpx;
	border-radius: 12rpx;
	border-left: 3rpx solid #4a90d9;
}

.timeline-item-text {
	font-size: 28rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.7;
}

.warning-card {
	border-color: rgba(255, 152, 0, 0.15);
}

.warning-box {
	background: linear-gradient(135deg, #fffbf0 0%, #fff5e0 100%);
	border-radius: 16rpx;
	padding: 24rpx;
	border: 1px solid rgba(255, 152, 0, 0.15);
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

.warning-text {
	font-size: 28rpx;
	color: #3d2415;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.8;
	white-space: pre-wrap;
	word-break: break-word;
}

.warning-subtitle {
	font-size: 30rpx;
	font-weight: bold;
	color: #e65100;
	margin-top: 16rpx;
	margin-bottom: 8rpx;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
}

.warning-list {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.warning-row {
	display: flex;
	align-items: flex-start;
	gap: 12rpx;
	padding: 12rpx 16rpx;
	background: rgba(255, 255, 255, 0.6);
	border-radius: 8rpx;
}

.warning-icon {
	width: 32rpx;
	height: 32rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #ff9800, #f57c00);
	color: #fff;
	font-size: 20rpx;
	font-weight: bold;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-shrink: 0;
}

.warning-item-text {
	flex: 1;
	font-size: 28rpx;
	color: #5d4037;
	font-family: 'Noto Serif SC', 'Songti SC', serif;
	line-height: 1.7;
}

.extra-card {
	border-color: rgba(156, 39, 176, 0.1);
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
