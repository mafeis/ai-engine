/**
 * 通用工具函数
 */

/**
 * 渲染 Markdown 内容
 */
export function renderMarkdown(content) {
    if (typeof marked !== 'undefined') {
        return marked.parse(content);
    }
    // 如果 marked 未加载，返回预格式化文本
    return `<pre>${content}</pre>`;
}

/**
 * 获取状态文本
 */
export function getStatusText(status) {
    const statusMap = {
        'draft': '草稿',
        'designing': '设计中',
        'resources': '资源生成',
        'ready': '就绪',
        'published': '已发布'
    };
    return statusMap[status] || status;
}

/**
 * 获取资源实际可用的URL
 */
export function getAssetUrl(projectId, folder, itemId, filePath) {
    if (filePath) {
        const match = filePath.match(/projects[\\\/](.+)/);
        if (match) {
            return 'http://localhost:8000/assets/' + match[1].replace(/\\/g, '/');
        }
    }
    return '';
}

/**
 * 初始化代码高亮与Markdown
 */
export function initMarkdown() {
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            highlight: function (code, lang) {
                if (typeof hljs !== 'undefined' && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
    }
}
