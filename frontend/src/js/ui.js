/**
 * UI 交互与面板切换逻辑
 */

import { state } from './state.js';
import { stopInteractivePreview } from './game.js';

/**
 * 切换到主面板中的某个子面板
 */
export function showPanel(panelId) {
    document.querySelectorAll('.panel').forEach(p => p.classList.add('hidden'));
    const panel = document.getElementById(panelId);
    if (panel) panel.classList.remove('hidden');
}

/**
 * 返回项目详情页
 */
export function backToProject() {
    const panels = ['document-panel', 'spec-panel', 'resource-panel', 'preview-panel'];
    panels.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    });

    const projectPanel = document.getElementById('project-panel');
    if (projectPanel) projectPanel.classList.remove('hidden');

    // 停止运行中的游戏
    stopInteractivePreview();
}

/**
 * 从规格面板返回
 */
export function backFromSpec() {
    const specPanel = document.getElementById('spec-panel');
    const projectPanel = document.getElementById('project-panel');
    if (specPanel) specPanel.classList.add('hidden');
    if (projectPanel) projectPanel.classList.remove('hidden');
}

/**
 * 返回项目列表页
 */
export function backToProjectList() {
    const projectPanel = document.getElementById('project-panel');
    const welcomePanel = document.getElementById('welcome-panel');

    if (projectPanel) projectPanel.classList.add('hidden');
    if (welcomePanel) welcomePanel.classList.remove('hidden');

    // 清除当前选择
    state.currentProject = null;
    const items = document.querySelectorAll('.project-item');
    items.forEach(item => item.classList.remove('active'));
}

/**
 * 切换资源面板返回
 */
export function backFromResource() {
    const resourcePanel = document.getElementById('resource-panel');
    const projectPanel = document.getElementById('project-panel');
    if (resourcePanel) resourcePanel.classList.add('hidden');
    if (projectPanel) projectPanel.classList.remove('hidden');
}

/**
 * 切换项目面板内的 Tab
 */
export function switchTab(tabName) {
    const projectPanel = document.getElementById('project-panel');
    if (!projectPanel) return;

    const tabs = projectPanel.querySelectorAll('.tab-item');
    const panes = projectPanel.querySelectorAll('.tab-pane');

    tabs.forEach(t => t.classList.remove('active'));
    panes.forEach(p => p.classList.remove('active'));

    const activeTab = projectPanel.querySelector(`.tab-item[data-tab="${tabName}"]`);
    const activePane = projectPanel.querySelector(`#tab-${tabName}`);

    if (activeTab) activeTab.classList.add('active');
    if (activePane) activePane.classList.add('active');
}

/**
 * 快捷显示预览面板（切换项目内部 Tab 并初始化）
 */
export function showPreviewPanel(projectId) {
    switchTab('preview');
    // 如果需要初始化预览内容 (initPreviewTab 在 main.js 中被挂载到 window)
    if (window.initPreviewTab) {
        window.initPreviewTab(projectId);
    }
}
