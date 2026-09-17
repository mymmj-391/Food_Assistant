<template>
	<view class="app-layout">
		<!-- 悬浮AI聊天按钮 -->
		<FloatingChat />

		<!-- 全局点击水波纹 -->
		<ClickRipple />

		<!-- 全局遮罩层 -->
		<view v-if="isDrawerOpen || isBottomSheetOpen" class="drawer-mask" @click="closeAllDrawers"></view>

		<!-- 左侧总览抽屉 -->
		<view class="sidebar-drawer" :class="{ 'open': isDrawerOpen }" @click="handleSidebarTap">
			<view class="drawer-header">
				<view class="home-btn" @click.stop="goToHome">
					<text class="home-icon">⌂</text>
				</view>
				<text class="drawer-title">总览</text>
			</view>

			<scroll-view class="drawer-menu-scroll" scroll-y="true">
				<!-- 菜品分类 -->
				<view class="menu-section">
					<view class="section-title-box">
						<view class="title-bar"></view>
						<text class="section-title">菜品分类</text>
					</view>
					<view class="menu-list">
						<view
							v-for="(item, index) in dishCategories"
							:key="'dish-' + index"
							class="menu-item parent-item"
							:class="{ 'menu-item-selected': selectedCategory === item.id }"
							@click.stop="handleSubTap(item)"
						>
							<text class="menu-item-text parent-text">{{ item.name }}</text>
						</view>
					</view>
				</view>

				<view class="section-divider"></view>

				<!-- 厨房技巧 -->
				<view class="menu-section">
					<view class="section-title-box">
						<view class="title-bar"></view>
						<text class="section-title">厨房技巧</text>
					</view>
					<view class="menu-list">
						<template v-for="(item, index) in kitchenTips" :key="'tip-' + index">
							<view class="menu-item parent-item" :class="{ 'menu-item-selected': selectedTip === item.id && item.children === null }" @click.stop="handleParentTap(item)">
								<text class="menu-item-text parent-text">{{ item.name }}</text>
								<text v-if="item.children" class="arrow-icon" :class="{ 'arrow-down': expandedItem === item.name }">v</text>
							</view>
							<view class="expand-drawer" :class="{ 'expand-open': expandedItem === item.name }">
								<view
									v-if="item.children"
									v-for="(sub, subIdx) in item.children"
									:key="'sub-' + index + '-' + subIdx"
									class="menu-item sub-item"
									:class="{ 'menu-item-selected': selectedTip === sub.id }"
									@click.stop="handleSubTap({ ...sub, type: 'kitchen' })"
								>
									<text class="menu-item-text sub-text">{{ sub.name }}</text>
								</view>
							</view>
						</template>
					</view>
				</view>
			</scroll-view>

			<!-- 底部用户面板 -->
			<view class="user-panel" @click.stop="toggleBottomSheet">
				<image class="user-avatar" :src="userAvatar" mode="aspectFill"></image>
				<view class="user-info">
					<text class="user-name">{{ username }}</text>
					<text class="user-action">个人设置</text>
				</view>
				<text class="arrow-icon panel-arrow" :class="{ 'arrow-down': isBottomSheetOpen }">^</text>
			</view>
		</view>

		<!-- 底部向上弹出的抽屉 -->
		<view class="bottom-sheet" :class="{ 'open': isBottomSheetOpen }">
			<view class="sheet-user-info">
				<image class="sheet-avatar" :src="userAvatar" mode="aspectFill"></image>
				<text class="sheet-username">{{ username }}</text>
			</view>
			<view class="sheet-close-btn" @click.stop="toggleBottomSheet">
				<text class="close-arrow">v</text>
			</view>
			<view class="sheet-item" @click="goToFavorites">
				<text class="sheet-name">我的收藏</text>
			</view>
			<view class="sheet-item" @click="goToDietRecords">
				<text class="sheet-name">饮食记录</text>
			</view>
			<view class="sheet-divider"></view>
			<view class="sheet-item logout-item" @click="handleLogout">
				<text class="sheet-name">退出登录</text>
			</view>
		</view>

		<!-- 页面主内容区 -->
		<view class="main-content">
			<view class="header">
				<view class="star-deco">✦ ✦ ✦</view>
				<view class="back-btn" :class="{ 'back-btn-hidden': !showBack }" @click="goBack">
					<text class="back-icon"><</text>
				</view>
				<view class="hamburger-btn" @click="toggleDrawer">
					<text class="hamburger-icon">☰</text>
				</view>
				<view class="header-content">
					<text class="greeting">{{ welcome || '主页' }}</text>
					<text class="tips">{{ (tips.length ? tips[0] : '健康饮食，从每一餐开始') }}</text>
				</view>
				<view class="line-deco"></view>
			</view>
			<view class="content-area">
				<slot></slot>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue'
import FloatingChat from './FloatingChat.vue'
import ClickRipple from './ClickRipple.vue'

defineProps({
	showBack: {
		type: Boolean,
		default: true
	}
})

const userInfo = uni.getStorageSync('user') || {}
const username = ref(userInfo.nickname || userInfo.username || '')
const welcome = ref('')
const tips = ref([])
const userAvatar = ref('https://cdn-icons-png.flaticon.com/512/1077/1077114.png')

const isDrawerOpen = ref(false)
const isBottomSheetOpen = ref(false)
const expandedItem = ref('')
const selectedCategory = ref('')
const selectedTip = ref('')

const dishCategories = ref([
	{ name: '素菜', id: 'vegetable_dish', type: 'dish' },
	{ name: '荤菜', id: 'meat_dish', type: 'dish' },
	{ name: '水产', id: 'aquatic', type: 'dish' },
	{ name: '早餐', id: 'breakfast', type: 'dish' },
	{ name: '主食', id: 'staple', type: 'dish' },
	{ name: '汤品', id: 'soup', type: 'dish' },
	{ name: '饮品', id: 'drink', type: 'dish' },
	{ name: '甜品', id: 'dessert', type: 'dish' },
	{ name: '半成品', id: 'semi-finished', type: 'dish' },
	{ name: '调味品', id: 'condiment', type: 'dish' }
])

const kitchenTips = ref([
	{ id: '厨房准备', name: '厨房准备', children: null },
	{ id: '如何洗碗', name: '如何洗碗', children: null },
	{ id: '如何选择现在吃什么', name: '如何选择现在吃什么', children: null },
	{
		id: 'learn',
		name: '学习',
		children: [
			{ id: '去腥', name: '去腥' },
			{ id: '学习凉拌', name: '凉拌' },
			{ id: '学习炒与煎', name: '炒与煎' },
			{ id: '学习焯水', name: '焯水' },
			{ id: '学习煮', name: '煮' },
			{ id: '学习腌', name: '腌' },
			{ id: '学习蒸', name: '蒸' },
			{ id: '微波炉', name: '微波炉' },
			{ id: '空气炸锅', name: '空气炸锅' },
			{ id: '食品安全', name: '食品安全' },
			{ id: '高压力锅', name: '高压力锅' }
		]
	},
	{
		id: 'advanced',
		name: '高级',
		children: [
			{ id: '油温判断技巧', name: '油温判断技巧' },
			{ id: '糖色的炒制', name: '糖色的炒制' },
			{ id: '辅料技巧', name: '辅料技巧' },
			{ id: '高级专业术语', name: '高级专业术语' }
		]
	}
])

const handleParentTap = (item) => {
	if (!item.children) {
		closeAllDrawers()
		selectedTip.value = item.id
		selectedCategory.value = ''
		uni.navigateTo({
			url: `/pages/kitchen-detail/kitchen-detail?tipId=${item.id}&tipName=${encodeURIComponent(item.name)}`
		})
		return
	}
	expandedItem.value = expandedItem.value === item.name ? '' : item.name
}

const toggleDrawer = () => {
	isDrawerOpen.value = !isDrawerOpen.value
	if (!isDrawerOpen.value) {
		isBottomSheetOpen.value = false
		expandedItem.value = ''
	}
}

const goBack = () => {
	const pages = getCurrentPages()
	if (pages.length > 1) {
		uni.navigateBack()
	} else {
		uni.reLaunch({ url: '/pages/home/home' })
	}
}

const toggleBottomSheet = () => {
	isBottomSheetOpen.value = !isBottomSheetOpen.value
}

const handleSidebarTap = () => {
	if (isBottomSheetOpen.value) isBottomSheetOpen.value = false
}

const closeAllDrawers = () => {
	isDrawerOpen.value = false
	isBottomSheetOpen.value = false
	expandedItem.value = ''
}

const handleSubTap = (item) => {
	closeAllDrawers()
	if (item.type === 'dish') {
		selectedCategory.value = item.id
		selectedTip.value = ''
		uni.navigateTo({
			url: `/pages/dish-list/dish-list?categoryId=${item.id}&categoryName=${encodeURIComponent(item.name)}`
		})
	} else if (item.type === 'kitchen') {
		selectedTip.value = item.id
		selectedCategory.value = ''
		uni.navigateTo({
			url: `/pages/kitchen-detail/kitchen-detail?tipId=${item.id}&tipName=${encodeURIComponent(item.name)}`
		})
	} else {
		uni.showToast({ title: `${item.name || item}（待开发）`, icon: 'none' })
	}
}

const goToHome = () => {
	closeAllDrawers()
	uni.reLaunch({ url: '/pages/home/home' })
}

const goToFavorites = () => {
	closeAllDrawers()
	uni.navigateTo({ url: '/pages/favorites/favorites' })
}

const goToDietRecords = () => {
	closeAllDrawers()
	uni.navigateTo({ url: '/pages/diet-records/diet-records' })
}

const handleLogout = () => {
	closeAllDrawers()
	uni.showModal({
		title: '提示',
		content: '确定要退出登录吗？',
		success: (res) => {
			if (res.confirm) {
				uni.removeStorageSync('token')
				uni.removeStorageSync('user')
				uni.reLaunch({ url: '/pages/index/index' })
			}
		}
	})
}

const setHeader = ({ greeting: g, tip: t }) => {
	if (g !== undefined) welcome.value = g
	if (t !== undefined) tips.value = t ? [t] : []
}

const setSidebarSelection = ({ categoryId, tipId } = {}) => {
	selectedCategory.value = categoryId || ''
	selectedTip.value = tipId || ''
}

defineExpose({ setHeader, setSidebarSelection })

</script>

<style scoped>
	.app-layout { min-height: 100vh; background-color: #f5f6fa; }

	.drawer-mask {
		position: fixed; top: 0; left: 0; right: 0; bottom: 0;
		background-color: rgba(0, 0, 0, 0.4); z-index: 998;
	}

	.sidebar-drawer {
		position: fixed; top: 0; left: 0; bottom: 0;
		width: 25vw;
		background: linear-gradient(180deg, #ffffff 0%, #fdf8f0 100%); z-index: 999;
		transform: translateX(-100%); transition: transform 0.3s ease;
		display: flex; flex-direction: column;
		box-shadow: 4rpx 0 20rpx rgba(140, 90, 50, 0.1);
	}
	.sidebar-drawer.open { transform: translateX(0); }

	.drawer-header {
		padding: 40rpx 20rpx 30rpx;
		background: linear-gradient(135deg, #fef5eb 0%, #fde8d0 100%);
		border-bottom: 2rpx solid rgba(224, 122, 44, 0.15);
		flex-shrink: 0;
		display: flex; justify-content: center; align-items: center;
		position: relative;
	}
	.drawer-title { font-size: 32rpx; font-weight: bold; color: #5c3d1e; font-family: 'Ma Shan Zheng', 'ZCOOL XiaoWei', serif; }

	.home-btn {
		position: absolute;
		left: 20rpx;
		top: 50%;
		transform: translateY(-50%);
		width: 60rpx;
		height: 60rpx;
		border-radius: 50%;
		background-color: #e07a2c;
		display: flex;
		justify-content: center;
		align-items: center;
		box-shadow: 0 4rpx 12rpx rgba(224, 122, 44, 0.3);
	}
	.home-btn:active { background-color: #c86422; }
	.home-icon { font-size: 36rpx; color: #fff; line-height: 1; }

	.drawer-menu-scroll { flex: 1; height: 0; padding-bottom: 20rpx; }

	.menu-section { margin-top: 10rpx; }
	.section-title-box { display: flex; align-items: center; padding: 24rpx 20rpx 16rpx; }
	.title-bar { width: 6rpx; height: 28rpx; background-color: #e07a2c; border-radius: 3rpx; margin-right: 12rpx; }
	.section-title { font-size: 28rpx; color: #333; font-weight: bold; }
	.section-divider { height: 16rpx; background-color: #f5f6fa; margin: 10rpx 0; }

	.menu-item { padding: 20rpx 20rpx 20rpx 38rpx; display: flex; align-items: center; }
	.menu-item:active { background-color: rgba(224, 122, 44, 0.05); }
	.menu-item-text { font-size: 24rpx; color: #666; font-family: 'Noto Serif SC', 'Songti SC', serif; }

	.menu-item-selected { background-color: rgba(224, 122, 44, 0.08); }
	.menu-item-selected .parent-text { color: #e07a2c; }

	.parent-item { justify-content: space-between; padding-right: 20rpx; margin-top: 4rpx; }
	.parent-text { font-weight: bold; color: #3d2415; font-size: 26rpx; font-family: 'Noto Serif SC', 'Songti SC', serif; }

	.arrow-icon { font-size: 20rpx; color: #999; transition: transform 0.3s ease; }
	.arrow-down { transform: rotate(180deg); }

	.expand-drawer {
		max-height: 0; overflow: hidden; transition: max-height 0.3s ease;
		background-color: #fcfcfc;
	}
	.expand-open { max-height: 500rpx; }

	.sub-item { padding-left: 56rpx; padding-top: 16rpx; padding-bottom: 16rpx; }
	.sub-text { font-size: 22rpx; color: #8b7355; font-family: 'Noto Serif SC', 'Songti SC', serif; }

	.user-panel {
		display: flex; align-items: center; padding: 40rpx 20rpx;
		background: linear-gradient(135deg, #fef5eb 0%, #fde8d0 100%); border-top: 1rpx solid rgba(224, 122, 44, 0.15); flex-shrink: 0;
	}
	.user-avatar { width: 60rpx; height: 60rpx; border-radius: 50%; margin-right: 15rpx; background-color: #f5e6d3; }
	.user-info { flex: 1; display: flex; flex-direction: column; }
	.user-name { font-size: 24rpx; font-weight: bold; color: #3d2415; font-family: 'Noto Serif SC', 'Songti SC', serif; }
	.user-action { font-size: 18rpx; color: #8b7355; margin-top: 4rpx; font-family: 'Noto Serif SC', 'Songti SC', serif; }
	.panel-arrow { font-size: 24rpx; font-weight: bold; }

	.bottom-sheet {
		position: fixed; left: 0; bottom: 0; width: 25vw;
		background: linear-gradient(180deg, #ffffff 0%, #fdf8f0 100%); z-index: 1000;
		transform: translateY(100%); transition: transform 0.3s ease;
		border-radius: 24rpx 24rpx 0 0;
		padding-bottom: env(safe-area-inset-bottom);
		padding-top: 100rpx;
		box-shadow: 0 -4rpx 20rpx rgba(140, 90, 50, 0.12);
	}
	.bottom-sheet.open { transform: translateY(0); }

	.sheet-user-info {
		position: absolute; top: 10rpx; left: 20rpx;
		display: flex; align-items: center;
	}
	.sheet-avatar { width: 48rpx; height: 48rpx; border-radius: 50%; margin-right: 12rpx; background-color: #f5e6d3; }
	.sheet-username { font-size: 26rpx; font-weight: bold; color: #3d2415; font-family: 'Noto Serif SC', 'Songti SC', serif; }

	.sheet-close-btn {
		position: absolute; top: 8rpx; right: 20rpx;
		width: 40rpx; height: 40rpx;
		display: flex; align-items: center; justify-content: center;
	}
	.close-arrow { font-size: 24rpx; color: #8b7355; font-weight: bold; }

	.sheet-item { display: flex; align-items: center; padding: 30rpx 20rpx; }
	.sheet-name { font-size: 28rpx; color: #3d2415; font-family: 'Noto Serif SC', 'Songti SC', serif; }
	.sheet-divider { height: 16rpx; background-color: rgba(224, 122, 44, 0.08); }
	.logout-item .sheet-name { color: #d32f2f; }

	.main-content {
		display: flex;
		flex-direction: column;
		height: 100vh;
	}

	.header {
		flex-shrink: 0;
		position: sticky;
		top: 0;
		z-index: 10;
		display: flex;
		align-items: center;
		padding: 40rpx 32rpx 80rpx;
		background:
			radial-gradient(ellipse at 80% 20%, rgba(255, 210, 160, 0.5) 0%, transparent 45%),
			radial-gradient(ellipse at 10% 80%, rgba(255, 190, 140, 0.3) 0%, transparent 40%),
			linear-gradient(180deg, #fffaf5 0%, #fef3e6 100%);
		border-radius: 0 0 40rpx 40rpx;
		border-bottom: 3rpx solid transparent;
		border-image: linear-gradient(90deg, #f0b088, #e07a2c, #d4804a) 1;
		box-shadow: 0 8rpx 32rpx rgba(224, 122, 44, 0.12), 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
		transition: box-shadow 0.3s ease, padding 0.3s ease;
		overflow: hidden;
	}
	.star-deco {
		position: absolute;
		top: 16rpx;
		right: 24rpx;
		font-size: 28rpx;
		color: #e07a2c;
		letter-spacing: 8rpx;
		font-family: sans-serif;
		pointer-events: none;
	}
	.line-deco {
		position: absolute;
		bottom: 22rpx;
		left: 50%;
		transform: translateX(-50%);
		width: 80rpx;
		height: 2rpx;
		background: linear-gradient(90deg, transparent, rgba(224, 122, 44, 0.4), transparent);
		border-radius: 2rpx;
		pointer-events: none;
	}
	.back-btn {
		flex-shrink: 0;
		width: 64rpx;
		height: 64rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 16rpx;
		border-radius: 50%;
		background: linear-gradient(135deg, #fef5eb, #fde8d0);
		border: 1.5rpx solid rgba(224, 122, 44, 0.2);
		box-shadow: 0 4rpx 16rpx rgba(224, 122, 44, 0.1);
	}
	.back-btn-hidden {
		visibility: hidden;
		pointer-events: none;
	}
	.back-btn:active {
		background: linear-gradient(135deg, #fde8d0, #f5d5b8);
	}
	.back-icon {
		font-size: 32rpx;
		color: #d4804a;
		font-weight: bold;
	}
	.hamburger-btn {
		flex-shrink: 0;
		width: 64rpx;
		height: 64rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 20rpx;
		border-radius: 50%;
		background: linear-gradient(135deg, #fef5eb, #fde8d0);
		border: 1.5rpx solid rgba(224, 122, 44, 0.2);
		box-shadow: 0 4rpx 16rpx rgba(224, 122, 44, 0.1);
	}
	.hamburger-btn:active {
		background: linear-gradient(135deg, #fde8d0, #f5d5b8);
	}
	.hamburger-icon {
		font-size: 36rpx;
		color: #d4804a;
	}
	.header-content {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}
	.greeting {
		font-size: 36rpx;
		font-weight: bold;
		color: #5c3d1e;
		text-shadow: 0 1rpx 2rpx rgba(140, 90, 50, 0.08);
	}
	.tips {
		display: block;
		margin-top: 8rpx;
		font-size: 24rpx;
		color: #8b5e3c;
		font-family: 'Cormorant Garamond', 'Noto Serif SC', serif;
		font-weight: 300;
		letter-spacing: 2rpx;
	}
	.content-area {
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		position: relative;
		display: flex;
		flex-direction: column;
		-webkit-overflow-scrolling: touch;
		padding: 0 0 20rpx;
	}
	.content-area::-webkit-scrollbar {
		width: 6px;
	}
	.content-area::-webkit-scrollbar-track {
		background: transparent;
	}
	.content-area::-webkit-scrollbar-thumb {
		background: rgba(224, 122, 44, 0.2);
		border-radius: 3px;
	}
	.content-area::-webkit-scrollbar-thumb:hover {
		background: rgba(224, 122, 44, 0.4);
	}
</style>
