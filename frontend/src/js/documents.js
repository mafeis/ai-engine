/**
 * 文档与规格处理组件
 */

import { api } from './api.js';
import { state } from './state.js';
import { getStatusText, renderMarkdown } from './utils.js';

/**
 * 渲染项目详情面板（含文档列表）
 */
export async function renderProjectPanel(project) {
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
                    <span class="icon">🖥️</span>
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
                    <span class="icon">🕹️</span>
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
export function getDocIcon(docType) {
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
export async function handleDocAction(projectId, docType, exists) {
    if (exists) {
        await viewDocument(projectId, docType);
    } else {
        await generateSingleDocument(projectId, docType);
    }
}

/**
 * 查看文档
 */
export async function viewDocument(projectId, docType) {
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
export async function generateSingleDocument(projectId, docType) {
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
 * 生成全部文档
 */
export async function generateAllDocuments(projectId) {
    if (!confirm('确定要为该项目生成所有文档吗？这可能需要几分钟。')) {
        return;
    }

    const btn = event.target;
    btn.textContent = '生成中...';
    btn.disabled = true;

    try {
        await api.generateDocument(projectId, 'all');
        alert('文档生成任务已启动，请稍后刷新。');
        await renderProjectPanel(state.currentProject);
    } catch (error) {
        console.error('生成文档失败:', error);
        alert('生成文档失败: ' + error.message);
    } finally {
        btn.textContent = '🔄 生成全部';
        btn.disabled = false;
    }
}

/**
 * 提取规格
 */
export async function extractSpec(projectId, docType) {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = '提取中...';
    btn.disabled = true;

    try {
        await api.extractSpec(projectId, docType);
        await renderProjectPanel(state.currentProject);
    } catch (error) {
        console.error('提取规格失败:', error);
        alert('提取规格失败: ' + error.message);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

/**
 * 查看JSON规格内容
 */
export async function viewSpec(projectId, specType) {
    try {
        const spec = await api.getSpec(projectId, specType);
        const specJson = JSON.stringify(spec, null, 2);

        // 使用对话框展示
        const dialog = document.createElement('dialog');
        dialog.className = 'dialog spec-dialog';
        dialog.innerHTML = `
            <h2>${specType} 规格预览</h2>
            <pre><code class="language-json">${specJson}</code></pre>
            <div class="dialog-actions">
                <button class="btn btn-primary" onclick="this.closest('dialog').close(); this.closest('dialog').remove();">关闭</button>
            </div>
        `;
        document.body.appendChild(dialog);
        dialog.showModal();

        // 高亮
        if (typeof hljs !== 'undefined') {
            hljs.highlightElement(dialog.querySelector('code'));
        }
    } catch (error) {
        console.error('查看规格失败:', error);
        alert('查看规格失败: ' + error.message);
    }
}

/**
 * 提取全部规格
 */
export async function extractAllSpecs(projectId) {
    const btn = event.target;
    btn.textContent = '提取中...';
    btn.disabled = true;

    try {
        await api.extractSpec(projectId, 'all');
        await renderProjectPanel(state.currentProject);
    } catch (error) {
        console.error('提取规格失败:', error);
        alert('提取规格失败: ' + error.message);
    } finally {
        btn.textContent = '📊 提取全部';
        btn.disabled = false;
    }
}

/**
 * 从文档编辑页直接提取规格
 */
export async function extractSpecFromDoc(projectId, docType) {
    try {
        await api.extractSpec(projectId, docType);
        alert('规格提取成功');
    } catch (error) {
        console.error('提取规格失败:', error);
        alert('提取规格失败: ' + error.message);
    }
}
