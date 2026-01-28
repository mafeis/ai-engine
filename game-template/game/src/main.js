/**
 * AI 游戏 - Phaser 3 主入口
 * 
 * 游戏配置和场景加载
 */

import Phaser from 'phaser';
import { BootScene } from './scenes/BootScene.js';
import { MenuScene } from './scenes/MenuScene.js';
import { GameScene } from './scenes/GameScene.js';

// 游戏配置
const config = {
    type: Phaser.AUTO,
    parent: 'game-container',
    width: 800,
    height: 600,
    pixelArt: true,  // 像素风格渲染
    backgroundColor: '#1a1a2e',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 800 },
            debug: false
        }
    },
    scene: [BootScene, MenuScene, GameScene]
};

// 创建游戏实例
const game = new Phaser.Game(config);

// 导出游戏实例供调试使用
window.game = game;
