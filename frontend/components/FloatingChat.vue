<template>
	<view class="floating-chat-wrapper">
		<!-- 遮罩层 -->
		<view v-if="isOpen" class="chat-mask" @click="closeChat"></view>

		<!-- 聊天窗口 -->
		<view v-if="isOpen" class="chat-container">
			<!-- 头部简化栏 -->
			<view class="chat-header">
				<view class="header-left">
					<view class="header-avatar">
						<AiAvatar />
					</view>
					<text class="header-title">AI 饮食助手</text>
				</view>
				<view class="header-actions">
					<view class="action-btn" @click="clearMessages">
						<text class="action-icon">⟳</text>
					</view>
					<view class="action-btn" @click="closeChat">
						<text class="action-icon">×</text>
					</view>
				</view>
			</view>

			<!-- 消息列表 -->
			<scroll-view
				class="chat-messages"
				scroll-y="true"
				:scroll-top="scrollTop"
				scroll-with-animation
				:show-scrollbar="false"
			>
				<view class="messages-inner">
					<view
						v-for="(msg, index) in visibleMessages"
						:key="index"
						class="message-item"
						:class="msg.role === 'user' ? 'message-user' : 'message-ai'"
					>
						<!-- AI 消息 -->
						<template v-if="msg.role === 'ai'">
							<view class="message-avatar ai-avatar">
								<AiAvatar />
							</view>
							<view class="message-content">
								<view class="message-bubble">
									<rich-text :nodes="formatMessage(msg.content)"></rich-text>
								</view>
								<!-- 菜品链接 -->
								<view v-if="msg.dishLinks && msg.dishLinks.length" class="dish-links">
									<text class="links-label">相关推荐：</text>
									<view class="links-list">
										<view
											v-for="(link, li) in msg.dishLinks"
											:key="li"
											class="dish-link-item"
											@click="navigateToDish(link)"
										>
											<text class="link-text">{{ link.name }}</text>
											<text class="link-arrow">→</text>
										</view>
									</view>
								</view>
								<text v-if="msg.time" class="message-time">{{ msg.time }}</text>
							</view>
						</template>

						<!-- 用户消息 -->
						<template v-if="msg.role === 'user'">
							<view class="message-avatar user-avatar">
								<text class="avatar-text">我</text>
							</view>
							<view class="message-content">
								<view class="message-bubble">
									<text class="message-text">{{ msg.content }}</text>
								</view>
								<text v-if="msg.time" class="message-time">{{ msg.time }}</text>
							</view>
						</template>
					</view>
					<view v-if="isLoading && !messages[messages.length - 1]?.content" class="message-item message-ai">
						<view class="message-avatar ai-avatar">
							<AiAvatar />
						</view>
						<view class="message-content">
							<view class="message-bubble loading-bubble">
								<view class="loading-dots">
									<view class="dot"></view>
									<view class="dot"></view>
									<view class="dot"></view>
								</view>
							</view>
						</view>
					</view>
				</view>
			</scroll-view>

			<!-- 快捷问题 -->
			<view v-if="messages.length <= 1" class="quick-questions">
				<text class="quick-title">你可以这样问：</text>
				<view class="quick-list">
					<view
						v-for="(q, qi) in quickQuestions"
						:key="qi"
						class="quick-item"
						@click="inputText = q; sendMessage()"
					>
						<text class="quick-text">{{ q }}</text>
					</view>
				</view>
			</view>

			<!-- 输入区域 -->
			<view class="chat-input-area">
				<view class="input-wrapper">
					<textarea
						class="chat-input"
						v-model="inputText"
						placeholder="输入你的饮食问题..."
						placeholder-class="input-placeholder"
						:auto-height="true"
						:maxlength="-1"
						confirm-type="send"
						@confirm="sendMessage"
						:disabled="isLoading"
					/>
				</view>
				<view
					v-if="isLoading"
					class="stop-btn"
					@click="stopGeneration"
				>
					<text class="stop-icon">■</text>
				</view>
				<view
					v-else
					class="send-btn"
					:class="{ 'send-btn-active': inputText.trim() }"
					@click="sendMessage"
				>
					<text class="send-icon">↑</text>
				</view>
			</view>
		</view>

		<!-- 3D 模型悬浮按钮 -->
		<view
			v-show="!isOpen"
			ref="modelContainer"
			class="floating-model-wrapper"
			@click="handleClick"
			@mousedown="onDragStart"
			@touchstart="onDragStart"
		>
			<view v-if="unreadCount > 0" class="unread-badge">
				<text class="unread-text">{{ unreadCount > 99 ? '99+' : unreadCount }}</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, nextTick, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { chatStore } from '../stores/chat'
import { streamChatMessage } from '../api/chat'
import AiAvatar from './AiAvatar.vue'

// ===== 会话状态 =====
const inputText = ref('')
const isLoading = ref(false)
const scrollTop = ref(0)
const currentStreamCancel = ref(null)

const messages = computed(() => chatStore.messages)

// 只展示有内容的消息，避免思考过程中出现空的 AI 气泡
const visibleMessages = computed(() =>
	messages.value.filter(
		(m) => m.role === 'user' || m.content || (m.dishLinks && m.dishLinks.length)
	)
)
const isOpen = computed({
	get: () => chatStore.isOpen,
	set: (val) => { chatStore.isOpen = val }
})
const sessionId = computed({
	get: () => chatStore.sessionId,
	set: (val) => { chatStore.sessionId = val }
})
const unreadCount = computed(() => chatStore.unreadCount)

// ===== 3D 模型 =====
const MODEL_URL = '/static/food-model.glb'
const MODEL_SIZE = 300
const BASE_Y = -0.3
const DRAG_THRESHOLD = 5

const modelContainer = ref(null)

let scene, camera, renderer, modelMesh, animationId
let idleTime = 0
let modelX = 20
let modelY = 20
let drag = { active: false, moved: false, originX: 0, originY: 0, baseX: 0, baseY: 0 }

function initThreeJS() {
	const container = modelContainer.value?.$el || modelContainer.value
	if (!container) return

	scene = new THREE.Scene()

	camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100)
	camera.position.set(0, 0.5, 4)
	camera.lookAt(0, 0, 0)

	renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
	renderer.setPixelRatio(window.devicePixelRatio || 1)
	renderer.setSize(MODEL_SIZE, MODEL_SIZE)
	renderer.setClearColor(0x000000, 0)
	container.appendChild(renderer.domElement)

	scene.add(new THREE.AmbientLight(0xffffff, 1.2))
	const dirLight = new THREE.DirectionalLight(0xffffff, 1.5)
	dirLight.position.set(2, 4, 5)
	scene.add(dirLight)
	const fillLight = new THREE.DirectionalLight(0xfff5eb, 0.8)
	fillLight.position.set(-3, 1, 2)
	scene.add(fillLight)
	const backLight = new THREE.DirectionalLight(0xffd699, 0.6)
	backLight.position.set(-2, -1, -3)
	scene.add(backLight)

	new GLTFLoader().load(
		MODEL_URL,
		(gltf) => {
			modelMesh = gltf.scene
			modelMesh.scale.setScalar(1.1)
			modelMesh.position.set(0, BASE_Y, 0)
			scene.add(modelMesh)
		},
		undefined,
		(err) => {
			console.warn('[FloatingChat] 模型加载失败，使用内置模型:', err)
			createDefaultModel()
		}
	)

	animate()
}

function animate() {
	animationId = requestAnimationFrame(animate)
	idleTime += 0.02
	if (modelMesh) {
		modelMesh.position.y = BASE_Y + Math.sin(idleTime) * 0.08
		modelMesh.rotation.x = Math.sin(idleTime * 0.5) * 0.05
		modelMesh.rotation.z = Math.cos(idleTime * 0.3) * 0.05
	}
	renderer.render(scene, camera)
}

function onDragStart(e) {
	const point = e.touches ? e.touches[0] : e
	const el = modelContainer.value?.$el || modelContainer.value
	const rect = el ? el.getBoundingClientRect() : null
	drag = {
		active: true,
		moved: false,
		originX: point.clientX,
		originY: point.clientY,
		baseX: rect ? rect.left : modelX,
		baseY: rect ? rect.top : modelY,
	}
	window.addEventListener('mousemove', onDragMove)
	window.addEventListener('mouseup', onDragEnd)
	window.addEventListener('touchmove', onDragMove, { passive: false })
	window.addEventListener('touchend', onDragEnd)
}

function onDragMove(e) {
	if (!drag.active) return
	const point = e.touches ? e.touches[0] : e
	const dx = point.clientX - drag.originX
	const dy = point.clientY - drag.originY
	if (!drag.moved && Math.abs(dx) < DRAG_THRESHOLD && Math.abs(dy) < DRAG_THRESHOLD) return

	drag.moved = true
	if (e.cancelable) e.preventDefault()
	modelX = drag.baseX + dx
	modelY = drag.baseY + dy

	const el = modelContainer.value?.$el || modelContainer.value
	if (el) {
		el.style.right = 'auto'
		el.style.bottom = 'auto'
		el.style.left = `${modelX}px`
		el.style.top = `${modelY}px`
	}
}

function onDragEnd() {
	drag.active = false
	window.removeEventListener('mousemove', onDragMove)
	window.removeEventListener('mouseup', onDragEnd)
	window.removeEventListener('touchmove', onDragMove)
	window.removeEventListener('touchend', onDragEnd)
}

function handleClick() {
	if (drag.moved) {
		drag.moved = false
		return
	}
	toggleChat()
}

watch(isOpen, (open) => {
	if (open && modelMesh) {
		modelMesh.position.y = BASE_Y
		modelMesh.rotation.set(0, 0, 0)
		idleTime = 0
	}
})

function createDefaultModel() {
	const group = new THREE.Group()

	const body = new THREE.Mesh(
		new THREE.IcosahedronGeometry(1, 1),
		new THREE.MeshPhongMaterial({ color: 0xf5a623, shininess: 80, specular: 0xffe0b0 })
	)
	group.add(body)

	const eyeGeom = new THREE.SphereGeometry(0.12, 16, 16)
	const eyeMat = new THREE.MeshPhongMaterial({ color: 0x3d2415 })
	const leftEye = new THREE.Mesh(eyeGeom, eyeMat)
	leftEye.position.set(-0.3, 0.2, 0.85)
	group.add(leftEye)
	const rightEye = new THREE.Mesh(eyeGeom, eyeMat)
	rightEye.position.set(0.3, 0.2, 0.85)
	group.add(rightEye)

	const mouth = new THREE.Mesh(
		new THREE.TorusGeometry(0.2, 0.05, 8, 16, Math.PI),
		new THREE.MeshPhongMaterial({ color: 0x3d2415 })
	)
	mouth.position.set(0, -0.15, 0.88)
	mouth.rotation.z = Math.PI
	group.add(mouth)

	const hat = new THREE.Mesh(
		new THREE.ConeGeometry(0.6, 0.8, 8),
		new THREE.MeshPhongMaterial({ color: 0xffffff, shininess: 60 })
	)
	hat.position.set(0, 1.2, 0)
	group.add(hat)

	group.scale.setScalar(1.1)
	group.position.set(0, BASE_Y, 0)
	modelMesh = group
	scene.add(modelMesh)
}

onMounted(() => {
	initThreeJS()
})

onBeforeUnmount(() => {
	onDragEnd()
	if (animationId) cancelAnimationFrame(animationId)
	if (renderer) {
		renderer.dispose()
		renderer.forceContextLoss()
		renderer.domElement?.remove()
		renderer = null
	}
	animationId = null
	modelMesh = null
})

// ===== 快捷问题 =====
const quickQuestionPool = [
	'红烧肉怎么做？',
	'有什么清淡的素菜推荐？',
	'如何挑选新鲜的水产？',
	'糖醋排骨的糖醋比例是多少？',
	'什么汤适合冬天喝？',
	'早餐吃什么营养又快捷？',
	'如何判断虾是否新鲜？',
	'减肥期间能吃什么零食？',
	'怎么做饭才能保留更多营养？',
	'什么是优质碳水？',
	'豆腐怎么做好吃？',
	'夏季适合喝什么饮品？',
	'如何处理鱼腥味？',
	'番茄炒蛋是先放番茄还是先放蛋？',
	'空气炸锅能做什么菜？'
]

const quickQuestions = ref([])

function shuffleQuestions() {
	const shuffled = [...quickQuestionPool].sort(() => Math.random() - 0.5)
	quickQuestions.value = shuffled.slice(0, 4)
}

function formatMessage(content) {
	if (!content) return ''
	let html = content
	html = html.replace(/&/g, '&amp;')
	html = html.replace(/</g, '&lt;')
	html = html.replace(/>/g, '&gt;')
	html = html.replace(/\n/g, '<br/>')
	html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color:#e07a2c">$1</strong>')
	return html
}

const toggleChat = () => {
	isOpen.value = !isOpen.value
	if (isOpen.value) {
		chatStore.unreadCount = 0
		shuffleQuestions()
		scrollToBottom()
	}
}

const closeChat = () => {
	isOpen.value = false
}

const clearMessages = () => {
	if (currentStreamCancel.value) {
		currentStreamCancel.value()
		currentStreamCancel.value = null
	}
	isLoading.value = false
	chatStore.reset()
}

const stopGeneration = () => {
	if (currentStreamCancel.value) {
		currentStreamCancel.value()
		currentStreamCancel.value = null
	}
	isLoading.value = false
	const last = messages.value[messages.value.length - 1]
	if (last && last.role === 'ai') {
		last.content = last.content ? `${last.content}\n（已停止生成）` : '（已停止生成）'
	}
	scrollToBottom()
}

const navigateToDish = (link) => {
	closeChat()
	uni.navigateTo({
		url: link.url,
		fail: () => {
			uni.reLaunch({ url: '/pages/home/home' })
		}
	})
}

const getCurrentTime = () => {
	const now = new Date()
	const hours = String(now.getHours()).padStart(2, '0')
	const minutes = String(now.getMinutes()).padStart(2, '0')
	return `${hours}:${minutes}`
}

const sendMessage = async () => {
	const text = inputText.value.trim()
	if (!text || isLoading.value) return

	const currentTime = getCurrentTime()
	messages.value.push({
		role: 'user',
		content: text,
		dishLinks: [],
		time: currentTime,
	})
	inputText.value = ''
	isLoading.value = true
	scrollToBottom()

	messages.value.push({
		role: 'ai',
		content: '',
		dishLinks: [],
		time: currentTime,
	})

	const aiIndex = messages.value.length - 1

	currentStreamCancel.value = streamChatMessage(text, 5, sessionId.value, {
		onContent: (chunk) => {
			messages.value[aiIndex].content += chunk
			scrollToBottom()
		},
		onDone: (data) => {
			sessionId.value = data.session_id || sessionId.value
			messages.value[aiIndex].dishLinks = data.dish_links || []
			isLoading.value = false
			currentStreamCancel.value = null
			if (!isOpen.value) {
				chatStore.unreadCount++
			}
			scrollToBottom()
		},
		onError: (err) => {
			messages.value[aiIndex].content = err
			isLoading.value = false
			currentStreamCancel.value = null
		}
	})
}

const scrollToBottom = () => {
	nextTick(() => {
		scrollTop.value = messages.value.length * 10000
	})
}
</script>

<style scoped>
/* 遮罩层 */
.chat-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0, 0, 0, 0.4);
	z-index: 9998;
	animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
	from { opacity: 0; }
	to { opacity: 1; }
}

/* 聊天窗口 */
.chat-container {
	position: fixed;
	top: 0;
	right: 0;
	width: 480px;
	height: 100vh;
	background: linear-gradient(180deg, #ffffff 0%, #fdf8f0 100%);
	box-shadow: -8px 0 40px rgba(140, 90, 50, 0.15);
	display: flex;
	flex-direction: column;
	z-index: 9999;
	animation: slideIn 0.3s ease;
}

@keyframes slideIn {
	from {
		transform: translateX(100%);
		opacity: 0;
	}
	to {
		transform: translateX(0);
		opacity: 1;
	}
}

/* 简化头部 */
.chat-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 14px 20px;
	background:
		radial-gradient(ellipse at 80% 20%, rgba(255, 210, 160, 0.5) 0%, transparent 45%),
		radial-gradient(ellipse at 10% 80%, rgba(255, 190, 140, 0.3) 0%, transparent 40%),
		linear-gradient(180deg, #fffaf5 0%, #fef3e6 100%);
	border-bottom: 2px solid transparent;
	border-image: linear-gradient(90deg, #f0b088, #e07a2c, #d4804a) 1;
	flex-shrink: 0;
}

.header-left {
	display: flex;
	align-items: center;
	gap: 10px;
}

.header-avatar {
	width: 36px;
	height: 36px;
	border-radius: 50%;
	overflow: hidden;
	flex-shrink: 0;
}

.header-title {
	font-size: 16px;
	color: #5c3d1e;
	font-weight: bold;
	font-family: 'Ma Shan Zheng', 'ZCOOL XiaoWei', serif;
	letter-spacing: 1px;
}

.header-actions {
	display: flex;
	align-items: center;
	gap: 8px;
}

.action-btn {
	width: 32px;
	height: 32px;
	border-radius: 50%;
	background: linear-gradient(135deg, #fef5eb, #fde8d0);
	border: 1.5px solid rgba(224, 122, 44, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s;
	box-shadow: 0 2px 8px rgba(224, 122, 44, 0.1);
}

.action-btn:active {
	background: linear-gradient(135deg, #fde8d0, #f5d5b8);
	transform: scale(0.92);
}

.action-icon {
	font-size: 16px;
	color: #d4804a;
	font-weight: bold;
}

/* 消息列表 */
.chat-messages {
	flex: 1;
	overflow-y: auto;
	background-color: #fdf8f0;
}

.messages-inner {
	padding: 16px 12px 16px 16px;
}

.message-item {
	display: flex;
	margin-bottom: 16px;
	align-items: flex-start;
}

.message-avatar {
	width: 36px;
	height: 36px;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	overflow: hidden;
}

.ai-avatar {
	background: linear-gradient(135deg, #fef5eb, #fde8d0);
	border: 1.5px solid rgba(224, 122, 44, 0.2);
	margin-right: 10px;
}

.user-avatar {
	background: linear-gradient(135deg, #8b5e3c, #6b4226);
	margin-left: 10px;
	margin-right: 0;
}

.avatar-text {
	font-size: 12px;
	color: #ffffff;
	font-weight: bold;
}

.message-content {
	flex: 1;
	min-width: 0;
}

/* 用户消息：头像在右侧，消息在左侧 */
.message-user {
	flex-direction: row-reverse;
}

.message-user .message-avatar {
	margin-left: 10px;
	margin-right: 0;
}

.message-user .message-content {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
}

.message-bubble {
	padding: 12px 16px;
	border-radius: 16px;
	word-break: break-word;
	max-width: 100%;
}

.message-user .message-bubble {
	background: linear-gradient(135deg, #f0b088, #e07a2c);
	border-top-right-radius: 4px;
	box-shadow: 0 2px 8px rgba(224, 122, 44, 0.15);
}

.message-ai .message-bubble {
	background-color: #fef5eb;
	border-top-left-radius: 4px;
	box-shadow: 0 2px 8px rgba(140, 90, 50, 0.08);
	border: 1px solid rgba(224, 122, 44, 0.08);
}

.message-text {
	font-size: 14px;
	line-height: 1.6;
}

.message-user .message-text {
	color: #ffffff;
}

.message-time {
	font-size: 11px;
	color: #999999;
	margin-top: 4px;
}

.message-user .message-time {
	text-align: right;
}

/* 菜品链接 */
.dish-links {
	margin-top: 10px;
}

.links-label {
	font-size: 12px;
	color: #8b7355;
	margin-bottom: 6px;
}

.links-list {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
}

.dish-link-item {
	display: flex;
	align-items: center;
	padding: 8px 14px;
	background-color: #fef5eb;
	border: 1px solid rgba(224, 122, 44, 0.2);
	border-radius: 20px;
	transition: all 0.2s;
}

.dish-link-item:active {
	background-color: #fde8d0;
	transform: scale(0.96);
}

.link-text {
	font-size: 13px;
	color: #e07a2c;
}

.link-arrow {
	font-size: 13px;
	color: #e07a2c;
	margin-left: 4px;
}

/* 加载动画 */
.loading-bubble {
	padding: 14px 20px;
}

.loading-dots {
	display: flex;
	align-items: center;
	gap: 6px;
}

.dot {
	width: 8px;
	height: 8px;
	border-radius: 50%;
	background-color: #e07a2c;
	animation: dot-bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes dot-bounce {
	0%, 80%, 100% {
		transform: scale(0.6);
		opacity: 0.4;
	}
	40% {
		transform: scale(1);
		opacity: 1;
	}
}

/* 快捷问题 */
.quick-questions {
	padding: 12px 16px;
	background-color: #ffffff;
	border-top: 1px solid rgba(224, 122, 44, 0.1);
}

.quick-title {
	font-size: 12px;
	color: #8b7355;
	margin-bottom: 10px;
}

.quick-list {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
}

.quick-item {
	padding: 8px 14px;
	background-color: #fef5eb;
	border: 1px solid rgba(224, 122, 44, 0.2);
	border-radius: 20px;
	transition: all 0.2s;
}

.quick-item:active {
	background-color: #fde8d0;
}

.quick-text {
	font-size: 13px;
	color: #e07a2c;
}

/* 输入区域 */
.chat-input-area {
	display: flex;
	align-items: flex-end;
	padding: 12px 16px;
	background-color: #ffffff;
	border-top: 1px solid rgba(224, 122, 44, 0.1);
	flex-shrink: 0;
	gap: 10px;
}

.input-wrapper {
	flex: 1;
	background-color: #fdf8f0;
	border-radius: 20px;
	padding: 8px 16px;
	min-height: 40px;
	max-height: 120px;
	border: 1px solid rgba(224, 122, 44, 0.1);
}

.chat-input {
	width: 100%;
	font-size: 14px;
	color: #3d2415;
	line-height: 1.5;
	min-height: 24px;
	max-height: 100px;
}

.input-placeholder {
	color: #8b7355;
}

.stop-btn {
	width: 40px;
	height: 40px;
	border-radius: 50%;
	background: linear-gradient(135deg, #fef5eb, #fde8d0);
	border: 1.5px solid rgba(224, 122, 44, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s ease;
	flex-shrink: 0;
	box-shadow: 0 2px 8px rgba(224, 122, 44, 0.1);
}

.stop-btn:active {
	background: linear-gradient(135deg, #fde8d0, #f5d5b8);
	transform: scale(0.92);
}

.stop-icon {
	font-size: 16px;
	color: #d4804a;
	font-weight: bold;
}

.send-btn {
	width: 40px;
	height: 40px;
	border-radius: 50%;
	background-color: #e0e0e0;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s ease;
	flex-shrink: 0;
}

.send-btn-active {
	background: linear-gradient(135deg, #f0b088, #e07a2c);
	box-shadow: 0 4px 12px rgba(224, 122, 44, 0.3);
}

.send-icon {
	font-size: 18px;
	color: #ffffff;
	font-weight: bold;
}

/* 3D 模型悬浮按钮 */
.floating-model-wrapper {
	width: 300px;
	height: 300px;
	cursor: pointer;
	position: fixed;
	right: -50px;
	bottom: -80px;
	z-index: 9999;
	transition: transform 0.3s ease;
	touch-action: none;
	user-select: none;
}

.floating-model-wrapper:active {
	transform: scale(0.95);
}

.floating-model-wrapper :deep(canvas) {
	display: block;
	pointer-events: none;
}

.unread-badge {
	position: absolute;
	top: -4px;
	right: -4px;
	min-width: 20px;
	height: 20px;
	border-radius: 10px;
	background-color: #ef4444;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0 6px;
}

.unread-text {
	font-size: 11px;
	color: #ffffff;
	font-weight: bold;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
	width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
	background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
	background-color: rgba(0, 0, 0, 0.15);
	border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
	background-color: rgba(0, 0, 0, 0.25);
}

/* 响应式 */
@media (max-width: 768px) {
	.chat-container {
		width: 100%;
	}
}
</style>
