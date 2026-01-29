/**
 * API 基础地址与请求服务
 */

const API_BASE = 'http://localhost:8000/api';

export const api = {
    /**
     * 获取项目列表
     */
    async getProjects() {
        const response = await fetch(`${API_BASE}/projects/`);
        return response.json();
    },

    /**
     * 创建新项目
     */
    async createProject(data) {
        const response = await fetch(`${API_BASE}/projects/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    /**
     * 获取项目详情
     */
    async getProject(projectId) {
        const response = await fetch(`${API_BASE}/projects/${projectId}`);
        return response.json();
    },

    /**
     * 删除项目
     */
    async deleteProject(projectId) {
        const response = await fetch(`${API_BASE}/projects/${projectId}`, {
            method: 'DELETE'
        });
        return response.json();
    },

    /**
     * 获取文档列表
     */
    async getDocumentList(projectId) {
        const response = await fetch(`${API_BASE}/documents/${projectId}/list`);
        return response.json();
    },

    /**
     * 获取文档内容
     */
    async getDocument(projectId, docType) {
        const response = await fetch(`${API_BASE}/documents/${projectId}/${docType}`);
        if (!response.ok) {
            throw new Error('文档不存在');
        }
        return response.json();
    },

    /**
     * 保存文档内容
     */
    async saveDocument(projectId, docType, content) {
        const response = await fetch(`${API_BASE}/documents/${projectId}/${docType}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(content)
        });
        return response.json();
    },

    /**
     * 生成文档
     */
    async generateDocument(projectId, docType) {
        const response = await fetch(`${API_BASE}/documents/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: projectId, doc_type: docType })
        });
        return response.json();
    },

    /**
     * 提取JSON规格
     */
    async extractSpec(projectId, docType) {
        const response = await fetch(`${API_BASE}/documents/extract-spec`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_id: projectId, doc_type: docType })
        });
        return response.json();
    },

    /**
     * 获取规格文件
     */
    async getSpec(projectId, specType) {
        const response = await fetch(`${API_BASE}/documents/${projectId}/specs/${specType}`);
        if (!response.ok) {
            throw new Error('规格文件不存在');
        }
        return response.json();
    },

    /**
     * 获取规格文件列表
     */
    async getSpecList(projectId) {
        const response = await fetch(`${API_BASE}/documents/${projectId}/specs`);
        return response.json();
    },

    /**
     * 启动游戏预览
     */
    async startGame(projectId) {
        const response = await fetch(`${API_BASE}/game/${projectId}/start`, {
            method: 'POST'
        });
        return response.json();
    },

    /**
     * 停止游戏预览
     */
    async stopGame(projectId) {
        const response = await fetch(`${API_BASE}/game/${projectId}/stop`, {
            method: 'POST'
        });
        return response.json();
    },

    /**
     * 生成单个资源脚本
     */
    async generateResourceScript(projectId, specType, itemId, options = {}) {
        const { force_regenerate_script, ...params } = options;
        const response = await fetch(`${API_BASE}/resources/${projectId}/generate-item`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                spec_type: specType,
                item_id: itemId,
                params: params,
                variant_count: 3,
                force_regenerate_script: !!force_regenerate_script
            })
        });
        return response.json();
    },

    /**
     * 获取资源变体列表
     */
    async getResourceVariants(projectId, resourceType, itemId) {
        const response = await fetch(`${API_BASE}/resources/${projectId}/${resourceType}/${itemId}/variants`);
        return response.json();
    },

    /**
     * 选择资源变体
     */
    async selectVariant(projectId, resourceType, itemId, variantId) {
        const response = await fetch(`${API_BASE}/resources/${projectId}/${resourceType}/${itemId}/select/${variantId}`, {
            method: 'POST'
        });
        return response.json();
    },

    /**
     * 生成角色序列帧动画
     */
    async generateAnimations(projectId, itemId, description, style) {
        const response = await fetch(`${API_BASE}/resources/${projectId}/generate-animations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, description: description, style: style })
        });
        return response.json();
    },

    /**
     * 清理特定项的临时缓存
     */
    async clearItemTemp(projectId, specType, itemId) {
        const response = await fetch(`${API_BASE}/resources/${projectId}/temp/${specType}/${itemId}`, {
            method: 'DELETE'
        });
        return response.json();
    },

    /**
     * 上传角色序列帧动画
     */
    async uploadAnimations(projectId, itemId, file, animType = 'full') {
        const formData = new FormData();
        formData.append('item_id', itemId);
        formData.append('anim_type', animType);
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/resources/${projectId}/upload-animations`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }
};
