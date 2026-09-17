<template>
	<view class="cursor-trail">
		<view class="trail-dot trail-1" :style="{ left: trailX1 + 'px', top: trailY1 + 'px' }"></view>
		<view class="trail-dot trail-2" :style="{ left: trailX2 + 'px', top: trailY2 + 'px' }"></view>
		<view class="trail-dot trail-3" :style="{ left: trailX3 + 'px', top: trailY3 + 'px' }"></view>
		<view class="trail-dot trail-4" :style="{ left: trailX4 + 'px', top: trailY4 + 'px' }"></view>
		<view class="trail-dot trail-5" :style="{ left: trailX5 + 'px', top: trailY5 + 'px' }"></view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			mouseX: 0,
			mouseY: 0,
			trailX1: 0, trailY1: 0,
			trailX2: 0, trailY2: 0,
			trailX3: 0, trailY3: 0,
			trailX4: 0, trailY4: 0,
			trailX5: 0, trailY5: 0,
		}
	},
	mounted() {
		this.rafId = null
		this.startTrailAnimation()
		this.bindEvents()
	},
	beforeUnmount() {
		this.unbindEvents()
		if (this.rafId) {
			cancelAnimationFrame(this.rafId)
			this.rafId = null
		}
	},
	methods: {
		bindEvents() {
			if (typeof window === 'undefined') return
			window.addEventListener('mousemove', this.onMouseMove)
			window.addEventListener('touchmove', this.onTouchMove)
		},
		unbindEvents() {
			if (typeof window === 'undefined') return
			window.removeEventListener('mousemove', this.onMouseMove)
			window.removeEventListener('touchmove', this.onTouchMove)
		},
		onMouseMove(e) {
			if (e.clientX !== undefined && e.clientY !== undefined) {
				this.mouseX = e.clientX
				this.mouseY = e.clientY
			}
		},
		onTouchMove(e) {
			if (e.touches && e.touches.length > 0) {
				this.mouseX = e.touches[0].clientX
				this.mouseY = e.touches[0].clientY
			}
		},
		startTrailAnimation() {
			const updateTrail = () => {
				this.trailX5 += (this.trailX4 - this.trailX5) * 0.3
				this.trailY5 += (this.trailY4 - this.trailY5) * 0.3
				this.trailX4 += (this.trailX3 - this.trailX4) * 0.35
				this.trailY4 += (this.trailY3 - this.trailY4) * 0.35
				this.trailX3 += (this.trailX2 - this.trailX3) * 0.4
				this.trailY3 += (this.trailY2 - this.trailY3) * 0.4
				this.trailX2 += (this.trailX1 - this.trailX2) * 0.45
				this.trailY2 += (this.trailY1 - this.trailY2) * 0.45
				this.trailX1 += (this.mouseX - this.trailX1) * 0.5
				this.trailY1 += (this.mouseY - this.trailY1) * 0.5
				this.rafId = requestAnimationFrame(updateTrail)
			}
			updateTrail()
		}
	}
}
</script>

<style>
.cursor-trail {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	pointer-events: none;
	z-index: 9999;
}

.trail-dot {
	position: absolute;
	border-radius: 50%;
	transform: translate(-50%, -50%);
	mix-blend-mode: screen;
}

.trail-1 {
	width: 20px;
	height: 20px;
	background: radial-gradient(circle, rgba(245, 215, 142, 0.8) 0%, rgba(245, 215, 142, 0.4) 40%, transparent 70%);
	box-shadow: 0 0 20px rgba(245, 215, 142, 0.6);
}

.trail-2 {
	width: 16px;
	height: 16px;
	background: radial-gradient(circle, rgba(245, 215, 142, 0.6) 0%, rgba(245, 215, 142, 0.3) 40%, transparent 70%);
	box-shadow: 0 0 15px rgba(245, 215, 142, 0.4);
}

.trail-3 {
	width: 12px;
	height: 12px;
	background: radial-gradient(circle, rgba(245, 215, 142, 0.45) 0%, rgba(245, 215, 142, 0.2) 40%, transparent 70%);
	box-shadow: 0 0 12px rgba(245, 215, 142, 0.3);
}

.trail-4 {
	width: 8px;
	height: 8px;
	background: radial-gradient(circle, rgba(245, 215, 142, 0.3) 0%, rgba(245, 215, 142, 0.15) 40%, transparent 70%);
	box-shadow: 0 0 8px rgba(245, 215, 142, 0.2);
}

.trail-5 {
	width: 5px;
	height: 5px;
	background: radial-gradient(circle, rgba(245, 215, 142, 0.2) 0%, rgba(245, 215, 142, 0.1) 40%, transparent 70%);
	box-shadow: 0 0 5px rgba(245, 215, 142, 0.15);
}
</style>
