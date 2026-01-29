/**
 * 全局状态管理
 */

export const state = {
    projects: [],
    currentProject: null,
    currentDocument: null,
    isEditing: false
};

// 当前活跃的 Phaser 游戏实例
export let phaserGame = null;

/**
 * 更新游戏实例
 */
export function setPhaserGame(instance) {
    phaserGame = instance;
}
