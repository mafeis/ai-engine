/**
 * AI 游戏引擎 - 前端主入口 (模块化版本)
 */

import { api } from './js/api.js';
import { state } from './js/state.js';
import { initMarkdown, renderMarkdown } from './js/utils.js';
import { renderProjectList, selectProject, deleteProject } from './js/projects.js';
import {
    viewDocument,
    handleDocAction,
    generateAllDocuments,
    generateSingleDocument,
    extractSpec,
    extractAllSpecs,
    viewSpec,
    extractSpecFromDoc
} from './js/documents.js';
import {
    showResourcePanel,
    generateItemVariants,
    viewItemVariants,
    selectVariant,
    generateCharacterAnimations,
    clearItemTempDirectory,
    clearTempDirectory
} from './js/resources.js';
import { showPreviewPanel, startInteractivePreview, stopInteractivePreview } from './js/game.js';
import { backToProject, backToProjectList, backFromResource, showPanel } from './js/ui.js';

// ============ 全局初始化 ============

async function init() {
    console.log('🚀 AI Engine Frontend Initializing...');

    // 初始化工具
    initMarkdown();

    // 初始加载项目列表
    try {
        const result = await api.getProjects();
        state.projects = result.projects || [];
        renderProjectList();
    } catch (error) {
        console.error('初始化加载项目失败:', error);
    }

    // 绑定基础事件
    setupEventListeners();
}

/**
 * 绑定 UI 事件监听
 */
function setupEventListeners() {
    // 创建项目
    const createProjectDialog = document.getElementById('create-project-dialog');
    const createProjectForm = document.getElementById('create-project-form');

    document.getElementById('create-project-btn').onclick = () => {
        createProjectForm.reset();
        createProjectDialog.showModal();
    };

    createProjectForm.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(createProjectForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const result = await api.createProject(data);
            createProjectDialog.close();

            // 刷新列表并自动选择
            const projectsData = await api.getProjects();
            state.projects = projectsData.projects || [];
            renderProjectList();
            await selectProject(result.id);
        } catch (error) {
            console.error('创建项目失败:', error);
            alert('创建项目失败: ' + error.message);
        }
    };

    // 文档编辑
    document.getElementById('edit-doc-btn').onclick = () => {
        const content = state.currentDocument.content;
        const editor = document.getElementById('document-editor');
        const display = document.getElementById('document-content');

        editor.value = content;
        editor.classList.remove('hidden');
        display.classList.add('hidden');

        document.getElementById('edit-doc-btn').style.display = 'none';
        document.getElementById('save-doc-btn').style.display = 'inline-block';
        state.isEditing = true;
    };

    document.getElementById('save-doc-btn').onclick = async () => {
        const { projectId, docType } = state.currentDocument;
        const newContent = document.getElementById('document-editor').value;

        try {
            await api.saveDocument(projectId, docType, { content: newContent });
            state.currentDocument.content = newContent;

            // 刷新显示
            const display = document.getElementById('document-content');
            display.innerHTML = renderMarkdown(newContent);

            // 退出编辑
            document.getElementById('document-editor').classList.add('hidden');
            display.classList.remove('hidden');
            document.getElementById('edit-doc-btn').style.display = 'inline-block';
            document.getElementById('save-doc-btn').style.display = 'none';
            state.isEditing = false;
        } catch (error) {
            console.error('保存文档失败:', error);
            alert('保存失败: ' + error.message);
        }
    };
}

// ============ 导出到 window (兼容 HTML 中的 onclick) ============

window.selectProject = selectProject;
window.deleteProject = deleteProject;
window.backToProjectList = backToProjectList;
window.backToProject = backToProject;
window.backFromResource = backFromResource;

window.handleDocAction = handleDocAction;
window.viewDocument = viewDocument;
window.generateSingleDocument = generateSingleDocument;
window.generateAllDocuments = generateAllDocuments;

window.extractSpec = extractSpec;
window.extractAllSpecs = extractAllSpecs;
window.viewSpec = viewSpec;
window.extractSpecFromDoc = extractSpecFromDoc;

window.showResourcePanel = showResourcePanel;
window.generateItemVariants = generateItemVariants;
window.viewItemVariants = viewItemVariants;
window.selectVariant = selectVariant;
window.generateCharacterAnimations = generateCharacterAnimations;
window.clearItemTempDirectory = clearItemTempDirectory;
window.clearTempDirectory = clearTempDirectory;

window.showPreviewPanel = showPreviewPanel;
window.startGame = startInteractivePreview; // 保持 HTML 里的名字
window.stopGame = stopInteractivePreview;

// 执行初始化
init();
