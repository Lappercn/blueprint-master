<template>
  <el-card shadow="hover" class="popular-books-card">
    <template #header>
      <div class="header">
        <span class="title">📚 热门书籍</span>
        <el-tag size="small" effect="plain" type="info">总榜</el-tag>
      </div>
    </template>

    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <el-empty v-else-if="books.length === 0" description="暂无数据" />

    <div v-else class="list">
      <div v-for="(b, idx) in books" :key="b.book_name + idx" class="row">
        <div :class="['rank', idx < 3 ? 'rank-top' : '']">{{ idx + 1 }}</div>
        <div class="name">《{{ b.book_name }}》</div>
        <el-tag size="small" effect="plain">{{ b.count }}次</el-tag>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getBookStats } from '../api/dashboard'

const loading = ref(true)
const books = ref([])

const fetchBooks = async () => {
  loading.value = true
  try {
    const res = await getBookStats()
    books.value = (res && res.data && res.data.all) ? res.data.all.slice(0, 5) : []
  } catch (e) {
    books.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.popular-books-card {
  border-radius: 12px;
  border: none;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 600;
  color: #303133;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rank {
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  border-radius: 8px;
  background: #f2f3f5;
  color: #606266;
  font-weight: 700;
  font-size: 12px;
  flex: 0 0 auto;
}

.rank.rank-top {
  background: linear-gradient(135deg, #409eff 0%, #36cfc9 100%);
  color: #ffffff;
}

.name {
  flex: 1 1 auto;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  color: #303133;
  font-weight: 500;
}

.loading {
  padding: 4px 0;
}
</style>
