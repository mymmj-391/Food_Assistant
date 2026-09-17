import { reactive } from 'vue'

export const chatStore = reactive({
	messages: [
		{
			role: 'ai',
			content: '你好！我是你的饮食助手，有任何关于菜品、食材或烹饪技巧的问题都可以问我哦~',
			dishLinks: [],
			time: '',
		}
	],
	sessionId: '',
	isOpen: false,
	unreadCount: 0,

	reset() {
		this.messages = [
			{
				role: 'ai',
				content: '对话已清空，有什么可以帮你的吗？',
				dishLinks: [],
				time: '',
			}
		]
		this.sessionId = ''
		this.unreadCount = 0
	}
})
