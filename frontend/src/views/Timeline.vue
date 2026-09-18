<template>
  <div class="timeline-page">
    <h2 class="page-title">山大校史时间轴</h2>
    <p class="page-desc">点击时间节点，探索山东大学趵突泉校区的百年发展历程</p>

    <div class="timeline-container">
      <div class="timeline-line"></div>
      <div v-for="(item, idx) in events" :key="idx"
        class="timeline-item" :class="{ left: idx % 2 === 0, right: idx % 2 !== 0 }">
        <div class="timeline-dot"></div>
        <div class="timeline-card" @click="selectEvent(item)">
          <div class="timeline-year">{{ item.year }}</div>
          <h3 class="timeline-title">{{ item.title }}</h3>
          <p class="timeline-desc">{{ item.desc }}</p>
          <div v-if="item.tags" class="timeline-tags">
            <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const events = ref([
  {
    year: '1901',
    title: '山东大学堂创办',
    desc: '袁世凯上奏《遵旨改设学堂酌拟试办章程折》，山东大学堂在济南泺源书院正式创办，是继京师大学堂之后中国创办的第二所官立大学堂。',
    tags: ['建校', '清末']
  },
  {
    year: '1904',
    title: '迁至杆石桥新址',
    desc: '山东大学堂迁至济南杆石桥新校址（今山东省实验中学一带），办学条件得到改善。',
    tags: ['校区']
  },
  {
    year: '1917',
    title: '齐鲁大学正式定名',
    desc: '由美国、英国、加拿大基督教会联合创办的山东基督教共合大学正式更名为齐鲁大学，校址位于今山东大学趵突泉校区，是中国最早的教会大学之一。',
    tags: ['齐鲁大学', '教会大学']
  },
  {
    year: '1930',
    title: '国立青岛大学改名国立山东大学',
    desc: '国立青岛大学正式改名为国立山东大学，杨振声任校长，赵太侔任教务长，闻一多任文学院院长，梁实秋任外文系主任。',
    tags: ['更名', '民国']
  },
  {
    year: '1930-1934',
    title: '老舍任教山东大学',
    desc: '老舍（舒庆春）受聘于国立山东大学，先后任中文系讲师、教授，讲授《文学概论》《小说作法》等课程。在济南期间创作了《大明湖》《猫城记》《离婚》等作品。',
    tags: ['老舍', '人文']
  },
  {
    year: '1934',
    title: '侯宝璋任齐鲁大学医学院教授',
    desc: '著名病理学家侯宝璋受聘于齐鲁大学医学院，任病理学教授，后任医学院院长。他在病理学研究和医学教育方面成就卓著，培养了大批医学人才。',
    tags: ['侯宝璋', '医学教育']
  },
  {
    year: '1952',
    title: '院系调整',
    desc: '全国高等学校院系调整，齐鲁大学解体，其医学院与山东省立医学院、华东白求恩医学院合并成立山东医学院，校址设在原齐鲁大学校园（今趵突泉校区）。',
    tags: ['院系调整', '建国初期']
  },
  {
    year: '1970',
    title: '山东医学院与山东中医学院合并',
    desc: '山东医学院与山东中医学院合并，仍称山东医学院。1976年两校重新分开。',
    tags: ['合并']
  },
  {
    year: '1985',
    title: '更名为山东医科大学',
    desc: '山东医学院更名为山东医科大学，成为卫生部直属重点医科大学，办学水平和规模进一步提升。',
    tags: ['更名', '改革开放']
  },
  {
    year: '2000',
    title: '三校合并组建新山东大学',
    desc: '山东大学、山东医科大学、山东工业大学合并组建新的山东大学。原山东医科大学校园更名为山东大学趵突泉校区，现为山东大学齐鲁医学院所在地。',
    tags: ['合并', '新山大']
  }
])

const selectEvent = (item) => {
  console.log('选中事件:', item.title)
  // 后续可跳转数字人讲解该段历史
}
</script>

<style scoped>
.timeline-page { max-width: 900px; margin: 0 auto; }
.page-title { font-size: 24px; color: #8B0000; margin-bottom: 8px; padding-left: 12px; border-left: 4px solid #8B0000; }
.page-desc { color: #777; font-size: 14px; margin-bottom: 32px; padding-left: 16px; }
.timeline-container { position: relative; padding: 20px 0; }
.timeline-line {
  position: absolute;
  left: 50%;
  top: 0; bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #8B0000, #d4a574);
  transform: translateX(-50%);
}
.timeline-item {
  position: relative;
  width: 50%;
  padding: 16px 40px;
  margin-bottom: 8px;
}
.timeline-item.left { left: 0; text-align: right; }
.timeline-item.right { left: 50%; text-align: left; }
.timeline-dot {
  position: absolute;
  top: 28px;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: #8B0000;
  border: 3px solid #fff;
  box-shadow: 0 0 0 2px #8B0000;
  z-index: 1;
}
.timeline-item.left .timeline-dot { right: -8px; }
.timeline-item.right .timeline-dot { left: -8px; }
.timeline-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: inline-block;
  text-align: left;
  max-width: 100%;
}
.timeline-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(139,0,0,0.15); }
.timeline-year {
  font-size: 20px;
  font-weight: 700;
  color: #8B0000;
  margin-bottom: 6px;
}
.timeline-title { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 8px; }
.timeline-desc { font-size: 13px; color: #666; line-height: 1.7; }
.timeline-tags { margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap; }
.tag {
  font-size: 11px;
  padding: 2px 8px;
  background: #f5f0e8;
  color: #8B6914;
  border-radius: 10px;
}
</style>
