<template>
	<view class="landing-page">
		<CursorTrail />
		<ClickRipple />
		<view class="bg-container" :style="{ transform: 'translateY(' + bgTranslateY + 'px)' }">
			<view class="bg-slide bg-slide-1"></view>

			<view class="transition-section transition-section-1">
				<view class="transition-overlay"></view>
			</view>

			<view class="bg-slide bg-slide-2"></view>

			<view class="transition-section transition-section-2">
				<view class="transition-overlay"></view>
			</view>

			<view class="bg-slide bg-slide-3"></view>

			<view class="transition-section transition-section-3">
				<view class="transition-overlay"></view>
			</view>

			<view class="bg-slide bg-slide-4"></view>
		</view>

		<view class="nav-bar">
			<view class="nav-actions">
				<view
					class="nav-btn login-btn"
					:class="{ 'btn-hover': hoverBtn === 'login' }"
					@mouseenter="hoverBtn = 'login'"
					@mouseleave="hoverBtn = ''"
					@click="goToLogin"
				>
					<text class="btn-text">登录</text>
				</view>
				<view
					class="nav-btn register-btn"
					:class="{ 'btn-hover': hoverBtn === 'register' }"
					@mouseenter="hoverBtn = 'register'"
					@mouseleave="hoverBtn = ''"
					@click="goToRegister"
				>
					<text class="btn-text">注册</text>
				</view>
			</view>
		</view>

		<view class="art-text-container" :style="{ opacity: textOpacity, transform: 'translate(-50%, -50%) translateY(' + textTranslateY + 'px) scale(' + textScale + ')' }">
			<text class="art-title">食　光</text>
			<text class="art-subtitle">SAVOR THE MOMENT</text>
		</view>

		<scroll-view class="main-scroll" scroll-y="true" @scroll="onScroll" :scroll-with-animation="true">
			<view class="scroll-content" :style="{ height: scrollContentHeight + 'px' }"></view>
		</scroll-view>
	</view>
</template>

<script>
import CursorTrail from '../../components/CursorTrail.vue'
import ClickRipple from '../../components/ClickRipple.vue'

export default {
	components: {
		CursorTrail,
		ClickRipple
	},
	data() {
		return {
			scrollProgress: 0,
			windowHeight: 0,
			bgTranslateY: 0,
			scrollContentHeight: 0,
			hoverBtn: '',
		}
	},
	computed: {
		textScale() {
			return 1 - this.scrollProgress * 0.6
		},
		textTranslateY() {
			return -this.scrollProgress * 600
		},
		textOpacity() {
			if (this.scrollProgress < 0.1) return 1
			if (this.scrollProgress > 0.3) return 0
			return 1 - (this.scrollProgress - 0.1) / 0.2
		}
	},
	onLoad() {
		const systemInfo = uni.getSystemInfoSync()
		this.windowHeight = systemInfo.windowHeight
		this.scrollContentHeight = this.windowHeight * 6
	},
	methods: {
		goToLogin() {
			this.hoverBtn = ''
			uni.navigateTo({ url: '/pages/login/login' })
		},
		goToRegister() {
			this.hoverBtn = ''
			uni.navigateTo({ url: '/pages/register/register' })
		},
		onScroll(e) {
			const { scrollTop, scrollHeight } = e.detail
			const maxScroll = scrollHeight - this.windowHeight
			if (maxScroll > 0) {
				this.scrollProgress = Math.min(Math.max(scrollTop / maxScroll, 0), 1)
				this.bgTranslateY = -scrollTop * 0.6
			}
		}
	}
}
</script>

<style>
.landing-page {
	position: relative;
	width: 100%;
	height: 100vh;
	overflow: hidden;
}

.bg-container {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 600vh;
	z-index: 0;
	will-change: transform;
	transition: transform 0.1s linear;
}

.bg-slide {
	position: absolute;
	width: 100%;
	height: 100vh;
	background-size: cover;
	background-position: center;
	background-repeat: no-repeat;
}

.bg-slide-1 { top: 0; }
.bg-slide-2 { top: 100vh; }
.bg-slide-3 { top: 200vh; }
.bg-slide-4 { top: 300vh; }

.bg-slide-1 { background-image: url('/static/index01.png'); }
.bg-slide-2 { background-image: url('/static/index02.png'); }
.bg-slide-3 { background-image: url('/static/index03.png'); }
.bg-slide-4 { background-image: url('/static/index04.png'); }

.bg-slide::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 40vh;
	background: linear-gradient(to bottom,
		rgba(80, 50, 30, 0.6) 0%,
		rgba(80, 50, 30, 0.3) 40%,
		rgba(80, 50, 30, 0.1) 70%,
		transparent 100%);
	pointer-events: none;
	z-index: 1;
}

.bg-slide::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	height: 40vh;
	background: linear-gradient(to top,
		rgba(80, 50, 30, 0.6) 0%,
		rgba(80, 50, 30, 0.3) 40%,
		rgba(80, 50, 30, 0.1) 70%,
		transparent 100%);
	pointer-events: none;
	z-index: 1;
}

.bg-slide-1::before {
	display: none;
}

.transition-section {
	position: absolute;
	left: 0;
	right: 0;
	height: 40vh;
	z-index: 2;
}

.transition-section-1 { top: 80vh; }
.transition-section-2 { top: 180vh; }
.transition-section-3 { top: 280vh; }

.transition-overlay {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    pointer-events: none; /* 保证不阻挡滚动和点击 */
    z-index: 2;

    /* 核心修改：使用暖白/香槟色渐变，提取环境高光色 */
    background: linear-gradient(to bottom,
        transparent 0%,
        rgba(140, 120, 100, 0.8) 25%,
        rgba(140, 120, 100, 1) 50%,
        rgba(140, 120, 100, 0.8) 75%,
        transparent 100%
    );

    /* 核心修改：使用柔光混合模式，让高光完美融入底下的图片 */
    mix-blend-mode: soft-light;

    /* 核心修改：高斯模糊，消除渐变边缘的断层感 */
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.nav-bar {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	z-index: 100;
	display: flex;
	justify-content: flex-end;
	padding: 60rpx 50rpx;
}

.nav-actions {
	display: flex;
	gap: 20rpx;
}

.nav-btn {
	padding: 16rpx 50rpx;
	border-radius: 50rpx;
	transition: border-color 0.4s ease, background 0.4s ease, box-shadow 0.4s ease;
	border: 1rpx solid rgba(255, 255, 255, 0.25);
	background: linear-gradient(135deg, rgba(60, 45, 35, 0.42), rgba(30, 22, 18, 0.28));
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 60rpx;
	position: relative;
	overflow: hidden;
	box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.nav-btn::before {
	content: '';
	position: absolute;
	top: 0;
	left: -100%;
	width: 100%;
	height: 100%;
	background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
	transition: left 0.6s ease;
}

.nav-btn.btn-hover::before {
	left: 100%;
}

.nav-btn.btn-hover {
	border-color: rgba(255, 255, 255, 0.5);
	background: linear-gradient(135deg, rgba(80, 60, 45, 0.6), rgba(45, 33, 26, 0.45));
	box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15), 0 0 60px rgba(245, 215, 142, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.nav-btn:active {
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.btn-text {
	font-size: 26rpx;
	font-weight: 500;
	color: rgba(255, 255, 255, 0.95);
	letter-spacing: 4rpx;
	text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
	position: relative;
	z-index: 1;
}

.art-text-container {
	position: absolute;
	top: 50%;
	left: 50%;
	z-index: 60;
	pointer-events: none;
	text-align: center;
}

.art-title {
	display: block;
	font-size: 500rpx;
	font-weight: 200;
	color: #fff;
	letter-spacing: 20rpx;
	line-height: 1.4;
	font-family: "STKaiti", "KaiTi", "华文楷体", "STXingkai", "华文行楷", serif;
}

.art-subtitle {
	display: block;
	font-size: 24rpx;
	font-weight: 400;
	color: rgba(255, 255, 255, 0.7);
	letter-spacing: 12rpx;
	margin-top: 30rpx;
	text-transform: uppercase;
}

.main-scroll {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
}

.scroll-content {
	width: 100%;
}
</style>
