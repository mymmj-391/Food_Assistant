// utils/dishText.js
// 菜品摘要文本处理：清洗原始 Markdown 摘要 + 提取关键词标签

// 摘要关键词词典，按优先级排列，命中后取前两个拼成标签
const KEYWORDS = [
	'清爽', '开胃', '解腻', '清淡', '低脂', '减脂', '健康', '养胃',
	'简单', '快手', '新手友好', '省时', '易消化',
	'家常', '经典', '宴客', '硬菜', '下饭',
	'嫩滑', '滑嫩', '酥脆', '香脆', '软糯', '劲道',
	'鲜香', '咸鲜', '酸香', '酸甜', '麻辣', '香辣', '微辣',
	'滋补', '暖胃', '养颜', '清热', '高蛋白',
	'凉拌', '清蒸', '红烧', '爆炒', '香煎',
	'早餐', '宵夜', '下午茶', '便当',
]

/**
 * 清洗后端返回的摘要（原始 .md 前 100 字）
 * 去掉标题、图片语法、预估信息等 Markdown 噪音
 */
export const cleanSummary = (raw) => {
	if (!raw) return ''
	return raw
		.replace(/!\[[^\]]*\]\([^)]*\)/g, '')
		.replace(/^#{1,6}\s.*$/gm, '')
		.replace(/^\s*预估[^\n]*$/gm, '')
		.replace(/[*_`>]/g, '')
		.replace(/\s+/g, ' ')
		.trim()
}

/**
 * 从摘要中提取关键词作为卡片标签，无命中时回退到分类名
 */
export const summaryTag = (raw, fallback = '') => {
	const text = cleanSummary(raw)
	const hit = []

	for (const word of KEYWORDS) {
		if (!text.includes(word)) continue
		if (hit.some(h => h.includes(word) || word.includes(h))) continue
		hit.push(word)
		if (hit.length === 2) break
	}

	return hit.length ? hit.join('') : (fallback || '家常菜')
}
