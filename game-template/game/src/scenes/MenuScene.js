/**
 * 菜单场景 - 游戏主菜单
 */

export class MenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MenuScene' });
    }

    create() {
        const { width, height } = this.cameras.main;

        // 背景渐变效果
        const graphics = this.add.graphics();
        graphics.fillGradientStyle(0x1a1a2e, 0x1a1a2e, 0x2d2d4a, 0x2d2d4a, 1);
        graphics.fillRect(0, 0, width, height);

        // 游戏标题
        this.add.text(width / 2, height / 3, 'AI 游戏', {
            font: 'bold 48px Arial',
            fill: '#ffffff',
            stroke: '#6366f1',
            strokeThickness: 4
        }).setOrigin(0.5);

        // 开始按钮
        const startBtn = this.add.text(width / 2, height / 2 + 50, '▶ 开始游戏', {
            font: '24px Arial',
            fill: '#ffffff',
            backgroundColor: '#6366f1',
            padding: { x: 30, y: 15 }
        })
            .setOrigin(0.5)
            .setInteractive({ useHandCursor: true });

        // 按钮悬停效果
        startBtn.on('pointerover', () => {
            startBtn.setStyle({ backgroundColor: '#818cf8' });
        });

        startBtn.on('pointerout', () => {
            startBtn.setStyle({ backgroundColor: '#6366f1' });
        });

        // 点击开始游戏
        startBtn.on('pointerdown', () => {
            this.scene.start('GameScene');
        });

        // 版本信息
        this.add.text(width / 2, height - 30, 'Powered by AI Engine', {
            font: '14px Arial',
            fill: '#64748b'
        }).setOrigin(0.5);
    }
}
