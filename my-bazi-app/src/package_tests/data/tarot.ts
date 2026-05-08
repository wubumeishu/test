/**
 * 大阿尔卡纳 22 张牌数据
 * 融合荣格原型心理学与东方禅意语境
 *
 * imgUrl 线上路径：https://api.aiyuechuan.cn/static/tarot/major_N.jpg
 * 图片来源：Wikimedia Commons，1909 年 Rider-Waite 原版扫描，公有领域
 */

export interface TarotCard {
  id: number
  name: string
  nameEn: string
  keywords: string
  description: string
  imgUrl: string
}

export const majorArcana: TarotCard[] = [
  {
    id: 0,
    name: '愚人',
    nameEn: 'The Fool',
    keywords: '冒险、初心、盲目乐观、无限可能、新的开始',
    description: '牌面上的年轻人站在悬崖边，仰望天空，身边的白狗正在提醒他危险，他却毫不在意。这不是愚蠢，而是一种近乎禅定的无执——他不被过去的经验束缚，也不被未来的恐惧拖拽，只是全然活在此刻的跃动中。当愚人出现，宇宙在邀请你放下"我应该怎样"的包袱，带着一颗赤子之心踏上未知的旅程。你的直觉比你的计划更可靠，你的勇气比你的准备更重要。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_0.jpg',
  },
  {
    id: 1,
    name: '魔术师',
    nameEn: 'The Magician',
    keywords: '意志力、创造、专注、掌控、将潜能化为现实',
    description: '魔术师一手指天、一手指地，桌上摆着权杖、圣杯、宝剑与星币——四种元素，四种力量，尽在掌握。他不是在变魔术，他是在将内在的意志投射为外在的现实。当这张牌出现，它在告诉你：你已经拥有了所需的一切工具，缺的只是那一份"我能做到"的笃定。专注你的意图，凝聚你的能量，此刻正是将想法落地的最佳时机。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_1.jpg',
  },
  {
    id: 2,
    name: '女祭司',
    nameEn: 'The High Priestess',
    keywords: '直觉、神秘、内在智慧、潜意识、沉默的知晓',
    description: '她端坐于两根柱子之间，身后是一道帷幕，帷幕后面是你尚未看见的真相。她不说话，因为最深的智慧无法用语言传递，只能用心去感知。女祭司是你内在那个"知道但说不清楚"的声音——那个在你做决定前一秒闪过的直觉，那个在深夜让你辗转反侧的预感。此刻，停止向外寻找答案，向内沉潜，你的潜意识已经知道你需要知道的一切。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_2.jpg',
  },
  {
    id: 3,
    name: '女皇',
    nameEn: 'The Empress',
    keywords: '丰盛、创造力、母性、感官享受、自然生命力',
    description: '她坐在麦田与森林之间，头戴十二星冠，怀抱大地的丰饶。女皇是生命本身的象征——不是那种努力挣来的丰盛，而是自然流淌的富足。她提醒你，创造不需要强迫，生长不需要焦虑。当你与自己的身体、感官和情感重新连接，当你允许自己去爱、去享受、去滋养，丰盛就会像春天的草木一样，自然而然地生长出来。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_3.jpg',
  },
  {
    id: 4,
    name: '皇帝',
    nameEn: 'The Emperor',
    keywords: '权威、秩序、结构、父性、稳定的掌控',
    description: '皇帝端坐于石制宝座，背后是光秃秃的山峰——那是意志力雕刻出的风景。他不依赖情感，他依赖规则、逻辑和长远的战略眼光。皇帝的出现，是在提醒你建立秩序的重要性：为你的生活设立边界，为你的目标制定计划，用纪律和结构为自由创造土壤。真正的自由不是无拘无束，而是在清晰的框架内，做自己真正想做的事。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_4.jpg',
  },
  {
    id: 5,
    name: '教皇',
    nameEn: 'The Hierophant',
    keywords: '传统、信仰、精神导师、集体智慧、寻求指引',
    description: '教皇坐于神圣的殿堂，两名信徒跪于脚下聆听教诲。他是传统与智慧的守护者，是连接人间与神圣的桥梁。当这张牌出现，它可能在问你：你是否需要一位导师？你是否在某个传统或信仰体系中寻找归属感？也可能是在提醒你，有些古老的智慧值得尊重，不必事事标新立异。向有经验的人请教，或者回归某种让你感到稳定的精神实践，此刻是合适的时机。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_5.jpg',
  },
  {
    id: 6,
    name: '恋人',
    nameEn: 'The Lovers',
    keywords: '选择、关系、价值观对齐、灵魂连接、真实的爱',
    description: '亚当与夏娃站在伊甸园，天使拉斐尔在云端俯视。这张牌的核心不是浪漫，而是选择——一个需要你用整个灵魂去做的选择。恋人牌出现时，往往意味着你站在一个人生的十字路口，需要在两种价值观、两种生活方式或两段关系之间做出抉择。真正的爱，无论是对他人还是对自己，都始于诚实：你真正渴望的是什么？你愿意为之承担什么？',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_6.jpg',
  },
  {
    id: 7,
    name: '战车',
    nameEn: 'The Chariot',
    keywords: '意志、胜利、自律、掌控方向、克服阻碍',
    description: '战车由两匹方向相反的狮身人面兽拉动，驾车者不用缰绳，只凭意志力驾驭。这是一幅关于内在冲突与整合的图景——当你内心的两股力量（理性与感性、进取与退缩）都被你看见并驾驭，你就能以惊人的速度向前推进。战车的胜利不是靠蛮力，而是靠专注、自律和对目标的绝对笃定。此刻，收紧你的意志，不要被外界的噪音分散注意力。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_7.jpg',
  },
  {
    id: 8,
    name: '力量',
    nameEn: 'Strength',
    keywords: '内在力量、温柔的勇气、耐心、驯服本能、慈悲',
    description: '一位女子用双手轻轻托住一头狮子的嘴，狮子没有挣扎，反而顺从地低下了头。这不是征服，这是驯化——用爱与耐心，而非恐惧与强迫。力量牌告诉你，真正的强大不是压制你的愤怒、恐惧或欲望，而是与它们同在，理解它们，温柔地引导它们。你内心那头"狮子"——那些让你感到失控的情绪——正在等待你用慈悲而非批判去靠近它。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_8.jpg',
  },
  {
    id: 9,
    name: '隐士',
    nameEn: 'The Hermit',
    keywords: '独处、内省、寻找真相、智慧、引导他人',
    description: '隐士独自站在雪山之巅，手持一盏灯笼，灯光微弱却足以照亮脚下的路。他不是在逃避世界，他是在主动选择独处，因为他知道：有些答案只能在寂静中找到。当隐士出现，宇宙在邀请你暂时退出喧嚣，给自己一段独处的时光。不是为了逃避，而是为了倾听那个在日常噪音中被淹没的内在声音。你已经走了很远，是时候停下来，看看自己究竟在走向哪里。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_9.jpg',
  },
  {
    id: 10,
    name: '命运之轮',
    nameEn: 'Wheel of Fortune',
    keywords: '命运转折、循环、机遇、因果、接受变化',
    description: '巨大的轮子在宇宙中旋转，轮缘上有上升的人，也有下降的人，而轮子本身永不停歇。命运之轮提醒你：没有什么是永恒不变的，无论此刻是高峰还是低谷，都只是轮回中的一个节点。当好运降临，不要忘乎所以；当逆境来临，不要绝望沉沦。真正的智慧是在轮子旋转时，保持内心的稳定——不是不感受，而是不被带走。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_10.jpg',
  },
  {
    id: 11,
    name: '正义',
    nameEn: 'Justice',
    keywords: '公平、真相、因果、责任、清醒的判断',
    description: '正义女神手持天平与宝剑，眼神清澈而无情。她不是在惩罚，她是在如实呈现：你的每一个选择，都在宇宙的账本上留下了记录。正义牌出现时，往往意味着一个需要你诚实面对的时刻——对自己诚实，对他人诚实，对事实诚实。逃避真相只会让天平继续倾斜，而当你愿意承担自己行为的后果，真正的平衡才会到来。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_11.jpg',
  },
  {
    id: 12,
    name: '倒吊人',
    nameEn: 'The Hanged Man',
    keywords: '暂停、放手、换个视角、牺牲、顿悟',
    description: '他倒挂在树上，脸上却带着平静甚至满足的神情。他没有挣扎，因为他知道：有时候，最有力量的行动是什么都不做。倒吊人是一张关于"暂停"的牌——不是失败，不是停滞，而是主动选择的等待。当你愿意放下对结果的执念，当你愿意从一个完全不同的角度看待问题，你会发现那些曾经让你困惑的事情，突然变得清晰起来。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_12.jpg',
  },
  {
    id: 13,
    name: '死神',
    nameEn: 'Death',
    keywords: '结束与开始、蜕变、放下、转化、不可避免的改变',
    description: '死神骑着白马缓缓前行，无论是国王还是平民，都无法阻挡他的步伐。但请注意：在他身后，太阳正在升起。死神牌极少意味着字面上的死亡，它更多代表一种深刻的转化——某段关系、某种身份、某个信念，已经走到了它的终点。这种结束令人悲伤，但它是新生的前提。你无法带着旧的自己进入新的生命，放手，才是真正的勇气。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_13.jpg',
  },
  {
    id: 14,
    name: '节制',
    nameEn: 'Temperance',
    keywords: '平衡、耐心、整合、中道、炼金术式的转化',
    description: '天使将水在两个杯子之间来回倾倒，动作流畅而精准，一只脚踏在水中，一只脚踏在陆地上。节制是一种动态的平衡——不是静止不动，而是在流动中保持和谐。当这张牌出现，它在提醒你：此刻需要的不是极端，而是融合。将你生命中看似对立的部分——工作与休息、理性与感性、给予与接受——找到它们之间的黄金比例，你会发现一种超越两者的第三种可能。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_14.jpg',
  },
  {
    id: 15,
    name: '恶魔',
    nameEn: 'The Devil',
    keywords: '束缚、执念、阴影、物质诱惑、自我囚禁',
    description: '两个人被链条锁在恶魔的宝座上，但仔细看，链条是松的——他们随时可以离开，却选择留下。恶魔牌揭示的是我们内心最深处的执念与恐惧：那些让你感到被困住的关系、习惯、信念，往往是你自己在维持的幻觉。它不是在评判你，而是在照亮你的阴影。当你愿意直视那些让你感到羞耻或恐惧的部分，你就已经开始松开那根链条了。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_15.jpg',
  },
  {
    id: 16,
    name: '塔',
    nameEn: 'The Tower',
    keywords: '突然崩塌、觉醒、打破幻象、混乱中的解放',
    description: '闪电击中高塔，火焰从窗口喷出，人们从塔顶坠落。这是塔罗中最令人恐惧的画面之一，但它所代表的，是一种必要的破坏。那座塔，是你建立在错误基础上的信念、关系或生活方式。当它轰然倒塌，你会感到恐惧和混乱，但在废墟之下，是更坚实的地基。塔牌的出现，往往意味着一次无法回避的觉醒——那些你一直不愿面对的真相，终于以最戏剧化的方式来敲门了。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_16.jpg',
  },
  {
    id: 17,
    name: '星星',
    nameEn: 'The Star',
    keywords: '希望、疗愈、信念、宁静、与宇宙同频',
    description: '一位裸体女子跪在水边，将水倒入大地与河流，头顶是璀璨的星空。在经历了塔的崩塌之后，星星带来的是疗愈与希望。她的裸体象征着真实与脆弱——在宇宙面前，你不需要任何防御，只需要如实地存在。星星牌告诉你：你是被宇宙所爱的，你的伤口正在愈合，你的祈愿正在被听见。此刻，允许自己相信美好，允许自己被滋养。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_17.jpg',
  },
  {
    id: 18,
    name: '月亮',
    nameEn: 'The Moon',
    keywords: '幻象、潜意识、恐惧、直觉、迷雾中的真相',
    description: '月亮高悬，两只狗（或狼）对着月亮嚎叫，一只龙虾从水中爬出，远处是两座塔。月亮的光是反射的光，它照亮的不是真相，而是真相的影子。月亮牌出现时，往往意味着你正处于一段迷雾之中——事情不像表面看起来那样，你的恐惧和幻想正在扭曲你对现实的感知。此刻需要的不是行动，而是耐心：等待迷雾散去，信任你的直觉，但不要被它带着跑。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_18.jpg',
  },
  {
    id: 19,
    name: '太阳',
    nameEn: 'The Sun',
    keywords: '喜悦、活力、成功、真实的自我、光明正大',
    description: '一个孩子骑着白马，在向日葵盛开的花园里奔跑，头顶是灿烂的太阳。太阳牌是塔罗中最纯粹的喜悦——不是那种需要努力维持的快乐，而是生命本身的光芒。当太阳出现，它在告诉你：此刻是真实的，此刻是美好的，你值得被这份光照耀。放下那些让你躲在阴影里的自我怀疑，让自己被看见，让自己发光。你的真实，就是你最大的礼物。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_19.jpg',
  },
  {
    id: 20,
    name: '审判',
    nameEn: 'Judgement',
    keywords: '觉醒、召唤、救赎、重生、回应内心的呼唤',
    description: '天使吹响号角，死者从棺材中复活，仰望天空。审判牌不是关于被评判，而是关于一次深刻的觉醒——你听到了来自灵魂深处的召唤，那个声音在问你：你真正想要的生命是什么样的？此刻是一个重新评估和重新选择的时刻。那些你曾经压抑的渴望、那些你曾经放弃的梦想，正在以某种方式重新浮现。这一次，你愿意回应吗？',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_20.jpg',
  },
  {
    id: 21,
    name: '世界',
    nameEn: 'The World',
    keywords: '圆满、整合、完成、宇宙意识、新循环的前夕',
    description: '一位舞者被月桂花环环绕，四角是四种神圣生物——狮子、牛、鹰与天使。她在舞动，因为她已经完成了一段旅程，整合了所有的经历，成为了一个更完整的自己。世界牌是大阿尔卡纳的终点，也是新循环的起点。当它出现，意味着你正在经历或即将经历一种深刻的圆满感——不是因为一切都完美，而是因为你终于与自己的生命和解，与宇宙同频共振。',
    imgUrl: 'https://api.aiyuechuan.cn/static/tarot/major_21.jpg',
  },
]
