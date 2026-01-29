/**
 * 项目管理组件
 */

import { api } from './api.js';
import { state } from './state.js';
import { getStatusText } from './utils.js';
import { renderProjectPanel } from './documents.js'; // 我们在 documents.js 中处理面板渲染

/**
 * 渲染项目列表
 */
export function renderProjectList() {
    const container = document.getElementById('project-list');
    if (!container) return;

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
 * 选择项目
 */
export async function selectProject(projectId) {
    try {
        const project = await api.getProject(projectId);
        state.currentProject = project;

        // 更新列表高亮
        document.querySelectorAll('.project-item').forEach(item => {
            item.classList.toggle('active', item.dataset.id === projectId);
        });

        // 显示项目详情 (在 documents.js 中实现)
        await renderProjectPanel(project);
    } catch (error) {
        console.error('获取项目失败:', error);
    }
}

/**
 * 删除项目
 */
export async function deleteProject(projectId) {
    if (!confirm('确定要删除这个项目吗？这将清除所有相关的文档和资源。')) {
        return;
    }

    try {
        await api.deleteProject(projectId);

        // 返回欢迎页
        document.getElementById('project-panel').classList.add('hidden');
        document.getElementById('welcome-panel').classList.remove('hidden');

        // 刷新列表
        const resultList = await api.getProjects();
        state.projects = resultList.projects || [];
        renderProjectList();

        alert('项目已删除');
    } catch (error) {
        console.error('删除项目失败:', error);
        alert('删除项目失败: ' + error.message);
    }
}
