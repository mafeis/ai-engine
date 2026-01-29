/**
 * Phaser 3 游戏预览引擎
 */

import { api } from './api.js';
import { phaserGame, setPhaserGame } from './state.js';
import { getAssetUrl } from './utils.js';

/**
 * 启动交互式预览面板
 */
export async function showPreviewPanel(projectId) {
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

        // 4. 显示面板
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

        // 默认不自动启动，等待用户点击
        stopInteractivePreview();

    } catch (error) {
        console.error('加载预览面板失败:', error);
        alert('加载失败: ' + error.message);
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
                if (charData.animation?.exists) {
                    this.load.spritesheet('player', 'http://localhost:8000' + charData.animation.spritesheet_url, {
                        frameWidth: 64, frameHeight: 64
                    });
                } else {
                    this.load.image('player', charData.imgUrl);
                }

                if (monsterData) {
                    if (monsterData.animation?.exists) {
                        this.load.spritesheet('monster', 'http://localhost:8000' + monsterData.animation.spritesheet_url, {
                            frameWidth: 64, frameHeight: 64
                        });
                    } else {
                        this.load.image('monster', monsterData.imgUrl);
                    }
                }
            },
            create: function () {
                this.physics.world.setBounds(0, 0, 960, 540);
                const bg = this.add.image(480, 270, 'bg');
                const scale = Math.max(960 / bg.width, 540 / bg.height);
                bg.setScale(scale);

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

                this.player = this.physics.add.sprite(200, 270, 'player');
                this.player.setCollideWorldBounds(true);
                this.player.setScale(1.2);
                this.createUI(this.player, charData.name, 0x00ff00);

                if (charData.animation?.exists) {
                    this.anims.create({ key: 'p_idle', frames: this.anims.generateFrameNumbers('player', { start: 0, end: 3 }), frameRate: 8, repeat: -1 });
                    this.anims.create({ key: 'p_walk', frames: this.anims.generateFrameNumbers('player', { start: 4, end: 7 }), frameRate: 10, repeat: -1 });
                    this.anims.create({ key: 'p_attack', frames: this.anims.generateFrameNumbers('player', { start: 8, end: 11 }), frameRate: 15, repeat: 0 });
                    this.player.play('p_idle');
                }

                if (monsterData) {
                    this.monster = this.physics.add.sprite(700, 270, 'monster');
                    this.monster.setCollideWorldBounds(true);
                    this.monster.setScale(1.2).setTint(0xffcccc);
                    this.createUI(this.monster, monsterData.name + " (Monster)", 0xff0000);
                    if (monsterData.animation?.exists) {
                        this.anims.create({ key: 'm_idle', frames: this.anims.generateFrameNumbers('monster', { start: 0, end: 3 }), frameRate: 8, repeat: -1 });
                        this.anims.create({ key: 'm_walk', frames: this.anims.generateFrameNumbers('monster', { start: 4, end: 7 }), frameRate: 8, repeat: -1 });
                        this.monster.play('m_idle');
                    }
                }

                this.cursors = this.input.keyboard.createCursorKeys();
                this.keys = this.input.keyboard.addKeys('W,A,S,D,SPACE');
                this.input.keyboard.on('keydown-SPACE', () => {
                    if (this.anims.exists('p_attack') && this.player.anims.currentAnim?.key !== 'p_attack') {
                        this.player.play('p_attack');
                    }
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

                this.minimap = this.cameras.add(780, 20, 160, 100).setZoom(0.18).setName('mini');
                this.minimap.setBackgroundColor(0x000000);
                this.minimap.scrollX = 480; this.minimap.scrollY = 270;
                this.minimap.ignore([this.player.nameText, this.player.hpBarBg, this.player.hpBar]);
                if (this.monster) this.minimap.ignore([this.monster.nameText, this.monster.hpBarBg, this.monster.hpBar]);

                this.add.text(15, 15, 'WASD移动 | 空格攻击', { fontSize: '16px', fill: '#fff', backgroundColor: 'rgba(0,0,0,0.6)', padding: 5 });
            },
            update: function () {
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

                if (!isAttacking) {
                    if (vx !== 0 || vy !== 0) {
                        if (this.anims.exists('p_walk') && this.player.anims.currentAnim?.key !== 'p_walk') this.player.play('p_walk');
                        this.player.flipX = vx < 0;
                    } else {
                        if (this.anims.exists('p_idle') && this.player.anims.currentAnim?.key !== 'p_idle') this.player.play('p_idle');
                    }
                }
                this.updateUI(this.player);

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

    setPhaserGame(new Phaser.Game(config));
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
