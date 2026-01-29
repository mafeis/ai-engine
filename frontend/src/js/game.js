/**
 * Phaser 3 游戏预览引擎
 */

import { api } from './api.js';
import { phaserGame, setPhaserGame } from './state.js';
import { getAssetUrl } from './utils.js';

/**
 * 启动交互式预览面板
 */
/**
 * 初始化预览 Tab 的控件
 */
export async function initPreviewTab(projectId) {
    try {
        const charSelect = document.getElementById('preview-character-select');
        const monsterSelect = document.getElementById('preview-monster-select');
        const sceneSelect = document.getElementById('preview-scene-select');

        // 健壮性检查：如果 DOM 还没准备好，先退出
        if (!charSelect || !monsterSelect || !sceneSelect) {
            console.warn('预览面板 DOM 尚未加载完成，取消初始化');
            return;
        }

        // 清除“加载中”状态 (即便后续可能返回)
        const clearLoading = (el, text) => {
            if (el.options.length > 0 && el.options[0].text === '加载中...') {
                el.innerHTML = `<option value="">${text}</option>`;
            }
        };
        clearLoading(charSelect, '选择主角...');
        clearLoading(monsterSelect, '选择怪物 (可选)...');
        clearLoading(sceneSelect, '选择场景...');

        // 如果已经填充了真实数据，则不再重复请求（除非需要刷新）
        if (charSelect.options.length > 1) {
            // 已有数据，跳过初始化
            return;
        }

        // 1. 获取规格
        const charSpec = await api.getSpec(projectId, 'character').catch(() => ({ characters: [] }));
        const sceneSpec = await api.getSpec(projectId, 'scene').catch(() => ({ scenes: [] }));

        // 统一处理数据结构：有些返回 {spec: {...}} 有些直接返回 {...}
        const characters = (charSpec.spec?.characters || charSpec.characters || []).filter(c => c && c.id);
        const scenes = (sceneSpec.spec?.scenes || sceneSpec.scenes || []).filter(s => s && s.id);

        if (characters.length === 0 && scenes.length === 0) {
            const desc = document.querySelector('#tab-preview .section-desc');
            if (desc) desc.innerHTML = '<span style="color:var(--warning)">⚠️ 请先生成设计文档（角色和场景），才能开始准备预览资源。</span>';
            return;
        }

        // 2. 检查哪些有资源 (已选定)
        const readyCharacters = [];
        const readyScenes = [];

        // 并行请求资源状态以提升速度
        const charPromises = characters.map(async (char) => {
            try {
                const result = await api.getResourceVariants(projectId, 'character', char.id);
                const selected = result.variants?.find(v => v.selected);
                if (selected) {
                    return {
                        id: char.id,
                        name: char.name,
                        imgUrl: getAssetUrl(projectId, 'characters', char.id, selected.file_path),
                        animation: result.animation
                    };
                }
            } catch (e) { }
            return null;
        });

        const scenePromises = scenes.map(async (scene) => {
            try {
                const result = await api.getResourceVariants(projectId, 'scene', scene.id);
                const selected = result.variants?.find(v => v.selected);
                if (selected) {
                    return {
                        id: scene.id,
                        name: scene.name,
                        imgUrl: getAssetUrl(projectId, 'scenes', scene.id, selected.file_path)
                    };
                }
            } catch (e) { }
            return null;
        });

        const charResults = await Promise.all(charPromises);
        readyCharacters.push(...charResults.filter(Boolean));

        const sceneResults = await Promise.all(scenePromises);
        readyScenes.push(...sceneResults.filter(Boolean));

        // 填充下拉框
        const fillSelect = (el, items, defaultText, emptyText) => {
            let html = `<option value="">${items.length > 0 ? defaultText : emptyText}</option>`;
            html += items.map(c => `<option value="${c.id}" data-assets='${JSON.stringify(c).replace(/'/g, "&apos;")}'>${c.name}</option>`).join('');
            el.innerHTML = html;
        };

        fillSelect(charSelect, readyCharacters, '选择主角...', '暂无选定角色 (请去资源管理选定)');
        fillSelect(monsterSelect, readyCharacters, '选择怪物 (可选/复用角色)...', '暂无选定怪物');
        fillSelect(sceneSelect, readyScenes, '选择场景...', '暂无选定场景 (请去资源管理选定)');

        // 检查是否有足够资源启动预览
        const desc = document.querySelector('#tab-preview .section-desc');
        if (readyCharacters.length === 0 || readyScenes.length === 0) {
            if (desc) {
                desc.innerHTML = '<span style="color:var(--danger)">⚠️ 无法启动预览：需至少有一个<b>已选定</b>的场景和一个角色。</span>';
            }
        } else {
            if (desc) {
                desc.innerHTML = '在选定的场景中控制角色移动，体验游戏的雏形。';
            }
        }

        // 5. 绑定按钮与实时切换事件
        const startBtn = document.getElementById('start-game-btn');
        if (startBtn) startBtn.onclick = () => startInteractivePreview(projectId);

        const stopBtn = document.getElementById('stop-game-btn');
        if (stopBtn) stopBtn.onclick = stopInteractivePreview;

        const syncRefresh = () => {
            if (phaserGame && sceneSelect.value && charSelect.value) {
                startInteractivePreview(projectId);
            }
        };
        sceneSelect.onchange = syncRefresh;
        charSelect.onchange = syncRefresh;
        monsterSelect.onchange = syncRefresh;

        stopInteractivePreview();

    } catch (error) {
        console.error('加载预览面板失败:', error);
        const desc = document.querySelector('#tab-preview .section-desc');
        if (desc) desc.innerHTML = `<span style="color:var(--danger)">❌ 加载预览失败: ${error.message}</span>`;
    }
}

/**
 * 核心游戏逻辑
 */
export function startInteractivePreview(projectId) {
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
                this.load.image('bg', sceneData.imgUrl);

                // 加载玩家资源
                if (charData.animation?.exists) {
                    const anims = charData.animation;
                    const baseUrl = 'http://localhost:8000';

                    // 检查是否有分段动画
                    const timestamp = `?t=${Date.now()}`;
                    if (anims.types && (anims.types.idle || anims.types.walk || anims.types.attack)) {
                        ["idle", "walk", "attack"].forEach(type => {
                            const custom = anims.types[type];
                            if (custom) {
                                const fSize = custom.frameSize || 64;
                                this.load.spritesheet(`p_sheet_${type}`, baseUrl + custom.url + timestamp, {
                                    frameWidth: fSize,
                                    frameHeight: fSize
                                });
                            }
                        });
                        // 兜底主图
                        this.load.spritesheet('player', baseUrl + anims.spritesheet_url + timestamp, { frameWidth: 64, frameHeight: 64 });
                    } else {
                        // 只有原有的整体图
                        this.load.spritesheet('player', baseUrl + anims.spritesheet_url + timestamp, { frameWidth: 64, frameHeight: 64 });
                    }
                } else {
                    this.load.image('player', charData.imgUrl + `?t=${Date.now()}`);
                }

                if (monsterData) {
                    if (monsterData.animation?.exists) {
                        const mAnims = monsterData.animation;
                        const baseUrl = 'http://localhost:8000';
                        if (mAnims.types && (mAnims.types.idle || mAnims.types.walk)) {
                            const mTimestamp = `?t=${Date.now()}`;
                            ["idle", "walk"].forEach(type => {
                                const custom = mAnims.types[type];
                                if (custom) {
                                    const fSize = custom.frameSize || 64;
                                    this.load.spritesheet(`m_sheet_${type}`, baseUrl + custom.url + mTimestamp, {
                                        frameWidth: fSize,
                                        frameHeight: fSize
                                    });
                                }
                            });
                            this.load.spritesheet('monster', baseUrl + mAnims.spritesheet_url + mTimestamp, { frameWidth: 64, frameHeight: 64 });
                        } else {
                            this.load.spritesheet('monster', baseUrl + mAnims.spritesheet_url + `?t=${Date.now()}`, { frameWidth: 64, frameHeight: 64 });
                        }
                    } else {
                        this.load.image('monster', monsterData.imgUrl + `?t=${Date.now()}`);
                    }
                }
            },
            create: function () {
                this.physics.world.setBounds(0, 0, 960, 540);
                const bg = this.add.image(480, 270, 'bg');
                const scale = Math.max(960 / bg.width, 540 / bg.height);
                bg.setScale(scale).setDepth(-10); // 确保背景在地板下

                this.createUI = (owner, name, color) => {
                    owner.health = 100;
                    owner.maxHealth = 100;

                    // 动态计算头顶位置：底部坐标 - (显示高度 * 重心比例)
                    const topY = owner.y - (owner.displayHeight * owner.originY);

                    owner.nameText = this.add.text(owner.x, topY - 25, name, {
                        fontSize: '14px', fill: '#fff', stroke: '#000', strokeThickness: 3
                    }).setOrigin(0.5);
                    owner.hpBarBg = this.add.rectangle(owner.x, topY - 10, 50, 5, 0x000000);
                    owner.hpBar = this.add.rectangle(owner.x - 25, topY - 10, 50, 5, color).setOrigin(0, 0.5);
                };

                this.updateUI = (owner) => {
                    if (!owner || !owner.active || !owner.nameText) return;
                    const topY = owner.y - (owner.displayHeight * owner.originY);

                    owner.nameText.setPosition(owner.x, topY - 25);
                    owner.hpBarBg.setPosition(owner.x, topY - 10);
                    owner.hpBar.setPosition(owner.x - 25, topY - 10);
                    const hpPercent = Math.max(0, owner.health / owner.maxHealth);
                    owner.hpBar.width = 50 * hpPercent;
                };

                this.player = this.physics.add.sprite(200, 270, 'player');
                this.player.setCollideWorldBounds(true);
                this.player.setDepth(2); // 玩家在中间层

                // --- 智能内容缩放 (Smart Zoom) ---
                const idleInfo = charData.animation?.types?.idle;
                const pFrameSize = (idleInfo?.frameSize || 64);
                let pScale = (64 / pFrameSize) * 1.2;

                if (idleInfo?.content_bbox) {
                    const [left, top, right, bottom] = idleInfo.content_bbox;
                    const contentH = bottom - top;
                    const fillRatio = contentH / pFrameSize;

                    // 如果内容占比小于 80%，则进行智能放大补偿，让主体更突出
                    if (fillRatio < 0.8 && fillRatio > 0.1) {
                        pScale *= (0.85 / fillRatio);
                    }
                }
                this.player.setScale(pScale);
                this.player.setOrigin(0.5, 0.8); // 修正重心，适合大部分人形角色

                this.createUI(this.player, charData.name, 0x00ff00);

                if (charData.animation?.exists) {
                    const hasIdle = this.textures.exists('p_sheet_idle');
                    const hasWalk = this.textures.exists('p_sheet_walk');
                    const hasAttack = this.textures.exists('p_sheet_attack');

                    // 获取各自的帧数
                    const fIdle = (charData.animation.types?.idle?.frames || 4);
                    const fWalk = (charData.animation.types?.walk?.frames || 4);
                    const fAttack = (charData.animation.types?.attack?.frames || 4);

                    this.anims.create({
                        key: 'p_idle',
                        frames: hasIdle
                            ? this.anims.generateFrameNumbers('p_sheet_idle', { start: 0, end: fIdle - 1 })
                            : this.anims.generateFrameNumbers('player', { start: 0, end: 3 }),
                        frameRate: 8, repeat: -1
                    });
                    this.anims.create({
                        key: 'p_walk',
                        frames: hasWalk
                            ? this.anims.generateFrameNumbers('p_sheet_walk', { start: 0, end: fWalk - 1 })
                            : this.anims.generateFrameNumbers('player', { start: 4, end: 7 }),
                        frameRate: 10, repeat: -1
                    });
                    this.anims.create({
                        key: 'p_attack',
                        frames: hasAttack
                            ? this.anims.generateFrameNumbers('p_sheet_attack', { start: 0, end: fAttack - 1 })
                            : this.anims.generateFrameNumbers('player', { start: 8, end: 11 }),
                        frameRate: 15, repeat: 0
                    });
                    this.player.play('p_idle');
                }

                if (monsterData) {
                    this.monster = this.physics.add.sprite(700, 270, 'monster');
                    this.monster.setCollideWorldBounds(true);

                    const mIdleInfo = monsterData.animation?.types?.idle;
                    const mFrameSize = (mIdleInfo?.frameSize || 64);
                    let mScale = (64 / mFrameSize) * 1.2;

                    if (mIdleInfo?.content_bbox) {
                        const [mL, mT, mR, mB] = mIdleInfo.content_bbox;
                        const mRatio = (mB - mT) / mFrameSize;
                        if (mRatio < 0.8 && mRatio > 0.1) {
                            mScale *= (0.85 / mRatio);
                        }
                    }

                    this.monster.setScale(mScale).setTint(0xffcccc);
                    this.monster.setOrigin(0.5, 0.8);

                    this.createUI(this.monster, monsterData.name + " (Monster)", 0xff0000);

                    if (monsterData.animation?.exists) {
                        const hasMIdle = this.textures.exists('m_sheet_idle');
                        const hasMWalk = this.textures.exists('m_sheet_walk');

                        this.anims.create({
                            key: 'm_idle',
                            frames: hasMIdle ? this.anims.generateFrameNumbers('m_sheet_idle', { start: 0, end: 3 }) : this.anims.generateFrameNumbers('monster', { start: 0, end: 3 }),
                            frameRate: 8, repeat: -1
                        });
                        this.anims.create({
                            key: 'm_walk',
                            frames: hasMWalk ? this.anims.generateFrameNumbers('m_sheet_walk', { start: 0, end: 3 }) : this.anims.generateFrameNumbers('monster', { start: 4, end: 5 }),
                            frameRate: 8, repeat: -1
                        });
                        this.monster.play('m_idle');
                    }
                }

                // 确保点击画布时获得焦点
                this.input.on('pointerdown', () => {
                    if (window.focus) window.focus();
                    if (this.game.canvas.focus) this.game.canvas.focus();
                });

                this.cursors = this.input.keyboard.createCursorKeys();
                this.keys = this.input.keyboard.addKeys({
                    W: Phaser.Input.Keyboard.KeyCodes.W,
                    A: Phaser.Input.Keyboard.KeyCodes.A,
                    S: Phaser.Input.Keyboard.KeyCodes.S,
                    D: Phaser.Input.Keyboard.KeyCodes.D,
                    R: Phaser.Input.Keyboard.KeyCodes.R,
                    SPACE: Phaser.Input.Keyboard.KeyCodes.SPACE
                });

                // --- 实现 R 键华丽大招：分身序列归宗 ---
                const ULTIMATE_COLORS = [0x00ffff, 0xff00ff, 0xffff00, 0x00ff00, 0xff0000, 0xffffff];

                this.input.keyboard.on('keydown-R', () => {
                    if (this.isUltimating) return;
                    if (!this.monster || !this.monster.active) return;

                    this.isUltimating = true;
                    this.player.setTint(0x00ffff).setAlpha(0.6); // 玩家虚化蓄力

                    const cloneCount = 6;

                    // 1. 产生分身并向四周散开
                    for (let i = 0; i < cloneCount; i++) {
                        const angle = (i / cloneCount) * Math.PI * 2;
                        const dist = 120;
                        const ghost = this.add.sprite(this.player.x, this.player.y, this.player.texture.key).setDepth(3);
                        ghost.setFrame(this.player.frame.name).setAlpha(0).setTint(ULTIMATE_COLORS[i]).setScale(this.player.scaleX);

                        // 阶段一：散开
                        this.tweens.add({
                            targets: ghost,
                            alpha: 0.8,
                            x: this.player.x + Math.cos(angle) * dist,
                            y: this.player.y + Math.sin(angle) * dist,
                            duration: 400,
                            ease: 'Back.easeOut',
                            onComplete: () => {
                                // 阶段二：按照间隔序列冲锋
                                this.time.delayedCall(i * 180 + 300, () => {
                                    if (!this.monster.active || !ghost.active) return ghost.destroy();

                                    // 启动流光拖尾
                                    const trailEvent = this.time.addEvent({
                                        delay: 20,
                                        callback: () => {
                                            if (!ghost.active) return;
                                            const t = this.add.sprite(ghost.x, ghost.y, ghost.texture.key).setDepth(2);
                                            t.setFrame(ghost.frame.name).setTint(ghost.tintTopLeft).setAlpha(0.4).setScale(ghost.scaleX);
                                            this.tweens.add({ targets: t, alpha: 0, scale: 0.3, duration: 150, onComplete: () => t.destroy() });
                                        },
                                        loop: true
                                    });

                                    this.tweens.add({
                                        targets: ghost,
                                        x: this.monster.x,
                                        y: this.monster.y,
                                        duration: 180,
                                        ease: 'Cubic.easeIn',
                                        onComplete: () => {
                                            trailEvent.remove();
                                            ghost.destroy();
                                            this.triggerStepImpact(i, cloneCount);
                                        }
                                    });
                                });
                            }
                        });
                    }
                });

                // 大招撞击处理函数
                this.triggerStepImpact = (index, total) => {
                    this.cameras.main.shake(120, 0.008);
                    this.monster.setTint(0xffffff);
                    this.time.delayedCall(80, () => this.monster.setTint(0xffcccc));

                    if (this.monster && this.monster.active) {
                        const dirX = this.monster.x > this.player.x ? 1 : -1;

                        this.tweens.add({
                            targets: this.monster,
                            x: this.monster.x + 20 * dirX,
                            y: this.monster.y - 12,
                            duration: 80,
                            yoyo: true,
                            ease: 'Back.easeOut'
                        });

                        if (index === total - 1) {
                            this.triggerFinalImpact();
                        }
                    }
                };

                // 大招终结大爆发
                this.triggerFinalImpact = () => {
                    this.cameras.main.shake(600, 0.035);
                    this.isUltimating = false;
                    this.player.clearTint().setAlpha(1);

                    if (this.monster && this.monster.active) {
                        this.monster.health -= 65;
                        this.monster.setTint(0xff0000);

                        const kDirX = this.monster.x > this.player.x ? 1 : -1;
                        this.tweens.add({
                            targets: this.monster,
                            x: this.monster.x + (300 * kDirX),
                            y: this.monster.y - 250,
                            angle: 1440 * kDirX,
                            duration: 1200,
                            ease: 'Expo.easeOut',
                            onComplete: () => {
                                this.monster.setAngle(0).setTint(0xffcccc);
                                if (this.monster.health <= 0) {
                                    this.monster.health = 100;
                                    this.monster.setPosition(Phaser.Math.Between(100, 860), Phaser.Math.Between(100, 440));
                                }
                            }
                        });
                    }
                };

                // 统一监听空格键
                this.input.keyboard.on('keydown-SPACE', () => {
                    if (this.isUltimating) return; // 大招期间不能普通攻击
                    // 只有当玩家没在攻击动画中时，才触发攻击
                    const canAttack = !this.anims.exists('p_attack') ||
                        (this.player.anims.currentAnim?.key !== 'p_attack') ||
                        (!this.player.anims.isPlaying);

                    if (canAttack) {
                        if (this.anims.exists('p_attack')) {
                            this.player.play('p_attack');
                        }

                        // 判定伤害 (无论有无动画)
                        if (this.monster && this.monster.active) {
                            const dist = Phaser.Math.Distance.Between(this.player.x, this.player.y, this.monster.x, this.monster.y);
                            if (dist < 80) {
                                this.monster.health -= 20;
                                this.monster.setTint(0xffffff);
                                this.time.delayedCall(100, () => this.monster.setTint(0xffcccc));
                                if (this.monster.health <= 0) {
                                    this.monster.health = 100;
                                    this.monster.setPosition(Phaser.Math.Between(100, 860), Phaser.Math.Between(100, 440));
                                }
                            }
                        }
                    }
                });

                this.minimap = this.cameras.add(780, 20, 160, 100).setZoom(0.18).setName('mini');
                this.minimap.setBackgroundColor(0x000000);
                this.minimap.scrollX = 480; this.minimap.scrollY = 270;
                this.minimap.ignore([this.player.nameText, this.player.hpBarBg, this.player.hpBar]);
                if (this.monster) this.minimap.ignore([this.monster.nameText, this.monster.hpBarBg, this.monster.hpBar]);

                this.add.text(15, 15, 'WASD/方向键 移动 | 空格 攻击 | R 大招', {
                    fontSize: '18px',
                    fill: '#fff',
                    backgroundColor: 'rgba(0,0,0,0.6)',
                    padding: 8,
                    fontStyle: 'bold'
                });
            },
            update: function () {
                const speed = 250;
                let vx = 0, vy = 0;

                // 检查是否正在执行攻击动画
                const isAttacking = this.anims.exists('p_attack') &&
                    this.player.anims.isPlaying &&
                    this.player.anims.currentAnim?.key === 'p_attack';

                if (!isAttacking && !this.isUltimating) {
                    if (this.cursors.left.isDown || this.keys.A.isDown) vx = -speed;
                    else if (this.cursors.right.isDown || this.keys.D.isDown) vx = speed;

                    if (this.cursors.up.isDown || this.keys.W.isDown) vy = -speed;
                    else if (this.cursors.down.isDown || this.keys.S.isDown) vy = speed;
                }

                this.player.setVelocity(vx, vy);

                // --- 酷炫残影拖行效果 (Motion Trail) ---
                if (vx !== 0 || vy !== 0 || isAttacking) {
                    this.trailCounter = (this.trailCounter || 0) + 1;
                    if (this.trailCounter % 2 === 0) { // 提高频率
                        const ghost = this.add.sprite(this.player.x, this.player.y, this.player.texture.key);
                        ghost.setFrame(this.player.frame.name);
                        ghost.setFlipX(this.player.flipX);
                        ghost.setScale(this.player.scaleX, this.player.scaleY);
                        ghost.setOrigin(this.player.originX, this.player.originY);
                        ghost.setTint(0x00ffff, 0x0088ff, 0x00ffff, 0x0088ff); // 四角渐变色彩
                        ghost.setAlpha(0.8); // 提高初始透明度
                        ghost.setDepth(1); // 必须大于背景的 -10，且小于玩家的 2

                        this.tweens.add({
                            targets: ghost,
                            alpha: 0,
                            scaleX: ghost.scaleX * 0.9,
                            scaleY: ghost.scaleY * 0.9,
                            duration: 300,
                            ease: 'Power2',
                            onComplete: () => ghost.destroy()
                        });
                    }
                }

                if (!isAttacking && !this.isUltimating) {
                    if (vx !== 0 || vy !== 0) {
                        if (this.anims.exists('p_walk') && this.player.anims.currentAnim?.key !== 'p_walk') {
                            this.player.play('p_walk');
                        }
                        this.player.flipX = vx < 0;
                    } else {
                        if (this.anims.exists('p_idle') && this.player.anims.currentAnim?.key !== 'p_idle') {
                            this.player.play('p_idle');
                        }
                    }
                }
                this.updateUI(this.player);

                if (this.monster) {
                    const dist = Phaser.Math.Distance.Between(this.player.x, this.player.y, this.monster.x, this.monster.y);
                    if (dist < 300 && dist > 45) {
                        this.physics.moveToObject(this.monster, this.player, 120);
                        if (this.anims.exists('m_walk') && this.monster.anims.currentAnim?.key !== 'm_walk') {
                            this.monster.play('m_walk');
                        }
                        this.monster.flipX = this.player.x < this.monster.x;
                    } else {
                        this.monster.setVelocity(0);
                        if (this.anims.exists('m_idle') && this.monster.anims.currentAnim?.key !== 'm_idle') {
                            this.monster.play('m_idle');
                        }
                        // 怪物攻击玩家
                        if (dist <= 45) {
                            this.player.health -= 0.15;
                            this.player.setTint(0xff0000);
                            this.time.delayedCall(50, () => this.player.clearTint());
                        }
                    }
                    this.updateUI(this.monster);
                }
            }
        }
    };

    const game = new Phaser.Game(config);
    setPhaserGame(game);

    // 强制移开按钮焦点，让按键立即生效
    if (document.activeElement) document.activeElement.blur();
}

/**
 * 停止运行中的游戏
 */
export function stopInteractivePreview() {
    if (phaserGame) {
        phaserGame.destroy(true);
        setPhaserGame(null);
    }
    const placeholder = document.querySelector('.game-placeholder');
    if (placeholder) placeholder.classList.remove('hidden');

    const startBtn = document.getElementById('start-game-btn');
    const stopBtn = document.getElementById('stop-game-btn');
    if (startBtn) startBtn.style.display = 'inline-block';
    if (stopBtn) stopBtn.style.display = 'none';
}
