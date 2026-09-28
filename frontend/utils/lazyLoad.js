// utils/lazyLoad.js
// 图片懒加载：uni-app 的 H5 端并没有实现 <image lazy-load> 属性，
// 传进去的 lazy-load 只是声明了 prop、无人读取，所以必须自己用 IntersectionObserver 实现。
//
// 用法：
//   1. 列表项容器渲染后调用 observe('选择器', 数据长度)，选择器需保证 DOM 顺序与数据顺序一致
//   2. 模板中用 isVisible(index) 决定是否渲染 <image>

import { nextTick, reactive, onUnmounted } from 'vue'

export const useLazyLoad = () => {
	// 已进入视口的索引（reactive Set 的 add / clear 会触发视图更新）
	const visibleIndexes = reactive(new Set())
	let observer = null

	const isVisible = (index) => visibleIndexes.has(index)

	const markAllVisible = (total) => {
		for (let i = 0; i < total; i++) visibleIndexes.add(i)
	}

	const stop = () => {
		if (observer) {
			observer.disconnect()
			observer = null
		}
	}

	/**
	 * 监听列表项，进入视口后再把对应索引标记为可见
	 * @param {string} selector 列表项选择器，DOM 顺序需与数据顺序一致
	 * @param {number} total 数据总条数
	 */
	const observe = async (selector, total) => {
		stop()
		visibleIndexes.clear()
		if (!total) return

		// #ifdef H5
		await nextTick()
		const nodes = document.querySelectorAll(selector)
		// 浏览器不支持 IntersectionObserver 时直接全部显示，避免图片永远不加载
		if (!nodes.length || typeof IntersectionObserver === 'undefined') {
			markAllVisible(total)
			return
		}

		observer = new IntersectionObserver((entries) => {
			entries.forEach((entry) => {
				if (!entry.isIntersecting) return
				visibleIndexes.add(Number(entry.target.getAttribute('data-lazy-index')))
				observer.unobserve(entry.target)
			})
		}, { rootMargin: '300px 0px' })

		nodes.forEach((el, index) => {
			el.setAttribute('data-lazy-index', index)
			observer.observe(el)
		})
		return
		// #endif

		// #ifndef H5
		// 小程序 / App 端在上面的代码已被编译期剥离，直接全部显示
		markAllVisible(total)
		// #endif
	}

	onUnmounted(stop)

	return { isVisible, observe, stop }
}
