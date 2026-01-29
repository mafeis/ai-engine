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
    document.getElementById(panelId).classList.remove('hidden');
}

/**
 * 返回项目详情页
 */
export function backToProject() {
    const projectPanel = document.getElementById('project-panel');
    const documentPanel = document.getElementById('document-panel');
    const previewPanel = document.getElementById('preview-panel');

    documentPanel.classList.add('hidden');
    previewPanel.classList.add('hidden');
    projectPanel.classList.remove('hidden');

    // 停止运行中的游戏
    stopInteractivePreview();
}

/**
 * 返回项目列表页
 */
export function backToProjectList() {
    document.getElementById('project-panel').classList.add('hidden');
    document.getElementById('welcome-panel').classList.remove('hidden');

    // 清除当前选择
    state.currentProject = null;
    const items = document.querySelectorAll('.project-item');
    items.forEach(item => item.classList.remove('active'));
}

/**
 * 切换资源面板返回
 */
export function backFromResource() {
    document.getElementById('resource-panel').classList.add('hidden');
    document.getElementById('project-panel').classList.remove('hidden');
}
