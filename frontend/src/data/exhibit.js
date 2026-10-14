export const eras = [
  { year: '1901', name: '大学肇始', title: '一纸奏折，开启百年求索', description: '1901 年，山东大学堂在济南创办。自此，为天下储人才、为国家图富强的理想，在这片土地上生根。', image: 'gate' },
  { year: '1917', name: '齐鲁弦歌', title: '弦歌不辍，文脉绵延', description: '齐鲁大学的校园承载了求知与育人的故事。今天，趵突泉校区的老建筑仍让这段记忆触手可及。', image: 'hall' },
  { year: '1932', name: '学人风华', title: '一代学人，留下精神坐标', description: '回望学人的身影，从医学课堂到编译馆，从科学探索到文化传承，读懂大学与时代的联系。', image: 'group' },
  { year: '1952', name: '薪火相续', title: '在新的起点，接续医学薪火', description: '1952 年院系调整，山东医学院组建。校园的医学传统在新的时代继续生长。', image: 'library' },
  { year: '2000', name: '山海新章', title: '三校合一，写就山大新章', description: '2000 年，山东大学、山东医科大学、山东工业大学合并，组建新的山东大学。新的篇章，由一代代山大人共同书写。', image: 'campus' }
]

export const photos = [
  { id: 'gate', title: '校友门前，往来皆是春秋', caption: '齐鲁大学时期的校友门', category: '建筑风物', date: '齐鲁大学时期', size: 'wide' },
  { id: 'garden', title: '绿荫里的葛罗神学院楼', caption: '春夏之交的葛罗神学院楼', category: '建筑风物', date: '拍摄年份未标注' },
  { id: 'gu', title: '顾颉刚先生', caption: '顾颉刚先生肖像', category: '学人风骨', date: '拍摄年份未标注', original: 'gu-original' },
  { id: 'group', title: '编译馆的一次合影', caption: '1935 年齐鲁大学编译馆同仁合影', category: '求学记忆', date: '1935', original: 'group-original' },
  { id: 'snow', title: '雪落求真楼', caption: '求真楼雪景', category: '建筑风物', date: '拍摄年份未标注', video: true },
  { id: 'hou', title: '侯宝璋教授在齐鲁大学', caption: '1932 年侯宝璋教授在齐鲁大学', category: '学人风骨', date: '1932' },
  { id: 'hall', title: '砖石间的时光：康穆堂', caption: '康穆堂南面观', category: '建筑风物', date: '拍摄年份未标注' },
  { id: 'classroom', title: '营养课堂上的专注', caption: '1941 年齐鲁大学护校的营养课堂', category: '求学记忆', date: '1941' },
  { id: 'lab', title: '让求知发生在实验室', caption: '齐鲁大学学生在做实验', category: '求学记忆', date: '齐鲁大学时期' },
  { id: 'autumn', title: '秋色，爬上求真楼', caption: '求真楼秋景', category: '建筑风物', date: '拍摄年份未标注' },
  { id: 'library', title: '书页深处，岁月悠长', caption: '奥古斯丁图书馆', category: '建筑风物', date: '拍摄年份未标注' },
  { id: 'campus', title: '从百年校园望见今天', caption: '山东大学齐鲁医学院校园全景', category: '建筑风物', date: '2021' }
]

export const questions = [
  { question: '山东大学的创办年份是？', choices: ['1898 年', '1901 年', '1917 年', '1932 年'], correct: 1, explanation: '山东大学前身是 1901 年创办的山东大学堂。百余年的办学历程，由此开启。', source: '山东大学官方历史沿革', tag: '大学肇始' },
  { question: '哪一句是山东大学的校训？', choices: ['自强不息，厚德载物', '博学而笃志，切问而近思', '学无止境，气有浩然', '允公允能，日新月异'], correct: 2, explanation: '“学无止境，气有浩然”表达了山大人不断求知与涵养浩然之气的精神追求。', source: '项目校史资料 · 校史.txt', tag: '山大精神' },
  { question: '新的山东大学由三校合并组建，发生在哪一年？', choices: ['1952 年', '1985 年', '1998 年', '2000 年'], correct: 3, explanation: '2000 年，山东大学、山东医科大学、山东工业大学合并，组建新的山东大学。', source: '山东大学官方历史沿革', tag: '山海新章' },
  { question: '山东大学医学学科的历史可以追溯到哪一年？', choices: ['1864 年', '1901 年', '1917 年', '1952 年'], correct: 0, explanation: '根据项目收录的校史资料，山东大学医学学科起源于 1864 年。', source: '项目校史资料 · 校史.txt', tag: '医学记忆' },
  { question: '哪句话体现了山东大学的办学宗旨？', choices: ['为天下储人才，为国家图富强', '以体育为先，以艺术为本', '只求技术，唯重实用', '专攻一艺，不问其他'], correct: 0, explanation: '“为天下储人才，为国家图富强”是贯穿山大办学历程的重要精神。', source: '项目校史资料 · 校史.txt', tag: '薪火相传' }
]

export const dialogues = [
  { title: '一所大学，何以历久弥新？', label: '大学与时代', turns: [
    { speaker: 'gu', text: '若把一所大学比作一部书，我们关心的，不只是它写了多久，更是它怎样诚实地记录、追问与思考。' },
    { speaker: 'hou', text: '在医学教育里，这份诚实同样珍贵。面对生命，我们的每一次判断，都应建立在严谨的观察与求证之上。' },
    { speaker: 'gu', text: '学问的门类不同，求真的方向却相通。保存一张老照片，也是在为后来的研究留下一条线索。' },
    { speaker: 'hou', text: '而把知识交到年轻人手里，让他们继续探索，正是一所大学生生不息的力量。' }
  ] },
  { title: '旧影像，为什么值得珍藏？', label: '影像与记忆', turns: [
    { speaker: 'gu', text: '老照片会留下文字未曾记录的细节：一处门窗、一间课堂，还有人们彼此相处的方式。' },
    { speaker: 'hou', text: '实验室的器具与课堂上的身影，也能帮助我们理解医学教育走过的路。' },
    { speaker: 'gu', text: '修复影像时，原始资料与后来的加工应当区分清楚。知道一张照片从何而来，和看清照片同样重要。' },
    { speaker: 'hou', text: '当今天的学生再看这些影像，也许会发现：探索未知的专注，可以跨越时代。' }
  ] }
]
