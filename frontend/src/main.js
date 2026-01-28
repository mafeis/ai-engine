/**
 * AI 游戏引擎 - 前端主入口
 * 
 * 功能:
 * - 项目管理 (创建/列表/选择)
 * - 文档查看与渲染 (Markdown)
 * - 与后端 API 通信
 */

// API 基础地址
const API_BASE = 'http://localhost:8000/api';

// ============ API 服务 ============

const api = {
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
    }
};

// ============ 状态管理 ============

const state = {
    projects: [],
    currentProject: null,
    currentDocument: null,
    isEditing: false
};

let phaserGame = null;

// ============ Markdown 渲染配置 ============

// 配置 marked
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

/**
 * 渲染 Markdown 内容
 */
function renderMarkdown(content) {
    if (typeof marked !== 'undefined') {
        return marked.parse(content);
    }
    // 如果 marked 未加载，返回预格式化文本
    return `<pre>${content}</pre>`;
}

// ============ UI 更新函数 ============

/**
 * 渲染项目列表
 */
function renderProjectList() {
    const container = document.getElementById('project-list');

    if (state.projects.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <span>暂无项目</span>
                <small>点击上方按钮创建第一个游戏</small>
            </div>
        `;
        return;
    }

    container.innerHTML = state.projects.map(project => `
        <div class="project-item ${state.currentProject?.id === project.id ? 'active' : ''}" 
             data-id="${project.id}">
            <h3>${project.name}</h3>
            <p>${project.intro}</p>
            <span class="project-status status-${project.status}">${getStatusText(project.status)}</span>
        </div>
    `).join('');

    // 绑定点击事件
    container.querySelectorAll('.project-item').forEach(item => {
        item.addEventListener('click', () => {
            selectProject(item.dataset.id);
        });
    });
}

/**
 * 获取状态文本
 */
function getStatusText(status) {
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
 * 选择项目
 */
async function selectProject(projectId) {
    try {
        const project = await api.getProject(projectId);
        state.currentProject = project;

        // 更新列表高亮
        document.querySelectorAll('.project-item').forEach(item => {
            item.classList.toggle('active', item.dataset.id === projectId);
        });

        // 显示项目详情
        await renderProjectPanel(project);
    } catch (error) {
        console.error('获取项目失败:', error);
    }
}

/**
 * 渲染项目详情面板（含文档列表）
 */
async function renderProjectPanel(project) {
    const welcomePanel = document.getElementById('welcome-panel');
    const projectPanel = document.getElementById('project-panel');
    const documentPanel = document.getElementById('document-panel');

    welcomePanel.classList.add('hidden');
    documentPanel.classList.add('hidden');
    projectPanel.classList.remove('hidden');

    // 获取文档列表
    let docListHtml = '<p class="loading">加载文档列表中...</p>';

    try {
        const docData = await api.getDocumentList(project.id);

        if (docData.documents && docData.documents.length > 0) {
            docListHtml = `
                <div class="document-grid">
                    ${docData.documents.map(doc => `
                        <div class="doc-card ${doc.exists ? 'exists' : 'empty'}" 
                             data-type="${doc.doc_type}" 
                             data-exists="${doc.exists}">
                            <div class="doc-icon">${getDocIcon(doc.doc_type)}</div>
                            <div class="doc-info">
                                <h4>${doc.title}</h4>
                                <span class="doc-status">${doc.exists ? '✓ 已生成' : '○ 未生成'}</span>
                            </div>
                            <button class="btn btn-sm ${doc.exists ? 'btn-view' : 'btn-generate'}" 
                                    onclick="handleDocAction('${project.id}', '${doc.doc_type}', ${doc.exists})">
                                ${doc.exists ? '查看' : '生成'}
                            </button>
                        </div>
                    `).join('')}
                </div>
                <div class="doc-summary">
                    <span>已生成 ${docData.generated} / ${docData.total} 个文档</span>
                    <button class="btn btn-primary" onclick="generateAllDocuments('${project.id}')">
                        🔄 生成全部
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('获取文档列表失败:', error);
        docListHtml = '<p class="error">加载文档列表失败</p>';
    }

    // 获取规格列表
    let specListHtml = '<p class="loading">加载规格列表中...</p>';

    try {
        const specData = await api.getSpecList(project.id);

        if (specData.specs && specData.specs.length > 0) {
            specListHtml = `
                <div class="spec-grid">
                    ${specData.specs.map(spec => `
                        <div class="spec-card ${spec.exists ? 'exists' : 'empty'}" 
                             data-type="${spec.spec_type}">
                            <div class="spec-icon">{ }</div>
                            <div class="spec-info">
                                <h4>${spec.title.replace('设计文档', '规格')}</h4>
                                <span class="spec-status">${spec.exists ? `✓ ${spec.item_count || 0} 条数据` : '○ 未提取'}</span>
                            </div>
                            <div class="spec-actions">
                                ${spec.exists ? `
                                    <button class="btn btn-sm btn-view" onclick="viewSpec('${project.id}', '${spec.spec_type}')">
                                        查看
                                    </button>
                                ` : ''}
                                <button class="btn btn-sm btn-generate" onclick="extractSpec('${project.id}', '${spec.spec_type}')">
                                    ${spec.exists ? '重新提取' : '提取'}
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="spec-summary">
                    <span>已提取 ${specData.extracted} / ${specData.total} 个规格</span>
                    <button class="btn btn-primary" onclick="extractAllSpecs('${project.id}')">
                        📊 提取全部
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('获取规格列表失败:', error);
        specListHtml = '<p class="muted">先生成设计文档，然后才能提取规格数据</p>';
    }

    projectPanel.innerHTML = `
        <div class="project-header">
            <h1>${project.name}</h1>
            <span class="project-status status-${project.status}">${getStatusText(project.status)}</span>
        </div>
        
        <p class="project-intro">${project.intro}</p>
        
        <div class="project-meta">
            <span>🎮 ${project.game_type}</span>
            <span>🎨 ${project.art_style}</span>
            <span>📅 ${new Date(project.created_at).toLocaleDateString()}</span>
        </div>
        
        <div class="section">
            <h2>📝 第一步：设计文档</h2>
            ${docListHtml}
        </div>
        
        <div class="section">
            <h2>📊 第二步：JSON 规格数据</h2>
            <p class="section-desc">从设计文档中提取结构化的JSON数据，用于资源生成</p>
            ${specListHtml}
        </div>
        
        <div class="section">
            <h2>🎨 第三步：生成资源</h2>
            <p class="section-desc">点击资源类型进入管理面板，查看每个条目的详情并生成候选变体</p>
            <div class="resource-actions">
                <div class="resource-type-card clickable" onclick="showResourcePanel('${project.id}', 'character')">
                    <span class="icon">👤</span>
                    <span class="label">角色资源</span>
                    <span class="arrow">→</span>
                </div>
                <div class="resource-type-card clickable" onclick="showResourcePanel('${project.id}', 'scene')">
                    <span class="icon">🏞️</span>
                    <span class="label">场景资源</span>
                    <span class="arrow">→</span>
                </div>
                <div class="resource-type-card clickable" onclick="showResourcePanel('${project.id}', 'item')">
                    <span class="icon">🎒</span>
                    <span class="label">道具资源</span>
                    <span class="arrow">→</span>
                </div>
                <div class="resource-type-card clickable" onclick="showResourcePanel('${project.id}', 'ui')">
                    <span class="icon">�️</span>
                    <span class="label">UI资源</span>
                    <span class="arrow">→</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🚀 第四步：实时预览</h2>
            <p class="section-desc">在选定的场景中控制角色移动，体验游戏的雏形</p>
            <div class="resource-actions">
                <div class="resource-type-card clickable highlight" onclick="showPreviewPanel('${project.id}')">
                    <span class="icon">�️</span>
                    <span class="label">启动实时游戏预览</span>
                    <span class="arrow">→</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎮 游戏控制</h2>
            <div class="game-controls-panel">
                <button class="btn btn-primary btn-lg" onclick="startGame('${project.id}')">
                    ▶ 启动预览
                </button>
                <button class="btn btn-secondary btn-lg" onclick="stopGame('${project.id}')">
                    ⏹ 停止
                </button>
            </div>
        </div>
        
        <div class="danger-zone">
            <button class="btn btn-danger" onclick="deleteProject('${project.id}')">
                🗑️ 删除项目
            </button>
        </div>
    `;
}

/**
 * 获取文档图标
 */
function getDocIcon(docType) {
    const icons = {
        main: '📋',
        character: '👤',
        gameplay: '🎯',
        scene: '🏞️',
        item: '🎒',
        quest: '📜',
        ui: '🖥️',
        audio: '🔊'
    };
    return icons[docType] || '📄';
}

/**
 * 处理文档操作（查看或生成）
 */
async function handleDocAction(projectId, docType, exists) {
    if (exists) {
        await viewDocument(projectId, docType);
    } else {
        await generateSingleDocument(projectId, docType);
    }
}

/**
 * 查看文档
 */
async function viewDocument(projectId, docType) {
    try {
        const doc = await api.getDocument(projectId, docType);
        state.currentDocument = { projectId, docType, content: doc.content };

        const projectPanel = document.getElementById('project-panel');
        const documentPanel = document.getElementById('document-panel');

        projectPanel.classList.add('hidden');
        documentPanel.classList.remove('hidden');

        // 设置标题
        const titles = {
            main: '游戏设计文档',
            character: '角色设计文档',
            gameplay: '玩法设计文档',
            scene: '场景设计文档',
            item: '道具设计文档',
            quest: '任务设计文档',
            ui: 'UI设计文档',
            audio: '音频设计文档'
        };
        document.getElementById('document-title').textContent = titles[docType] || '文档';

        // 渲染 Markdown
        const contentDiv = document.getElementById('document-content');
        contentDiv.innerHTML = renderMarkdown(doc.content);

        // 代码高亮
        if (typeof hljs !== 'undefined') {
            contentDiv.querySelectorAll('pre code').forEach((el) => {
                hljs.highlightElement(el);
            });
        }

        // 重置编辑状态
        state.isEditing = false;
        document.getElementById('edit-doc-btn').style.display = 'inline-block';
        document.getElementById('save-doc-btn').style.display = 'none';
        document.getElementById('document-editor').classList.add('hidden');
        document.getElementById('document-content').classList.remove('hidden');

        // 显示提取规格按钮（main文档不需要提取）
        const extractBtn = document.getElementById('extract-spec-btn');
        if (extractBtn) {
            if (docType !== 'main') {
                extractBtn.style.display = 'inline-block';
                extractBtn.onclick = () => extractSpecFromDoc(projectId, docType);
            } else {
                extractBtn.style.display = 'none';
            }
        }

    } catch (error) {
        console.error('获取文档失败:', error);
        alert('获取文档失败: ' + error.message);
    }
}

/**
 * 生成单个文档
 */
async function generateSingleDocument(projectId, docType) {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = '生成中...';
    btn.disabled = true;

    try {
        await api.generateDocument(projectId, docType);
        // 刷新项目面板以更新文档列表
        await renderProjectPanel(state.currentProject);
    } catch (error) {
        console.error('生成文档失败:', error);
        alert('生成文档失败: ' + error.message);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

/**
 * 生成所有文档
 */
async function generateAllDocuments(projectId) {
    const docTypes = ['main', 'character', 'gameplay', 'scene', 'item', 'quest', 'ui', 'audio'];

    for (const docType of docTypes) {
        console.log(`正在生成 ${docType} 文档...`);
        try {
            await api.generateDocument(projectId, docType);
        } catch (error) {
            console.error(`生成 ${docType} 文档失败:`, error);
        }
    }

    // 刷新面板
    await renderProjectPanel(state.currentProject);
    alert('所有文档生成完成！');
}

/**
 * 返回项目详情
 */
function backToProject() {
    const projectPanel = document.getElementById('project-panel');
    const documentPanel = document.getElementById('document-panel');
    const previewPanel = document.getElementById('preview-panel');

    documentPanel.classList.add('hidden');
    previewPanel.classList.add('hidden');
    projectPanel.classList.remove('hidden');

    // 停止运行中的游戏
    if (typeof stopInteractivePreview === 'function') {
        stopInteractivePreview();
    }
}

/**
 * 切换编辑模式
 */
function toggleEditMode() {
    state.isEditing = !state.isEditing;

    const contentDiv = document.getElementById('document-content');
    const editorArea = document.getElementById('document-editor');
    const editBtn = document.getElementById('edit-doc-btn');
    const saveBtn = document.getElementById('save-doc-btn');

    if (state.isEditing) {
        // 进入编辑模式
        editorArea.value = state.currentDocument.content;
        contentDiv.classList.add('hidden');
        editorArea.classList.remove('hidden');
        editBtn.style.display = 'none';
        saveBtn.style.display = 'inline-block';
    } else {
        // 退出编辑模式
        contentDiv.classList.remove('hidden');
        editorArea.classList.add('hidden');
        editBtn.style.display = 'inline-block';
        saveBtn.style.display = 'none';
    }
}

/**
 * 保存文档
 */
async function saveDocument() {
    const content = document.getElementById('document-editor').value;

    try {
        await api.saveDocument(
            state.currentDocument.projectId,
            state.currentDocument.docType,
            content
        );

        // 更新状态和视图
        state.currentDocument.content = content;
        document.getElementById('document-content').innerHTML = renderMarkdown(content);

        // 退出编辑模式
        toggleEditMode();

        alert('文档已保存！');
    } catch (error) {
        console.error('保存文档失败:', error);
        alert('保存失败: ' + error.message);
    }
}

// ============ 操作函数 ============

/**
 * 加载项目列表
 */
async function loadProjects() {
    try {
        const data = await api.getProjects();
        state.projects = data.projects;
        renderProjectList();
    } catch (error) {
        console.error('加载项目列表失败:', error);
    }
}

/**
 * 创建项目
 */
async function createProject(formData) {
    try {
        const project = await api.createProject(formData);
        state.projects.unshift(project);
        renderProjectList();
        selectProject(project.id);
        return project;
    } catch (error) {
        console.error('创建项目失败:', error);
        throw error;
    }
}

/**
 * 删除项目
 */
async function deleteProject(projectId) {
    if (!confirm('确定要删除这个项目吗？此操作不可恢复。')) {
        return;
    }

    try {
        await api.deleteProject(projectId);
        state.projects = state.projects.filter(p => p.id !== projectId);
        state.currentProject = null;
        renderProjectList();

        // 显示欢迎面板
        document.getElementById('welcome-panel').classList.remove('hidden');
        document.getElementById('project-panel').classList.add('hidden');
        document.getElementById('document-panel').classList.add('hidden');
    } catch (error) {
        console.error('删除项目失败:', error);
    }
}

/**
 * 启动游戏
 */
async function startGame(projectId) {
    try {
        const result = await api.startGame(projectId);
        if (result.url) {
            window.open(result.url, '_blank');
        }
        alert('游戏已启动！');
    } catch (error) {
        console.error('启动游戏失败:', error);
        alert('启动游戏失败: ' + error.message);
    }
}

/**
 * 停止游戏
 */
async function stopGame(projectId) {
    try {
        await api.stopGame(projectId);
        alert('游戏已停止');
    } catch (error) {
        console.error('停止游戏失败:', error);
    }
}

// ============ 事件绑定 ============

document.addEventListener('DOMContentLoaded', () => {
    // 加载项目列表
    loadProjects();

    // 创建项目按钮
    const createBtn = document.getElementById('create-project-btn');
    const dialog = document.getElementById('create-project-dialog');
    const form = document.getElementById('create-project-form');

    createBtn.addEventListener('click', () => {
        dialog.showModal();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            name: form.elements.name.value,
            intro: form.elements.intro.value,
            game_type: form.elements.game_type.value,
            art_style: form.elements.art_style.value
        };

        try {
            await createProject(formData);
            dialog.close();
            form.reset();
        } catch (error) {
            alert('创建失败: ' + error.message);
        }
    });

    // 返回按钮
    document.getElementById('back-to-project').addEventListener('click', backToProject);

    // 编辑按钮
    document.getElementById('edit-doc-btn').addEventListener('click', toggleEditMode);

    // 保存按钮
    document.getElementById('save-doc-btn').addEventListener('click', saveDocument);

    // 资源面板返回按钮
    document.getElementById('back-from-resource').addEventListener('click', backFromResource);
});

// ============ 规格相关函数 ============

/**
 * 从文档页面提取规格（文档查看页的入口）
 */
async function extractSpecFromDoc(projectId, docType) {
    const btn = document.getElementById('extract-spec-btn');
    const originalText = btn.textContent;
    btn.textContent = '提取中...';
    btn.disabled = true;

    try {
        const result = await api.extractSpec(projectId, docType);
        console.log(`${docType} 规格提取完成:`, result);

        // 提取完成后，直接跳转到规格查看
        await viewSpec(projectId, docType);

        alert('规格提取成功！');
    } catch (error) {
        console.error('提取规格失败:', error);
        alert('提取规格失败: ' + error.message);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

/**
 * 提取单个规格
 */
async function extractSpec(projectId, docType) {
    try {
        // 显示加载提示
        const result = await api.extractSpec(projectId, docType);
        console.log(`${docType} 规格提取完成:`, result);

        // 刷新项目面板
        await renderProjectPanel(state.currentProject);

    } catch (error) {
        console.error('提取规格失败:', error);
        alert('提取规格失败: ' + error.message);
    }
}

/**
 * 提取所有规格
 */
async function extractAllSpecs(projectId) {
    const specTypes = ['character', 'scene', 'item', 'audio', 'gameplay', 'quest', 'ui'];

    for (const specType of specTypes) {
        console.log(`正在提取 ${specType} 规格...`);
        try {
            await api.extractSpec(projectId, specType);
        } catch (error) {
            console.error(`提取 ${specType} 规格失败:`, error);
        }
    }

    // 刷新面板
    await renderProjectPanel(state.currentProject);
    alert('所有规格提取完成！');
}

/**
 * 查看规格数据
 */
async function viewSpec(projectId, specType) {
    try {
        const data = await api.getSpec(projectId, specType);

        const projectPanel = document.getElementById('project-panel');
        const documentPanel = document.getElementById('document-panel');

        projectPanel.classList.add('hidden');
        documentPanel.classList.remove('hidden');

        // 设置标题
        const titles = {
            character: '角色规格数据',
            scene: '场景规格数据',
            item: '道具规格数据',
            audio: '音频规格数据',
            gameplay: '玩法规格数据',
            quest: '任务规格数据',
            ui: 'UI规格数据'
        };
        document.getElementById('document-title').textContent = titles[specType] || 'JSON 规格';

        // 格式化 JSON 显示
        const contentDiv = document.getElementById('document-content');
        const jsonContent = JSON.stringify(data.spec, null, 2);
        contentDiv.innerHTML = `<pre><code class="language-json">${escapeHtml(jsonContent)}</code></pre>`;

        // 代码高亮
        if (typeof hljs !== 'undefined') {
            contentDiv.querySelectorAll('pre code').forEach((el) => {
                hljs.highlightElement(el);
            });
        }

        // 隐藏编辑按钮（暂不支持编辑JSON）
        document.getElementById('edit-doc-btn').style.display = 'none';
        document.getElementById('save-doc-btn').style.display = 'none';

    } catch (error) {
        console.error('获取规格失败:', error);
        alert('获取规格失败: ' + error.message);
    }
}

/**
 * HTML 转义
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ 资源生成函数 ============

/**
 * 生成资源脚本
 */
async function generateResources(projectId, specType) {
    try {
        const response = await fetch(`${API_BASE}/resources/${projectId}/generate-from-spec?spec_type=${specType}`, {
            method: 'POST'
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || '生成失败');
        }

        alert(`✓ ${result.message}\n\n已生成 ${result.generated_count} 个脚本文件`);
        console.log('生成结果:', result);

    } catch (error) {
        console.error('生成资源脚本失败:', error);
        alert('生成失败: ' + error.message);
    }
}

/**
 * 执行资源脚本
 */
async function runResourceScripts(projectId, specType) {
    try {
        const response = await fetch(`${API_BASE}/resources/${projectId}/run-scripts/${specType}`, {
            method: 'POST'
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || '执行失败');
        }

        alert(`✓ 执行完成\n\n成功: ${result.success} / ${result.total}`);
        console.log('执行结果:', result);

    } catch (error) {
        console.error('执行脚本失败:', error);
        alert('执行失败: ' + error.message);
    }
}

// ============ 资源管理面板 ============

/**
 * 显示资源管理面板
 */
async function showResourcePanel(projectId, specType) {
    try {
        // 获取规格数据
        const specData = await api.getSpec(projectId, specType);

        // 解析条目列表
        let items = [];
        const spec = specData.spec;
        if (specType === 'character') items = spec.characters || [];
        else if (specType === 'scene') items = spec.scenes || [];
        else if (specType === 'item') items = spec.items || [];
        else if (specType === 'audio') items = (spec.bgm || []).concat(spec.sfx || []);
        else if (specType === 'ui') items = spec.elements || [];

        // 切换面板
        document.getElementById('project-panel').classList.add('hidden');
        document.getElementById('resource-panel').classList.remove('hidden');

        // 设置标题
        const titles = {
            character: '角色资源管理',
            scene: '场景资源管理',
            item: '道具资源管理',
            audio: '音频资源管理',
            ui: 'UI资源管理'
        };
        document.getElementById('resource-panel-title').textContent = titles[specType] || '资源管理';

        // 保存状态
        state.currentSpecType = specType;

        // 渲染条目列表
        const listContainer = document.getElementById('resource-items-list');
        listContainer.innerHTML = `
            <div class="row items-center justify-between mb-4">
                <h3>${titles[specType] || '资源'}列表</h3>
                <button class="btn btn-danger btn-sm" onclick="clearTempDirectory('${projectId}')">
                    🗑️ 清理所有生成缓存
                </button>
            </div>
            <div class="resource-items">
                ${items.map(item => `
                    <div class="resource-item-card" id="card-${item.id}">
                        <div class="resource-item-header">
                            <span class="item-name">${item.name || item.id}</span>
                            <span class="item-id">#${item.id}</span>
                        </div>
                        <div class="resource-item-desc">
                            ${getItemDescription(item, specType)}
                        </div>
                        <div class="resource-item-params">
                            ${renderItemParams(item, specType)}
                        </div>
                        <div class="resource-item-actions">
                            <button class="btn btn-primary btn-sm" onclick="generateItemVariants('${projectId}', '${specType}', '${item.id}')">
                                🎨 智能生成 (1+3风格)
                            </button>
                            <button class="btn btn-secondary btn-sm" onclick="generateItemVariants('${projectId}', '${specType}', '${item.id}', true)">
                                🔄 重新AI设计并生成
                            </button>
                            <button class="btn btn-secondary btn-sm" onclick="viewItemVariants('${projectId}', '${specType}', '${item.id}')">
                                📂 查看变体
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="clearItemTempDirectory('${projectId}', '${specType}', '${item.id}')" title="清理该条目的生成脚本和变体缓存">
                                🗑️ 清理项缓存
                            </button>
                        </div>
                        <div class="variants-container" id="variants-${item.id}">
                            <!-- 变体列表将在此处渲染 -->
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        // 自动加载所有条目的变体/选定状态
        setTimeout(() => {
            items.forEach(item => {
                viewItemVariants(projectId, specType, item.id);
            });
        }, 100);

    } catch (error) {
        console.error('加载资源面板失败:', error);
        alert('加载失败: ' + error.message);
    }
}

/**
 * 获取条目描述
 */
function getItemDescription(item, specType) {
    if (specType === 'character') return item.appearance || '';
    if (specType === 'scene') return item.description || '';
    if (specType === 'item') return item.appearance || item.description || '';
    return item.description || item.name || '';
}

/**
 * 渲染条目参数
 */
function renderItemParams(item, specType) {
    if (specType === 'character' && item.stats) {
        return `
            <span class="param">HP: ${item.stats.hp || '-'}</span>
            <span class="param">攻击: ${item.stats.attack || '-'}</span>
            <span class="param">防御: ${item.stats.defense || '-'}</span>
        `;
    }
    if (specType === 'scene' && item.size) {
        return `<span class="param">尺寸: ${item.size.width || 320}x${item.size.height || 180}</span>`;
    }
    return '';
}

/**
 * 生成单个条目的多个变体
 */
async function generateItemVariants(projectId, specType, itemId, forceRegen = false) {
    const btn = event.target;
    // 如果是图标按钮，找到最近的button元素
    const targetBtn = btn.tagName === 'BUTTON' ? btn : btn.closest('button');
    const originalText = targetBtn.textContent;

    targetBtn.textContent = forceRegen ? 'AI 重新设计中...' : '资源创作中...';
    targetBtn.disabled = true;

    try {
        const result = await api.generateResourceScript(projectId, specType, itemId, {
            force_regenerate_script: forceRegen
        });

        console.log('变体生成结果:', result);

        // 渲染变体
        const container = document.getElementById(`variants-${itemId}`);
        container.innerHTML = renderVariantsHtml(result.variants, projectId, specType, itemId);

        alert(`✓ 成功创作 ${result.variants.length} 组资源方案`);

    } catch (error) {
        console.error('生成变体失败:', error);
        alert('生成失败: ' + error.message);
    } finally {
        targetBtn.textContent = originalText;
        targetBtn.disabled = false;
    }
}

/**
 * 清理单个条目的临时目录
 */
async function clearItemTempDirectory(projectId, specType, itemId) {
    if (!confirm('确定要清理该条目的生成缓存吗？')) {
        return;
    }

    try {
        const result = await api.clearItemTemp(projectId, specType, itemId);

        if (result.success) {
            // 清空对应变体容器
            const container = document.getElementById(`variants-${itemId}`);
            if (container) {
                container.innerHTML = '<p class="muted">缓存已清理</p>';
            }
            alert('✓ 清理成功');
        } else {
            alert('清理失败: ' + result.message);
        }
    } catch (error) {
        console.error('清理失败:', error);
        alert('清理失败: ' + error.message);
    }
}

/**
 * 清理临时目录
 */
async function clearTempDirectory(projectId) {
    if (!confirm('确定要清理所有生成的脚本和变体缓存吗？这将删除 temp 目录下的所有内容。')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/resources/${projectId}/temp`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (result.success) {
            alert('清理成功！所有缓存已删除。');

            // 清空当前显示的所有变体列表
            const containers = document.querySelectorAll('.variants-container');
            containers.forEach(el => {
                el.innerHTML = '<p class="muted">已清理缓存</p>';
            });

            console.log('临时目录清理成功');
        } else {
            alert('清理失败: ' + result.message);
        }
    } catch (error) {
        console.error('清理失败:', error);
        alert('清理失败: ' + error.message);
    }
}

/**
 * 查看条目的变体列表
 */
async function viewItemVariants(projectId, specType, itemId) {
    try {
        const resourceType = specType === 'audio' ? 'sfx' : specType;
        const result = await api.getResourceVariants(projectId, resourceType, itemId);

        const container = document.getElementById(`variants-${itemId}`);
        if (result.variants && result.variants.length > 0) {
            container.innerHTML = renderVariantsHtml(result, projectId, specType, itemId);
        } else {
            container.innerHTML = '<p class="muted">暂无方案，点击“智能生成 (1+3风格)”开始创作</p>';
        }

    } catch (error) {
        console.error('获取变体失败:', error);
    }
}

/**
 * 渲染变体HTML
 */
function renderVariantsHtml(result, projectId, specType, itemId) {
    const variants = result.variants || [];
    const animation = result.animation;
    const selectedVariant = variants.find(v => v.selected);

    // 如果已经选择了某个版本，展示精简的“已选定”视图
    if (selectedVariant) {
        let imgUrl = '';
        if (selectedVariant.exists && selectedVariant.file_path) {
            const match = selectedVariant.file_path.match(/projects[\\\/](.+)/);
            if (match) {
                imgUrl = 'http://localhost:8000/assets/' + match[1].replace(/\\/g, '/');
            }
        }

        const badgeText = selectedVariant.is_final ? '✓ 资产库正式版本' : '✓ 候选已选定';
        let html = '<div class="selected-resource-view">';
        html += '<div class="selected-main-card mb-3">';
        html += '   <div class="selected-badge">' + badgeText + '</div>';
        html += '   <div class="selected-preview"><img src="' + imgUrl + '" alt="已选定方案"></div>';
        html += '   <div class="selected-actions">';
        html += '       <button class="btn btn-outline-secondary btn-sm" onclick="generateItemVariants(\'' + projectId + '\', \'' + specType + '\', \'' + itemId + '\')">🔄 重新生成</button>';

        if (specType === 'character') {
            html += '       <button class="btn btn-warning btn-sm" onclick="generateCharacterAnimations(\'' + projectId + '\', \'' + itemId + '\')">🎬 ' + (animation && animation.exists ? '重新生成动画' : '生成动画序列') + '</button>';
        }
        html += '   </div>';
        html += '</div>';

        // 如果是角色且有动画，展示序列帧预览
        if (specType === 'character' && animation && animation.exists) {
            const sheetUrl = 'http://localhost:8000' + animation.spritesheet_url;
            html += '<div class="animation-preview-panel">';
            html += '   <h4>🏃 动画预览</h4>';
            html += '   <div class="animation-grid">';

            const actions = [
                { name: '待机 (Idle)', row: 0 },
                { name: '行走 (Walk)', row: 1 },
                { name: '攻击 (Attack)', row: 2 }
            ];

            actions.forEach(action => {
                html += '<div class="anim-preview-item">';
                html += '   <div class="anim-sprite-box" style="width:64px; height:64px; overflow:hidden; border:1px solid var(--border); background:rgba(255,255,255,0.05); border-radius:4px; margin:0 auto 8px;">';
                html += '       <div class="anim-sprite" style="width:256px; height:64px; background-image: url(\'' + sheetUrl + '\'); background-position: 0 -' + (action.row * 64) + 'px; animation: playSprite 0.8s steps(4) infinite;"></div>';
                html += '   </div>';
                html += '   <div class="anim-name-small">' + action.name + '</div>';
                html += '</div>';
            });

            html += '   </div>';
            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    let html = '<div class="variants-grid">';

    variants.forEach((v, idx) => {
        // 从绝对路径提取相对路径用于访问静态文件
        let imgUrl = '';
        if (v.exists && v.file_path) {
            const match = v.file_path.match(/projects[\\\/](.+)/);
            if (match) {
                imgUrl = 'http://localhost:8000/assets/' + match[1].replace(/\\/g, '/');
            }
        }

        const selectedClass = v.selected ? 'selected' : '';
        const btnClass = v.selected ? 'btn-secondary' : 'btn-primary';
        const btnText = v.selected ? '✓ 已选择' : '选择此版本';

        let previewHtml = '';
        if (v.error) {
            previewHtml = '<span class="no-preview error" title="' + v.error + '">生成失败</span>';
        } else if (v.exists && imgUrl) {
            previewHtml = '<img src="' + imgUrl + '" alt="变体' + (idx + 1) + '" onerror="this.parentElement.innerHTML=\'<span class=no-preview>加载失败</span>\'">';
        } else {
            previewHtml = '<span class="no-preview">生成中...</span>';
        }

        html += '<div class="variant-card" data-variant-id="' + v.variant_id + '">';
        html += '<div class="variant-preview">' + previewHtml + '</div>';
        html += '<div class="variant-info">';
        html += '<span class="variant-name">方案 ' + (idx + 1) + '</span>';
        html += '<span class="variant-seed">种子: ' + (v.seed || idx + 1) + '</span>';
        html += '</div>';
        html += '<div class="row gap-2">';
        html += '<button class="btn btn-sm btn-primary w-full" onclick="selectVariant(\'' + projectId + '\', \'' + specType + '\', \'' + itemId + '\', \'' + v.variant_id + '\')">选择此方案</button>';
        html += '</div>';
        html += '</div>';
    });

    html += '</div>';
    return html;
}

/**
 * 选择变体
 */
async function selectVariant(projectId, specType, itemId, variantId) {
    try {
        const resourceType = specType === 'audio' ? 'sfx' : specType;
        await api.selectVariant(projectId, resourceType, itemId, variantId);

        // 刷新变体显示
        await viewItemVariants(projectId, specType, itemId);

        alert('✓ 已选择此变体作为最终资源');

    } catch (error) {
        console.error('选择变体失败:', error);
        alert('选择失败: ' + error.message);
    }
}

/**
 * 生成角色序列帧动画
 */
async function generateCharacterAnimations(projectId, itemId) {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = '动画设计中...';
    btn.disabled = true;

    try {
        // 先获取描述 (简单从卡片里拿或者在这里重新获取)
        const card = document.getElementById(`card-${itemId}`);
        const desc = card ? card.querySelector('.resource-item-desc').textContent.trim() : '游戏角色';

        const result = await api.generateAnimations(projectId, itemId, desc);

        if (result.success) {
            alert('✓ 序列帧动画设计完成！');
            // 刷新显示以展示动画预览
            await viewItemVariants(projectId, 'character', itemId);
        }
    } catch (error) {
        console.error('动画生成失败:', error);
        alert('动画创作失败: ' + error.message);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

/**
 * 显示预览面板
 */
async function showPreviewPanel(projectId) {
    try {
        // 1. 获取规格
        const charSpec = await api.getSpec(projectId, 'character').catch(() => ({ spec: { characters: [] } }));
        const sceneSpec = await api.getSpec(projectId, 'scene').catch(() => ({ spec: { scenes: [] } }));

        const characters = charSpec.spec.characters || [];
        const scenes = sceneSpec.spec.scenes || [];

        // 2. 检查哪些有资源 (已选定)
        const readyCharacters = [];
        const readyScenes = [];

        for (const char of characters) {
            try {
                const result = await api.getResourceVariants(projectId, 'character', char.id);
                const selected = result.variants.find(v => v.selected);
                if (selected) {
                    readyCharacters.push({
                        id: char.id,
                        name: char.name,
                        imgUrl: getAssetUrl(projectId, 'characters', char.id, selected.file_path),
                        animation: result.animation
                    });
                }
            } catch (e) { }
        }

        for (const scene of scenes) {
            try {
                const result = await api.getResourceVariants(projectId, 'scene', scene.id);
                const selected = result.variants.find(v => v.selected);
                if (selected) {
                    readyScenes.push({
                        id: scene.id,
                        name: scene.name,
                        imgUrl: getAssetUrl(projectId, 'scenes', scene.id, selected.file_path)
                    });
                }
            } catch (e) { }
        }

        if (readyCharacters.length === 0 || readyScenes.length === 0) {
            alert('请先在“资源管理”中为至少一个场景和一个角色选择（选定）方案。');
            return;
        }

        // 3. 填充下拉框
        const charSelect = document.getElementById('preview-character-select');
        const monsterSelect = document.getElementById('preview-monster-select');
        const sceneSelect = document.getElementById('preview-scene-select');

        const charOptions = '<option value="">选择主角...</option>' +
            readyCharacters.map(c => `<option value="${c.id}" data-assets='${JSON.stringify(c).replace(/'/g, "&apos;")}'>${c.name}</option>`).join('');

        charSelect.innerHTML = charOptions;
        monsterSelect.innerHTML = '<option value="">选择怪物 (可选)...</option>' +
            readyCharacters.map(c => `<option value="${c.id}" data-assets='${JSON.stringify(c).replace(/'/g, "&apos;")}'>${c.name}</option>`).join('');

        sceneSelect.innerHTML = '<option value="">选择场景...</option>' +
            readyScenes.map(s => `<option value="${s.id}" data-assets='${JSON.stringify(s).replace(/'/g, "&apos;")}'>${s.name}</option>`).join('');

        // 4. 切换面板
        document.getElementById('project-panel').classList.add('hidden');
        document.getElementById('preview-panel').classList.remove('hidden');

        // 5. 绑定按钮与实时切换事件
        document.getElementById('start-game-btn').onclick = () => startInteractivePreview(projectId);
        document.getElementById('stop-game-btn').onclick = stopInteractivePreview;

        const syncRefresh = () => {
            if (phaserGame && sceneSelect.value && charSelect.value) {
                startInteractivePreview(projectId);
            }
        };
        sceneSelect.onchange = syncRefresh;
        charSelect.onchange = syncRefresh;
        monsterSelect.onchange = syncRefresh;

    } catch (error) {
        console.error('显示预览面板失败:', error);
        alert('无法加载预览数据: ' + error.message);
    }
}

/**
 * 获取资源实际可用的URL
 */
function getAssetUrl(projectId, folder, itemId, filePath) {
    if (filePath) {
        const match = filePath.match(/projects[\\\/](.+)/);
        if (match) {
            return 'http://localhost:8000/assets/' + match[1].replace(/\\/g, '/');
        }
    }
    return '';
}

/**
 * 启动交互式预览 (基于 Phaser)
 */
function startInteractivePreview(projectId) {
    const charSelect = document.getElementById('preview-character-select');
    const monsterSelect = document.getElementById('preview-monster-select');
    const sceneSelect = document.getElementById('preview-scene-select');

    if (!charSelect.value || !sceneSelect.value) {
        alert('请先选择场景和主角');
        return;
    }

    const charData = JSON.parse(charSelect.selectedOptions[0].getAttribute('data-assets'));
    const sceneData = JSON.parse(sceneSelect.selectedOptions[0].getAttribute('data-assets'));
    const monsterData = monsterSelect.value ? JSON.parse(monsterSelect.selectedOptions[0].getAttribute('data-assets')) : null;

    stopInteractivePreview();

    const placeholder = document.querySelector('.game-placeholder');
    if (placeholder) placeholder.classList.add('hidden');

    document.getElementById('start-game-btn').style.display = 'none';
    document.getElementById('stop-game-btn').style.display = 'inline-block';

    const config = {
        type: Phaser.AUTO,
        parent: 'game-container',
        width: 960,
        height: 540,
        physics: {
            default: 'arcade',
            arcade: { gravity: { y: 0 }, debug: false }
        },
        scene: {
            preload: function () {
                // 加载场景
                this.load.image('bg', sceneData.imgUrl);

                // 加载主角
                if (charData.animation && charData.animation.exists) {
                    this.load.spritesheet('player', 'http://localhost:8000' + charData.animation.spritesheet_url, {
                        frameWidth: 64, frameHeight: 64
                    });
                } else {
                    this.load.image('player', charData.imgUrl);
                }

                // 加载怪物
                if (monsterData) {
                    if (monsterData.animation && monsterData.animation.exists) {
                        this.load.spritesheet('monster', 'http://localhost:8000' + monsterData.animation.spritesheet_url, {
                            frameWidth: 64, frameHeight: 64
                        });
                    } else {
                        this.load.image('monster', monsterData.imgUrl);
                    }
                }
            },
            create: function () {
                // 1. 设置边界 (缩小到 960x540)
                this.physics.world.setBounds(0, 0, 960, 540);

                // 2. 绘制背景
                const bg = this.add.image(480, 240, 'bg');
                // 保持比例填充
                const scale = Math.max(960 / bg.width, 540 / bg.height);
                bg.setScale(scale).setOrigin(0.5, 0.5).setPosition(480, 270);

                // 3. 辅助函数：创建血条和名称
                this.createUI = (owner, name, color) => {
                    owner.health = 100;
                    owner.maxHealth = 100;
                    owner.nameText = this.add.text(owner.x, owner.y - 60, name, {
                        fontSize: '14px', fill: '#fff', stroke: '#000', strokeThickness: 3
                    }).setOrigin(0.5);
                    owner.hpBarBg = this.add.rectangle(owner.x, owner.y - 45, 50, 5, 0x000000);
                    owner.hpBar = this.add.rectangle(owner.x - 25, owner.y - 45, 50, 5, color).setOrigin(0, 0.5);
                };

                this.updateUI = (owner) => {
                    if (!owner || !owner.active || !owner.nameText) return;
                    owner.nameText.setPosition(owner.x, owner.y - 60);
                    owner.hpBarBg.setPosition(owner.x, owner.y - 45);
                    owner.hpBar.setPosition(owner.x - 25, owner.y - 45);
                    const hpPercent = Math.max(0, owner.health / owner.maxHealth);
                    owner.hpBar.width = 50 * hpPercent;
                };

                // 4. 主角
                this.player = this.physics.add.sprite(200, 270, 'player');
                this.player.setCollideWorldBounds(true);
                this.player.setScale(1.2);
                this.createUI(this.player, charData.name, 0x00ff00);

                // 主角动画 (使用更通用的逻辑检查)
                if (charData.animation && charData.animation.exists) {
                    this.anims.create({ key: 'p_idle', frames: this.anims.generateFrameNumbers('player', { start: 0, end: 3 }), frameRate: 8, repeat: -1 });
                    this.anims.create({ key: 'p_walk', frames: this.anims.generateFrameNumbers('player', { start: 4, end: 7 }), frameRate: 10, repeat: -1 });
                    this.anims.create({ key: 'p_attack', frames: this.anims.generateFrameNumbers('player', { start: 8, end: 11 }), frameRate: 15, repeat: 0 });
                    this.player.play('p_idle');
                }

                // 5. 怪物 (AI)
                if (monsterData) {
                    this.monster = this.physics.add.sprite(700, 270, 'monster');
                    this.monster.setCollideWorldBounds(true);
                    this.monster.setScale(1.2);
                    this.monster.setTint(0xffcccc);
                    this.createUI(this.monster, monsterData.name + " (Monster)", 0xff0000);

                    if (monsterData.animation && monsterData.animation.exists) {
                        this.anims.create({ key: 'm_idle', frames: this.anims.generateFrameNumbers('monster', { start: 0, end: 3 }), frameRate: 8, repeat: -1 });
                        this.anims.create({ key: 'm_walk', frames: this.anims.generateFrameNumbers('monster', { start: 4, end: 7 }), frameRate: 8, repeat: -1 });
                        this.monster.play('m_idle');
                    }
                }

                // 6. 输入与攻击
                this.cursors = this.input.keyboard.createCursorKeys();
                this.keys = this.input.keyboard.addKeys('W,A,S,D,SPACE');

                this.input.keyboard.on('keydown-SPACE', () => {
                    if (this.anims.exists('p_attack')) {
                        if (this.player.anims.currentAnim?.key !== 'p_attack') {
                            this.player.play('p_attack');
                        }
                    }

                    // 攻击碰撞判定
                    if (this.monster && Phaser.Math.Distance.Between(this.player.x, this.player.y, this.monster.x, this.monster.y) < 80) {
                        this.monster.health -= 20;
                        this.monster.setTint(0xffffff);
                        this.time.delayedCall(100, () => this.monster.setTint(0xffcccc));
                        if (this.monster.health <= 0) {
                            this.monster.health = 100;
                            this.monster.setPosition(Phaser.Math.Between(100, 860), Phaser.Math.Between(100, 440));
                        }
                    }
                });

                // 7. 小地图 (右上角)
                this.minimap = this.cameras.add(780, 20, 160, 100).setZoom(0.18).setName('mini');
                this.minimap.setBackgroundColor(0x000000);
                this.minimap.scrollX = 480;
                this.minimap.scrollY = 270;
                this.minimap.ignore([this.player.nameText, this.player.hpBarBg, this.player.hpBar]);
                if (this.monster) this.minimap.ignore([this.monster.nameText, this.monster.hpBarBg, this.monster.hpBar]);

                // 操作提示
                this.add.text(15, 15, 'WASD移动 | 空格攻击', {
                    fontSize: '16px', fill: '#fff', backgroundColor: 'rgba(0,0,0,0.6)', padding: 5
                });
            },
            update: function () {
                // 1. 移动逻辑
                const speed = 250;
                let vx = 0, vy = 0;

                const isAttacking = this.anims.exists('p_attack') && this.player.anims.currentAnim?.key === 'p_attack' && this.player.anims.isPlaying;

                if (!isAttacking) {
                    if (this.cursors.left.isDown || this.keys.A.isDown) vx = -speed;
                    else if (this.cursors.right.isDown || this.keys.D.isDown) vx = speed;
                    if (this.cursors.up.isDown || this.keys.W.isDown) vy = -speed;
                    else if (this.cursors.down.isDown || this.keys.S.isDown) vy = speed;
                }

                this.player.setVelocity(vx, vy);

                // 动画驱动
                if (!isAttacking) {
                    if (vx !== 0 || vy !== 0) {
                        if (this.anims.exists('p_walk') && this.player.anims.currentAnim?.key !== 'p_walk') this.player.play('p_walk');
                        this.player.flipX = vx < 0;
                    } else {
                        if (this.anims.exists('p_idle') && this.player.anims.currentAnim?.key !== 'p_idle') this.player.play('p_idle');
                    }
                }
                this.updateUI(this.player);

                // 2. 怪物移动
                if (this.monster) {
                    const dist = Phaser.Math.Distance.Between(this.player.x, this.player.y, this.monster.x, this.monster.y);
                    if (dist < 300 && dist > 40) {
                        this.physics.moveToObject(this.monster, this.player, 120);
                        if (this.anims.exists('m_walk') && this.monster.anims.currentAnim?.key !== 'm_walk') this.monster.play('m_walk');
                        this.monster.flipX = this.player.x < this.monster.x;
                    } else {
                        this.monster.setVelocity(0);
                        if (this.anims.exists('m_idle') && this.monster.anims.currentAnim?.key !== 'm_idle') this.monster.play('m_idle');

                        if (dist <= 40) {
                            this.player.health -= 0.1;
                            this.player.setTint(0xff0000);
                            this.time.delayedCall(50, () => this.player.clearTint());
                        }
                    }
                    this.updateUI(this.monster);
                }
            }
        }
    };

    phaserGame = new Phaser.Game(config);
}

/**
 * 停止交互式预览
 */
function stopInteractivePreview() {
    if (phaserGame) {
        phaserGame.destroy(true);
        phaserGame = null;
    }
    const placeholder = document.querySelector('.game-placeholder');
    if (placeholder) placeholder.classList.remove('hidden');

    const startBtn = document.getElementById('start-game-btn');
    const stopBtn = document.getElementById('stop-game-btn');
    if (startBtn) startBtn.style.display = 'inline-block';
    if (stopBtn) stopBtn.style.display = 'none';
}

/**
 * 返回项目页
 */
function backFromResource() {
    document.getElementById('resource-panel').classList.add('hidden');
    document.getElementById('project-panel').classList.remove('hidden');
}

// 导出供全局使用
window.handleDocAction = handleDocAction;
window.generateAllDocuments = generateAllDocuments;
window.extractSpec = extractSpec;
window.extractAllSpecs = extractAllSpecs;
window.viewSpec = viewSpec;
window.generateResources = generateResources;
window.runResourceScripts = runResourceScripts;
window.showResourcePanel = showResourcePanel;
window.generateItemVariants = generateItemVariants;
window.viewItemVariants = viewItemVariants;
window.selectVariant = selectVariant;
window.backFromResource = backFromResource;
window.startGame = startGame;
window.stopGame = stopGame;
window.deleteProject = deleteProject;
window.clearTempDirectory = clearTempDirectory;
window.clearItemTempDirectory = clearItemTempDirectory;
window.generateCharacterAnimations = generateCharacterAnimations;
window.showPreviewPanel = showPreviewPanel;
window.backToProject = backToProject;
window.startInteractivePreview = startInteractivePreview;
window.stopInteractivePreview = stopInteractivePreview;

