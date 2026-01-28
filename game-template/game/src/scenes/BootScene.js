/**
 * 启动场景 - 加载游戏资源
 */

export class BootScene extends Phaser.Scene {
    constructor() {
        super({ key: 'BootScene' });
    }

    preload() {
        // 显示加载进度
        const { width, height } = this.cameras.main;

        // 进度条背景
        const progressBox = this.add.graphics();
        progressBox.fillStyle(0x2d2d4a, 0.8);
        progressBox.fillRect(width / 2 - 160, height / 2 - 25, 320, 50);

        // 进度条
        const progressBar = this.add.graphics();

        // 加载文字
        const loadingText = this.add.text(width / 2, height / 2 - 50, '加载中...', {
            font: '20px Arial',
            fill: '#ffffff'
        }).setOrigin(0.5);

        // 百分比文字
        const percentText = this.add.text(width / 2, height / 2, '0%', {
            font: '18px Arial',
            fill: '#ffffff'
        }).setOrigin(0.5);

        // 监听加载进度
        this.load.on('progress', (value) => {
            percentText.setText(parseInt(value * 100) + '%');
            progressBar.clear();
            progressBar.fillStyle(0x6366f1, 1);
            progressBar.fillRect(width / 2 - 150, height / 2 - 15, 300 * value, 30);
        });

        this.load.on('complete', () => {
            progressBar.destroy();
            progressBox.destroy();
            loadingText.destroy();
            percentText.destroy();
        });

        // 加载资源
        // TODO: 从配置文件动态加载资源
        // this.load.image('player', 'assets/characters/hero/selected/final.png');
        // this.load.image('background', 'assets/scenes/level1/selected/final.png');
        // this.load.audio('bgm', 'assets/audio/bgm/main/selected/final.wav');
    }

    create() {
        // 跳转到菜单场景
        this.scene.start('MenuScene');
    }
}
