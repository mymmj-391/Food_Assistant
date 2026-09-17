<template>
	<view class="click-ripple-container">
		<view
			v-for="ripple in ripples"
			:key="ripple.id"
			class="ripple"
			:style="{
				left: ripple.x + 'px',
				top: ripple.y + 'px',
				width: ripple.size + 'px',
				height: ripple.size + 'px'
			}"
		>
			<view class="ripple-core"></view>
			<view class="ripple-ring"></view>
		</view>
	</view>
</template>

<script>
let rippleId = 0

export default {
	data() {
		return {
			ripples: []
		}
	},
	mounted() {
		this.bindEvents()
	},
	beforeUnmount() {
		this.unbindEvents()
	},
	methods: {
		bindEvents() {
			if (typeof window === 'undefined') return
			window.addEventListener('click', this.onClick)
			window.addEventListener('touchstart', this.onTouch, { passive: true })
		},
		unbindEvents() {
			if (typeof window === 'undefined') return
			window.removeEventListener('click', this.onClick)
			window.removeEventListener('touchstart', this.onTouch)
		},
		onClick(e) {
			if (e.clientX === undefined || e.clientY === undefined) return
			this.spawnRipple(e.clientX, e.clientY)
		},
		onTouch(e) {
			if (!e.touches || e.touches.length === 0) return
			const touch = e.touches[0]
			this.spawnRipple(touch.clientX, touch.clientY)
		},
		spawnRipple(x, y) {
			const id = ++rippleId
			const size = Math.round(30 + Math.random() * 14)

			this.ripples.push({ id, x, y, size })

			setTimeout(() => {
				this.ripples = this.ripples.filter(r => r.id !== id)
			}, 700)
		}
	}
}
</script>

<style>
.click-ripple-container {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	pointer-events: none;
	z-index: 9998;
	overflow: hidden;
}

.ripple {
	position: absolute;
	transform: translate(-50%, -50%) scale(0);
	animation: rippleGrow 0.65s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.ripple-core {
	position: absolute;
	top: 50%;
	left: 50%;
	width: 50%;
	height: 50%;
	border-radius: 50%;
	transform: translate(-50%, -50%);
	background: radial-gradient(circle, rgba(224, 122, 44, 0.7) 0%, rgba(224, 122, 44, 0.25) 50%, transparent 70%);
}

.ripple-ring {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	border-radius: 50%;
	border: 4px solid rgba(224, 122, 44, 0.8);
	box-shadow: 0 0 16px rgba(224, 122, 44, 0.5), inset 0 0 10px rgba(224, 122, 44, 0.3);
}

@keyframes rippleGrow {
	0% {
		transform: translate(-50%, -50%) scale(0);
		opacity: 1;
	}
	100% {
		transform: translate(-50%, -50%) scale(2.5);
		opacity: 0;
	}
}
</style>
