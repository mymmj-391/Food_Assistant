<template>
	<view class="login-page">
		<CursorTrail />
		<ClickRipple />
		<view class="background-overlay"></view>

		<view class="floating-card">
			<view class="back-btn" @click="goBack">
				<view class="back-icon"></view>
			</view>

			<view class="logo-area">
				<image class="logo" src="/static/login_logo.png" mode="aspectFit"></image>
				<text class="app-name">食光</text>
			</view>

			<view class="form-area">
				<view class="form-item">
				<input
					class="input"
					type="text"
					v-model="form.username"
					placeholder="请输入用户名"
					placeholder-class="placeholder"
					@keydown.enter="handleLogin"
				/>
			</view>
			<view class="form-item">
				<input
					class="input"
					:password="true"
					v-model="form.password"
					placeholder="请输入密码"
					placeholder-class="placeholder"
					@keydown.enter="handleLogin"
				/>
			</view>

				<button class="login-btn" :loading="loading" :disabled="loading" @click="handleLogin">
					登 录
				</button>

				<view class="register-link" @click="goRegister">
					<text>还没有账号？去注册</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
	import { reactive, ref } from 'vue'
	import { login } from '../../api/auth'
	import CursorTrail from '../../components/CursorTrail.vue'
	import ClickRipple from '../../components/ClickRipple.vue'

	const form = reactive({
		username: '',
		password: ''
	})

	const loading = ref(false)

	const handleLogin = async () => {
		if (!form.username || !form.password) {
			uni.showToast({
				title: '请输入用户名和密码',
				icon: 'none'
			})
			return
		}

		loading.value = true
		try {
			const res = await login({
				username: form.username,
				password: form.password
			})
			uni.setStorageSync('token', res.token)
			uni.setStorageSync('user', res.user)
			uni.showToast({
				title: '登录成功',
				icon: 'success'
			})
			uni.reLaunch({
				url: '/pages/home/home'
			})
		} catch (e) {
		} finally {
			loading.value = false
		}
	}

	const goRegister = () => {
		uni.navigateTo({
			url: '/pages/register/register'
		})
	}

	const goBack = () => {
		uni.reLaunch({
			url: '/pages/index/index'
		})
	}
</script>

<style>
	@import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&display=swap');

	.login-page {
	position: relative;
	min-height: 100vh;
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 40rpx;
	background-color: #1a1410;
	background-image: url('/static/login_background.png');
	background-size: cover;
	background-position: center;
}

	.background-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: linear-gradient(180deg,
			rgba(140, 120, 100, 0.25) 0%,
			rgba(80, 50, 30, 0.45) 50%,
			rgba(40, 25, 15, 0.65) 100%);
		z-index: 0;
	}

	.floating-card {
		position: relative;
		z-index: 1;
		width: 100%;
		max-width: 600rpx;
		min-height: 1000rpx;
		background: rgba(255, 254, 250, 0.08);
		border: 1px solid rgba(255, 254, 250, 0.15);
		border-radius: 40rpx;
		padding: 80rpx 48rpx;
		box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.4);
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
		display: flex;
		flex-direction: column;
		justify-content: center;
	}

	.back-btn {
		position: absolute;
		top: 32rpx;
		left: 32rpx;
		width: 64rpx;
		height: 64rpx;
		display: flex;
		justify-content: center;
		align-items: center;
		background: rgba(255, 254, 250, 0.1);
		border: 1px solid rgba(255, 254, 250, 0.2);
		border-radius: 50%;
	}

	.back-icon {
		width: 24rpx;
		height: 24rpx;
		border-left: 4rpx solid #FFFEFA;
		border-bottom: 4rpx solid #FFFEFA;
		border-top: 4rpx solid transparent;
		border-right: 4rpx solid transparent;
		transform: rotate(45deg);
		margin-left: 8rpx;
	}

	.logo-area {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-bottom: 64rpx;
	}

	.logo {
		width: 160rpx;
		height: 160rpx;
		border-radius: 50%;
		overflow: hidden;
	}

	.app-name {
		margin-top: 24rpx;
		font-size: 44rpx;
		font-weight: bold;
		color: #FFFEFA;
		letter-spacing: 8rpx;
	font-family: 'Ma Shan Zheng', 'ZCOOL XiaoWei', 'STKaiti', 'KaiTi', serif;
	text-shadow: 0 2px 8px rgba(245, 230, 200, 0.4);
}

.form-area {
		width: 100%;
	}

	.form-item {
		margin-bottom: 32rpx;
		background: rgba(255, 254, 250, 0.06);
		border: 1px solid rgba(255, 254, 250, 0.15);
		border-radius: 16rpx;
		padding: 0 28rpx;
	}

	.input {
		height: 100rpx;
		font-size: 32rpx;
		color: #FFFEFA;
	}

	.placeholder {
		color: rgba(255, 254, 250, 0.4);
	}

	.login-btn {
		margin-top: 24rpx;
		height: 100rpx;
		line-height: 100rpx;
		background: linear-gradient(135deg, #FFFEFA, #F5E6C8);
		color: #3a2a1a;
		font-size: 34rpx;
		font-weight: bold;
		border-radius: 16rpx;
	}

	.login-btn::after {
		border: none;
	}

	.register-link {
		margin-top: 40rpx;
		text-align: center;
		color: #F5E6C8;
		font-size: 28rpx;
	}
</style>
