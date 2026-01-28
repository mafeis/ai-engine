这是一份为《水浒世界》量身定制的音频设计文档（Audio Design Document）。

本方案旨在融合**中国传统民乐（如：唢呐、琵琶、二胡、大鼓）**与**现代影视配乐（Cinematic Orchestral）**，通过极具张力的音效表现北宋末年的草莽英雄气概与乱世动荡。

---

# 《水浒世界》音频设计文档 (ADD)

## 1. 背景音乐 (BGM) 设计

### 1.1 场景 BGM
| 场景名称 | 风格描述 | AI 生成提示词 (Prompt) |
| :--- | :--- | :--- |
| **水泊梁山 (主城)** | 雄壮、开阔、归属感。以笛子和古筝开场，随后加入厚重的弦乐与远处的号角。 | Epic Chinese martial arts theme, majestic bamboo flute melody, grand orchestral strings, traditional guzheng plucking, sense of brotherhood and honor, cinematic, wide stereo. |
| **东京汴梁 (繁华都市)** | 喧闹、市井、宫廷感。快节奏的琵琶与中阮，伴随轻快的打击乐。 | Bustling ancient Chinese city ambience, upbeat Pipa and Zhongruan, lively percussion, festive atmosphere, Northern Song Dynasty style, traditional folk ensemble. |
| **快活林酒肆 (酒馆)** | 悠闲、江湖、微醺感。低沉的胡琴伴随偶尔的木鱼声，节奏松散。 | Relaxing tavern music, low Erhu melody, wooden percussion, rustic atmosphere, drunken folk style, intimate and warm, traditional Chinese inn vibes. |
| **荒野/林间 (探索)** | 肃杀、紧迫、危机四伏。极简的打击乐，伴随凄凉的萧声。 | Desolate wilderness, eerie Xiao (vertical flute) solo, minimalist dark percussion, suspenseful, wind blowing soundscape, traditional Chinese mystery. |

### 1.2 战斗 BGM
| 战斗类型 | 风格描述 | AI 生成提示词 (Prompt) |
| :--- | :--- | :--- |
| **杂兵遭遇战** | 节奏明快，鼓点密集。快节奏的二胡拉弦与中国大鼓。 | Fast-paced combat music, intense Chinese Taiko drums, rapid Erhu tremolo, energetic martial arts action, high adrenaline, traditional percussion ensemble. |
| **英雄对决 (BOSS战)** | 震撼、史诗、压迫感。唢呐领奏，伴随厚重的管弦乐与人声合唱。 | Epic boss battle theme, heroic Suona (Chinese trumpet) lead, powerful cinematic orchestra, deep male choir, intense rhythmic tension, legendary hero confrontation. |
| **攻城掠地 (大型战场)** | 宏大、悲壮、混乱。沉重的号角，密集的战鼓，金属撞击般的节奏。 | Massive war theme, deep war horns, thunderous battle drums, chaotic orchestral brass, tragic heroism, large scale battlefield atmosphere. |

### 1.3 特殊事件 BGM
| 事件名称 | 风格描述 | AI 生成提示词 (Prompt) |
| :--- | :--- | :--- |
| **兄弟结义/庆功** | 豪迈、暖心、明亮。唢呐高亢但柔和，伴随响亮的锣鼓。 | Joyful celebration theme, bright Suona melody, festive gongs and cymbals, warm brotherhood atmosphere, triumphant Chinese folk music. |
| **英雄陨落/悲剧** | 凄凉、哀恸。极慢的二胡长音，伴随空灵的古琴。 | Sorrowful funeral theme, weeping Erhu solo, minimalist Guqin, tragic and emotional, slow tempo, sense of loss and mourning. |

---

## 2. 音效列表 (SFX)

### 2.1 角色音效
*   **脚步声 (Footsteps):** 
    *   *草地:* 干燥的草叶摩擦声。 (Dry grass crunching, light leather boot steps)
    *   *木板:* 沉重的木头回响，模拟酒楼地板。 (Thumping wood floor, creaking planks, heavy footsteps)
*   **攻击音效 (Attack):**
    *   *挥砍:* 凌厉的破空声。 (Sharp sword swoosh, high-frequency air cutting)
    *   *打击:* 重型钝器（如鲁智深禅杖）击中肉体的闷响。 (Heavy blunt impact, bone crushing thud, deep bass)
*   **受伤/死亡 (Damage/Death):**
    *   *甲片撞击:* 角色受击时金属盔甲的震动声。 (Metallic armor clinking, chainmail impact)
    *   *倒地:* 沉重的躯体撞击尘土的声音。 (Heavy body fall, dust impact, thud)

### 2.2 环境音效
*   **水泊波动 (Water):** 梁山水泊微弱的浪花拍岸声。 (Gentle lake ripples, water splashing against wooden boat, serene nature)
*   **战场环境 (War Ambience):** 远处的厮杀声、马鸣声、旗帜在风中猎猎作响。 (Distant battlefield screams, horse neighing, cloth fluttering in strong wind, chaotic background)
*   **天气 (Weather):** 
    *   *风雪 (山神庙):* 寒风呼啸，夹杂着雪粒撞击木门的声音。 (Howling winter wind, blizzard ambience, rattling wooden door)

### 2.3 UI 音效
*   **点击/确认:** 响亮的木板快板声或清脆的玉石碰撞声。 (Crisp Chinese woodblock clack, jade stone clinking, positive feedback)
*   **取消/返回:** 沉闷的纸张翻动声。 (Heavy paper parchment rustling, low frequency thud)
*   **任务达成:** 清脆的铃铛声伴随短促的古筝扫弦。 (Clear bell chime, short Guzheng glissando, rewarding sound)

### 2.4 道具音效
*   **饮酒 (Drinking):** 液体倒入瓷碗的咕嘟声，随后是豪爽的摔碗声。 (Liquid pouring into ceramic bowl, glugging sound, ceramic bowl shattering)
*   **拾取铜钱 (Money):** 大量金属硬币碰撞的清脆声。 (Jingling copper coins, metallic clinking, money bag handling)
*   **展开卷轴 (Scroll):** 粗糙纸张或丝绸摩擦展开的声音。 (Unrolling ancient paper scroll, friction sound of silk and parchment)

---

## 3. 语音设计 (Voiceover)

### 3.1 语音风格指南
*   **语调:** 豪放、粗犷、多用方言口音（山东、河北等北方韵味）。
*   **核心角色示例:**
    *   **鲁智深:** 大嗓门，语调浑厚，带有佛门弟子的威严与草莽的狂放。
    *   **林冲:** 语气压抑、冷静，但在战斗中爆发力极强。
    *   **李逵:** 语速快，嗓音沙哑，伴随大量的咆哮。

### 3.2 常用语音类型
*   **战斗喊麦:** "吃洒家一铲！"、"挡我者死！"、"为了梁山！"
*   **闲置语音:** "这鸟天气，真想吃口好酒。"
*   **互动语音:** "哥哥，别来无恙？"

---

## 4. 技术规格 (Technical Specs)
*   **采样率:** 48kHz / 24-bit。
*   **格式:** 背景音乐使用 OGG (循环处理)，音效使用 WAV (无损)。
*   **动态混音:** 战斗时自动衰减环境音（Ducking），强调打击感与技能音效。