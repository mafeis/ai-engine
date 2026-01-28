/**
 * 游戏场景 - 主游戏逻辑
 * 
 * 这是一个模板场景，会根据游戏配置动态生成
 */

export class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });

        // 玩家对象
        this.player = null;

        // 控制键
        this.cursors = null;
    }

    create() {
        const { width, height } = this.cameras.main;

        // 创建简单的地面平台
        const platforms = this.physics.add.staticGroup();

        // 地面
        const ground = this.add.rectangle(width / 2, height - 20, width, 40, 0x4f46e5);
        platforms.add(ground);
        this.physics.add.existing(ground, true);

        // 一些平台
        const platform1 = this.add.rectangle(200, height - 150, 150, 20, 0x4f46e5);
        platforms.add(platform1);
        this.physics.add.existing(platform1, true);

        const platform2 = this.add.rectangle(600, height - 250, 150, 20, 0x4f46e5);
        platforms.add(platform2);
        this.physics.add.existing(platform2, true);

        const platform3 = this.add.rectangle(400, height - 350, 150, 20, 0x4f46e5);
        platforms.add(platform3);
        this.physics.add.existing(platform3, true);

        // 创建玩家（简单的矩形代替，实际会用AI生成的图片）
        this.player = this.add.rectangle(100, height - 100, 32, 48, 0x22c55e);
        this.physics.add.existing(this.player);
        this.player.body.setBounce(0.1);
        this.player.body.setCollideWorldBounds(true);

        // 玩家与平台碰撞
        this.physics.add.collider(this.player, platforms);

        // 控制键
        this.cursors = this.input.keyboard.createCursorKeys();

        // 添加一些装饰文字
        this.add.text(width / 2, 50, '使用方向键移动，上键跳跃', {
            font: '16px Arial',
            fill: '#94a3b8'
        }).setOrigin(0.5);

        // 返回菜单按钮
        const backBtn = this.add.text(20, 20, '← 返回菜单', {
            font: '14px Arial',
            fill: '#94a3b8'
        }).setInteractive({ useHandCursor: true });

        backBtn.on('pointerdown', () => {
            this.scene.start('MenuScene');
        });
    }

    update() {
        if (!this.player || !this.player.body) return;

        const speed = 200;
        const jumpForce = -400;

        // 左右移动
        if (this.cursors.left.isDown) {
            this.player.body.setVelocityX(-speed);
        } else if (this.cursors.right.isDown) {
            this.player.body.setVelocityX(speed);
        } else {
            this.player.body.setVelocityX(0);
        }

        // 跳跃（只有在地面上才能跳）
        if (this.cursors.up.isDown && this.player.body.touching.down) {
            this.player.body.setVelocityY(jumpForce);
        }
    }
}
