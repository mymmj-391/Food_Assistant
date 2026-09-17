// utils/mdParser.js
// Markdown 章节解析器：将 .md 内容按 ## 标题拆分为结构化章节

/**
 * 将原始 Markdown 文本按 ## 标题拆分为章节数组
 * @param {string} raw - 原始 Markdown 文本
 * @returns {Array<{title: string, content: string}>} 章节列表
 */
export const parseSections = (raw) => {
	if (!raw) return []
	const lines = raw.replace(/\r\n/g, '\n').split('\n')
	const sections = []
	let current = null

	for (const line of lines) {
		if (/^##\s+/.test(line)) {
			if (current) sections.push(current)
			current = {
				title: line.replace(/^##\s+/, '').trim(),
				content: ''
			}
		} else if (current) {
			current.content += line + '\n'
		}
	}
	if (current) sections.push(current)

	return sections.map(s => ({
		title: s.title,
		content: s.content.trim()
	}))
}

/**
 * 解析菜品 MD 内容，提取食材/步骤/贴士
 * 适配结构：必备原料和工具 + 计算 → 食材 | 操作 → 步骤 | 附加内容 → 贴士
 * @param {string} raw - 原始 Markdown 文本
 * @returns {{ingredients: string, steps: string, tips: string}}
 */
export const parseDishContent = (raw) => {
	const sections = parseSections(raw)
	let ingredients = ''
	let steps = ''
	let tips = ''

	for (const sec of sections) {
		if (/必备原料|工具|食材/.test(sec.title)) {
			ingredients = sec.content
		} else if (/计算/.test(sec.title)) {
			ingredients += (ingredients ? '\n\n' : '') + sec.content
		} else if (/操作|步骤|做法/.test(sec.title)) {
			steps = sec.content
		} else if (/附加|贴士|注意|小贴士/.test(sec.title)) {
			tips = sec.content
		}
	}

	return { ingredients, steps, tips }
}

/**
 * 解析技巧 MD 内容，提取器具/流程/注意事项
 * @param {string} raw - 原始 Markdown 文本
 * @returns {{utensils: string, process: string, warnings: string, extra: Array<{title: string, content: string}>}}
 */
export const parseTipContent = (raw) => {
	const sections = parseSections(raw)
	let utensils = ''
	let process = ''
	let warnings = ''
	const extra = []

	for (const sec of sections) {
		if (/器具|工具|准备/.test(sec.title)) {
			utensils = sec.content
		} else if (/流程|步骤|操作/.test(sec.title)) {
			process = sec.content
		} else if (/注意|警告|安全|禁忌/.test(sec.title)) {
			warnings = sec.content
		} else {
			extra.push({ title: sec.title, content: sec.content })
		}
	}

	return { utensils, process, warnings, extra }
}

/**
 * 将章节内容转为HTML格式（支持列表、加粗、行内代码、表格）
 * @param {string} text - 章节 Markdown 文本
 * @returns {string} HTML 字符串
 */
export const mdToHtml = (text) => {
	if (!text) return ''
	let html = text
		// 表格
		.replace(/^\|.*\|$/gm, (match) => {
			const cells = match.split('|').filter(c => c.trim())
			if (cells.every(c => /^[-:]+$/.test(c.trim()))) return ''
			const tag = cells[0].trim().match(/^[-:]+$/) ? 'th' : 'td'
			return '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>'
		})

	// 包裹表格行
	html = html.replace(/(<tr>[\s\S]*?<\/tr>\n?)+/g, '<table>$&</table>')

	// 列表项
	html = html.replace(/^\*\s+(.+)$/gm, '<li>$1</li>')
	html = html.replace(/^(\d+)\.\s+(.+)$/gm, '<li>$1. $2</li>')

	// 包裹连续列表项
	html = html.replace(/(<li>[\s\S]*?<\/li>\n?)+/g, '<ul>$&</ul>')

	// 加粗和行内代码
	html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
	html = html.replace(/`([^`]+)`/g, '<code>$1</code>')

	// 段落
	html = html.split('\n\n').map(block => {
		block = block.trim()
		if (!block) return ''
		if (block.startsWith('<table') || block.startsWith('<ul') || block.startsWith('<h')) return block
		return '<p>' + block.replace(/\n/g, '<br>') + '</p>'
	}).join('\n')

	return html.trim()
}

/**
 * 将章节内容转为结构化数据（用于步骤列表渲染）
 * @param {string} text - 章节 Markdown 文本
 * @returns {Array<{type: string, text: string}>}
 */
export const mdToBlocks = (text) => {
	if (!text) return []
	const lines = text.replace(/\r\n/g, '\n').split('\n')
	const blocks = []
	let currentList = null

	for (const line of lines) {
		const trimmed = line.trim()
		if (!trimmed) {
			if (currentList) {
				blocks.push(currentList)
				currentList = null
			}
			continue
		}

		if (/^\*\s+/.test(trimmed) || /^\d+\.\s+/.test(trimmed)) {
			if (!currentList || currentList.type !== 'list') {
				if (currentList) blocks.push(currentList)
				currentList = { type: 'list', items: [] }
			}
			currentList.items.push(trimmed.replace(/^(\*\s+|\d+\.\s+)/, ''))
		} else if (/^####\s+/.test(trimmed)) {
			if (currentList) blocks.push(currentList)
			blocks.push({ type: 'subtitle', text: trimmed.replace(/^####\s+/, '') })
			currentList = null
		} else if (/^###\s+/.test(trimmed)) {
			if (currentList) blocks.push(currentList)
			blocks.push({ type: 'subtitle', text: trimmed.replace(/^###\s+/, '') })
			currentList = null
		} else {
			if (currentList && currentList.type === 'list') {
				blocks.push(currentList)
				currentList = null
			}
			if (currentList && currentList.type === 'text') {
				currentList.text += '\n' + trimmed
			} else {
				if (currentList) blocks.push(currentList)
				currentList = { type: 'text', text: trimmed }
			}
		}
	}
	if (currentList) blocks.push(currentList)

	return blocks
}
