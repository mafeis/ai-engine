/**
 * 资源创作与变体管理逻辑
 */

import { api } from './api.js';
import { state } from './state.js';
import { getAssetUrl } from './utils.js';

/**
 * 显示资源面板
 */
export async function showResourcePanel(projectId, specType) {
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

        // 保存当前状态
        state.currentSpecType = specType;

        // 渲染条目列表
        const listContainer = document.getElementById('resource-items-list');
        listContainer.innerHTML = `
            <div class="row items-center justify-between mb-4">
                <h3>${titles[specType] || '资源'}列表</h3>
                <button class="btn btn-danger btn-sm" id="clear-all-cache-btn">
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
                            <button class="btn btn-primary btn-sm gen-variants-btn" data-id="${item.id}">
                                🎨 智能生成 (1+3风格)
                            </button>
                            <button class="btn btn-secondary btn-sm regen-variants-btn" data-id="${item.id}">
                                🔄 重新AI设计并生成
                            </button>
                            <button class="btn btn-secondary btn-sm view-variants-btn" data-id="${item.id}">
                                📂 查看/更新
                            </button>
                            <button class="btn btn-outline-danger btn-sm clear-item-btn" data-id="${item.id}" title="清理缓存">
                                🗑️
                            </button>
                        </div>
                        <div class="variants-container" id="variants-${item.id}">
                            <!-- 变体列表将在此处渲染 -->
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        // 绑定事件
        document.getElementById('clear-all-cache-btn').onclick = () => clearTempDirectory(projectId);

        listContainer.querySelectorAll('.gen-variants-btn').forEach(btn => {
            btn.onclick = () => generateItemVariants(projectId, specType, btn.dataset.id);
        });
        listContainer.querySelectorAll('.regen-variants-btn').forEach(btn => {
            btn.onclick = () => generateItemVariants(projectId, specType, btn.dataset.id, true);
        });
        listContainer.querySelectorAll('.view-variants-btn').forEach(btn => {
            btn.onclick = () => viewItemVariants(projectId, specType, btn.dataset.id);
        });
        listContainer.querySelectorAll('.clear-item-btn').forEach(btn => {
            btn.onclick = () => clearItemTempDirectory(projectId, specType, btn.dataset.id);
        });

        // 自动加载所有变体/选定状态
        items.forEach(item => {
            viewItemVariants(projectId, specType, item.id);
        });

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
export async function generateItemVariants(projectId, specType, itemId, forceRegen = false) {
    const btn = event?.target.closest('button');
    const originalText = btn ? btn.textContent : '';

    if (btn) {
        btn.textContent = forceRegen ? 'AI 重新设计中...' : '资源创作中...';
        btn.disabled = true;
    }

    try {
        const result = await api.generateResourceScript(projectId, specType, itemId, {
            force_regenerate_script: forceRegen
        });

        // 渲染变体
        const container = document.getElementById(`variants-${itemId}`);
        if (container) {
            container.innerHTML = renderVariantsHtml(result, projectId, specType, itemId);
        }

        alert(`✓ 成功创作 ${result.variants.length} 组资源方案`);

    } catch (error) {
        console.error('生成变体失败:', error);
        alert('生成失败: ' + error.message);
    } finally {
        if (btn) {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
}

/**
 * 查看条目的变体列表
 */
export async function viewItemVariants(projectId, specType, itemId) {
    try {
        const resourceType = specType === 'audio' ? 'sfx' : specType;
        const result = await api.getResourceVariants(projectId, resourceType, itemId);

        const container = document.getElementById(`variants-${itemId}`);
        if (!container) return;

        if (result.variants && result.variants.length > 0) {
            container.innerHTML = renderVariantsHtml(result, projectId, specType, itemId);
        } else {
            container.innerHTML = '<p class="muted">暂无方案，点击“智能生成”开始创作</p>';
        }

    } catch (error) {
        console.error('获取变体失败:', error);
    }
}

/**
 * 渲染变体HTML
 */
export function renderVariantsHtml(result, projectId, specType, itemId) {
    const variants = result.variants || [];
    const animation = result.animation;
    const selectedVariant = variants.find(v => v.selected);

    // 如果已经选择了某个版本，展示精简的“已选定”视图
    if (selectedVariant) {
        const imgUrl = getAssetUrl(projectId, specType + 's', itemId, selectedVariant.file_path);
        const badgeText = selectedVariant.is_final ? '✓ 资产库正式版本' : '✓ 候选已选定';

        // 创建 HTML
        const wrapper = document.createElement('div');
        wrapper.className = 'selected-resource-view';

        let html = `
            <div class="selected-main-card mb-3">
                <div class="selected-badge">${badgeText}</div>
                <div class="selected-preview"><img src="${imgUrl}" alt="已选定方案"></div>
                <div class="selected-actions">
                    <button class="btn btn-outline-secondary btn-sm regen-trigger">🔄 重新生成</button>
        `;

        if (specType === 'character') {
            html += `
                <button class="btn btn-warning btn-sm anim-trigger">🎬 ${animation?.exists ? '重新生成动画' : '生成动画序列'}</button>
                <button class="btn btn-outline-primary btn-sm upload-trigger">📤 上传并替换</button>
                <input type="file" class="anim-upload-input" style="display:none" accept="image/png">
            `;
        }

        html += `</div></div>`;

        if (specType === 'character' && animation?.exists) {
            const types = [
                { id: 'idle', n: '待机', r: 0 },
                { id: 'walk', n: '行走', r: 1 },
                { id: 'attack', n: '攻击', r: 2 }
            ];

            html += `
                <div class="animation-preview-panel mt-3">
                    <h4 class="mb-3">🏃 动画组件管理</h4>
                    <p class="muted small mb-3">你可以分别为每个动作上传独立的 4 帧（1x4）序列帧图片，或使用 AI 生成的完整图。</p>
                    <div class="animation-grid">
                        ${types.map(a => {
                const customData = animation.types?.[a.id];
                const isCustom = !!customData;
                const frames = isCustom ? customData.frames : 4;
                const frameSize = isCustom ? (customData.frameSize || 64) : 64;
                const sheetUrl = (isCustom ? ('http://localhost:8000' + customData.url) : ('http://localhost:8000' + animation.spritesheet_url)) + `?t=${Date.now()}`;

                // 动态调整动画样式
                const spriteWidth = frames * frameSize;
                const scale = 64 / frameSize;
                const animationStyle = frames > 1
                    ? `playSprite 0.8s steps(${frames}) infinite`
                    : 'none';

                return `
                                <div class="anim-preview-item">
                                    <div class="anim-sprite-box" style="width:64px; height:64px; overflow:hidden; border:2px solid ${isCustom ? 'var(--primary)' : 'var(--border)'}; background:rgba(255,255,255,0.05); border-radius:4px; margin:0 auto 8px; position:relative;">
                                        <div class="anim-sprite" style="
                                            width:${spriteWidth}px; 
                                            height:${frameSize}px; 
                                            background-image: url('${sheetUrl}'); 
                                            background-position: 0 -${isCustom ? 0 : (a.r * frameSize)}px; 
                                            animation: ${animationStyle};
                                            transform: scale(${scale});
                                            transform-origin: 0 0;
                                        "></div>
                                        ${isCustom ? `<span style="position:absolute; top:0; right:0; font-size:10px; background:var(--primary); color:white; padding:1px 3px;">${frames}帧|${frameSize}px</span>` : ''}
                                    </div>
                                    <div class="anim-name-small">${a.n}</div>
                                    <div class="mt-2 text-center">
                                        <button class="btn btn-outline-primary btn-xs upload-type-trigger" data-type="${a.id}" title="上传 ${a.n} 序列帧 (支持任意分辨率)">
                                            上传
                                        </button>
                                        <input type="file" class="anim-type-upload-input" data-type="${a.id}" style="display:none" accept="image/png">
                                    </div>
                                </div>
                            `;
            }).join('')}
                    </div>
                </div>
            `;
        }

        // 注入并绑定事件 (因为字符串模板无法直接绑定函数)
        setTimeout(() => {
            const container = document.getElementById(`variants-${itemId}`);
            if (container) {
                const regenBtn = container.querySelector('.regen-trigger');
                if (regenBtn) regenBtn.onclick = () => generateItemVariants(projectId, specType, itemId);

                const animBtn = container.querySelector('.anim-trigger');
                if (animBtn) animBtn.onclick = () => generateCharacterAnimations(projectId, itemId);

                const uploadBtn = container.querySelector('.upload-trigger');
                const uploadInput = container.querySelector('.anim-upload-input');
                if (uploadBtn && uploadInput) {
                    uploadBtn.onclick = () => uploadInput.click();
                    uploadInput.onchange = (e) => {
                        const file = e.target.files[0];
                        if (file) uploadCharacterAnimations(projectId, itemId, file, 'full');
                    };
                }

                // 绑定独立动作上传
                container.querySelectorAll('.upload-type-trigger').forEach(subBtn => {
                    const atype = subBtn.dataset.type;
                    const subInput = container.querySelector(`.anim-type-upload-input[data-type="${atype}"]`);
                    if (subInput) {
                        subBtn.onclick = () => subInput.click();
                        subInput.onchange = (e) => {
                            const file = e.target.files[0];
                            if (file) uploadCharacterAnimations(projectId, itemId, file, atype);
                        };
                    }
                });
            }
        }, 0);

        return html;
    }

    // 否则显示变体网格
    let gridHtml = '<div class="variants-grid">';
    variants.forEach((v, idx) => {
        const imgUrl = getAssetUrl(projectId, specType + 's', itemId, v.file_path);
        let previewHtml = v.error ? `<span class="no-preview error">生成失败</span>`
            : (v.exists ? `<img src="${imgUrl}" alt="方案${idx + 1}">` : `<span class="no-preview">生成中...</span>`);

        gridHtml += `
            <div class="variant-card">
                <div class="variant-preview">${previewHtml}</div>
                <div class="variant-info">
                    <span class="variant-name">方案 ${idx + 1}</span>
                    <span class="variant-seed">种子: ${v.seed || idx + 1}</span>
                </div>
                <button class="btn btn-sm btn-primary w-full select-version-btn" data-variant="${v.variant_id}">选择此方案</button>
            </div>
        `;
    });
    gridHtml += '</div>';

    // 绑定选择事件
    setTimeout(() => {
        const container = document.getElementById(`variants-${itemId}`);
        if (container) {
            container.querySelectorAll('.select-version-btn').forEach(btn => {
                btn.onclick = () => selectVariant(projectId, specType, itemId, btn.dataset.variant);
            });
        }
    }, 0);

    return gridHtml;
}

/**
 * 选择变体
 */
export async function selectVariant(projectId, specType, itemId, variantId) {
    try {
        const resourceType = specType === 'audio' ? 'sfx' : specType;
        await api.selectVariant(projectId, resourceType, itemId, variantId);
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
export async function generateCharacterAnimations(projectId, itemId) {
    const btn = event?.target;
    const originalText = btn ? btn.textContent : '';

    if (btn) {
        btn.textContent = '动画设计中...';
        btn.disabled = true;
    }

    try {
        const card = document.getElementById(`card-${itemId}`);
        const desc = card ? card.querySelector('.resource-item-desc').textContent.trim() : '游戏角色';
        const result = await api.generateAnimations(projectId, itemId, desc);
        if (result.success) {
            alert('✓ 序列帧动画设计完成！');
            await viewItemVariants(projectId, 'character', itemId);
        }
    } catch (error) {
        console.error('动画生成失败:', error);
        alert('动画创作失败: ' + error.message);
    } finally {
        if (btn) {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
}

/**
 * 上传角色序列帧动画
 */
export async function uploadCharacterAnimations(projectId, itemId, file, animType = 'full') {
    try {
        const result = await api.uploadAnimations(projectId, itemId, file, animType);
        if (result.success) {
            alert(`✓ ${animType === 'full' ? '完整' : animType} 序列帧动画上传成功！`);
            await viewItemVariants(projectId, 'character', itemId);
        }
    } catch (error) {
        console.error('动画上传失败:', error);
        alert('动画上传失败: ' + error.message);
    }
}

/**
 * 清理单个条目的缓存
 */
export async function clearItemTempDirectory(projectId, specType, itemId) {
    if (!confirm('确定要清理该条目的生成缓存吗？')) return;
    try {
        const result = await api.clearItemTemp(projectId, specType, itemId);
        if (result.success) {
            const container = document.getElementById(`variants-${itemId}`);
            if (container) container.innerHTML = '<p class="muted">缓存已清理</p>';
            alert('✓ 清理成功');
        }
    } catch (error) {
        alert('清理失败: ' + error.message);
    }
}

/**
 * 清理所有临时目录
 */
export async function clearTempDirectory(projectId) {
    if (!confirm('确定要清理所有资源缓存吗？')) return;
    try {
        const response = await fetch(`http://localhost:8000/api/resources/${projectId}/temp`, { method: 'DELETE' });
        const result = await response.json();
        if (result.success) {
            document.querySelectorAll('.variants-container').forEach(el => el.innerHTML = '<p class="muted">已清理缓存</p>');
            alert('清理成功！所有缓存已删除。');
        }
    } catch (error) {
        alert('清理失败: ' + error.message);
    }
}
