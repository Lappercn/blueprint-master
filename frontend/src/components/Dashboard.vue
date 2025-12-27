<template>
  <div class="dashboard-container">
    <div class="stats-overview">
      <el-card shadow="hover" class="stat-card user-stat-card">
        <template #header>
          <div class="card-header">
            <span>👥 用户统计</span>
          </div>
        </template>
        <div class="stat-value-container">
            <div class="total-label">总用户数</div>
            <div class="total-number">{{ userStats.total_users || 0 }}</div>
        </div>
        <el-divider style="margin: 15px 0;" />
        <div class="active-users-section">
            <div class="section-title">最近活跃 (Top 20)</div>
            <div class="user-tags" v-if="userStats.active_users && userStats.active_users.length > 0">
                <el-tooltip
                    v-for="(user, index) in userStats.active_users" 
                    :key="index"
                    :content="'上次登录: ' + formatDate(user.last_login)"
                    placement="top"
                >
                    <el-tag 
                        size="small" 
                        class="user-tag"
                        :effect="index < 3 ? 'dark' : 'plain'"
                        :type="index < 3 ? 'danger' : ''"
                    >
                        {{ user.username }}
                    </el-tag>
                </el-tooltip>
            </div>
            <div v-else class="empty-text">暂无活跃用户</div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="stat-card">
        <template #header>
          <div class="card-header">
            <span>📚 热门书籍/方法论</span>
            <el-select v-model="selectedRankRole" placeholder="选择角色查看" size="small" style="width: 120px; margin-left: 10px;">
              <el-option label="总榜" value="all" />
              <el-option label="CEO/高管" value="cxo" />
              <el-option label="客户经理" value="ar" />
              <el-option label="解决方案" value="sr" />
              <el-option label="交付经理" value="fr" />
              <el-option label="PDT经理" value="pdt" />
              <el-option label="CIO/IT" value="cio" />
            </el-select>
          </div>
        </template>
        <div class="book-list">
           <el-table :data="currentBookStats" style="width: 100%" size="small" :show-header="false" empty-text="暂无数据">
             <el-table-column type="index" width="40">
                <template #default="scope">
                   <span :class="['rank-index', 'rank-' + (scope.$index + 1)]">{{ scope.$index + 1 }}</span>
                </template>
             </el-table-column>
             <el-table-column prop="book_name" label="书名">
                <template #default="scope">
                   <span class="book-name">《{{ scope.row.book_name }}》</span>
                </template>
             </el-table-column>
             <el-table-column prop="count" label="次数" width="80" align="right">
                <template #default="scope">
                   <el-tag size="small" effect="plain">{{ scope.row.count }}次</el-tag>
                </template>
             </el-table-column>
           </el-table>
        </div>
      </el-card>
    </div>

    <el-card shadow="hover" class="activity-card">
      <template #header>
        <div class="card-header">
          <span>🕒 最近活跃记录</span>
        </div>
      </template>
      <div class="activity-list">
         <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in userStats.recent_activities"
              :key="index"
              :timestamp="formatDate(activity.created_at)"
              placement="top"
              :type="index === 0 ? 'primary' : ''"
            >
              <div class="activity-content">
                 <span class="user-highlight">{{ activity.username }}</span> 
                 使用了蓝图大师分析了文档
              </div>
            </el-timeline-item>
          </el-timeline>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getBookStats, getUserStats } from '../api/dashboard'

const rawBookStats = ref({})
const userStats = ref({
  total_users: 0,
  active_users: [],
  recent_activities: []
})
const selectedRankRole = ref('all')

const currentBookStats = computed(() => {
  return rawBookStats.value[selectedRankRole.value] || []
})

const fetchData = async () => {
  try {
    const bookRes = await getBookStats()
    rawBookStats.value = bookRes.data
    
    const userRes = await getUserStats()
    userStats.value = userRes.data
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 10px;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.user-stat-card {
  background: linear-gradient(135deg, #ffffff 0%, #f9faff 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.stat-value-container {
  text-align: center;
  padding: 15px 0;
}

.total-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.total-number {
  font-size: 42px;
  font-weight: bold;
  background: linear-gradient(45deg, #409EFF, #36cfc9);
  -webkit-background-clip: text;
  color: transparent;
  line-height: 1.2;
}

.active-users-section {
  text-align: left;
}

.section-title {
  font-size: 13px;
  font-weight: bold;
  color: #606266;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.section-title::before {
  content: '';
  display: block;
  width: 3px;
  height: 12px;
  background-color: #409EFF;
  border-radius: 2px;
}

.user-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.user-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.user-tag:hover {
  transform: scale(1.05);
}

.book-list {
  max-height: 300px;
  overflow-y: auto;
}

.book-name {
  font-weight: 500;
  color: #303133;
}

.rank-index {
  display: inline-block;
  width: 22px;
  height: 22px;
  line-height: 22px;
  text-align: center;
  border-radius: 6px;
  background-color: #f0f2f5;
  color: #909399;
  font-size: 12px;
  font-weight: bold;
}

.rank-1 {
  background: linear-gradient(135deg, #ff7875, #ff4d4f);
  color: white;
  box-shadow: 0 2px 6px rgba(255, 77, 79, 0.3);
}

.rank-2 {
  background: linear-gradient(135deg, #ffc069, #ffa940);
  color: white;
  box-shadow: 0 2px 6px rgba(255, 169, 64, 0.3);
}

.rank-3 {
  background: linear-gradient(135deg, #69c0ff, #409eff);
  color: white;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
}

.activity-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.activity-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 0 10px;
}

.activity-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.user-highlight {
  font-weight: 600;
  color: #409EFF;
  margin-right: 4px;
}

.empty-text {
  color: #909399;
  font-size: 13px;
  text-align: center;
  padding: 20px 0;
  background-color: #f9fafc;
  border-radius: 8px;
}

/* 滚动条美化 */
.book-list::-webkit-scrollbar,
.activity-list::-webkit-scrollbar {
  width: 6px;
}

.book-list::-webkit-scrollbar-thumb,
.activity-list::-webkit-scrollbar-thumb {
  background-color: #e4e7ed;
  border-radius: 3px;
}

.book-list::-webkit-scrollbar-track,
.activity-list::-webkit-scrollbar-track {
  background-color: transparent;
}
</style>