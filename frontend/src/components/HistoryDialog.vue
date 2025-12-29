<template>
  <div class="history">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="按文件名/内容预览搜索"
        clearable
        class="search"
        @keyup.enter="fetchList(1)"
      />
      <el-button type="primary" :loading="loading" @click="fetchList(1)">刷新</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="filteredItems"
      size="small"
      style="width: 100%"
      empty-text="暂无历史记录"
      @row-click="handleRowClick"
    >
      <el-table-column prop="created_at" label="时间" width="170">
        <template #default="scope">
          <span>{{ formatTime(scope.row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="filename" label="文件" min-width="180" show-overflow-tooltip />
      <el-table-column prop="content_preview" label="摘要" min-width="260" show-overflow-tooltip />
      <el-table-column label="操作" width="160" align="right">
        <template #default="scope">
          <el-button link type="primary" @click.stop="openPreview(scope.row)">预览</el-button>
          <el-button link type="success" @click.stop="openToMain(scope.row)">打开</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        background
        layout="prev, pager, next, total"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @current-change="fetchList"
      />
    </div>

    <el-drawer v-model="previewVisible" title="分析历史预览" size="60%">
      <div class="drawer-body" v-loading="previewLoading">
        <div v-if="previewData" class="meta">
          <div class="meta-row">
            <span class="meta-key">文件</span>
            <span class="meta-val">{{ previewData.filename || '-' }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-key">时间</span>
            <span class="meta-val">{{ formatTime(previewData.created_at) }}</span>
          </div>
        </div>

        <el-divider />

        <pre class="content">{{ previewContent }}</pre>
      </div>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="previewVisible = false">关闭</el-button>
          <el-button type="success" :disabled="!previewData" @click="emitOpen(previewData, previewContent)">打开到主界面</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getAnalysisHistory, getAnalysisHistoryDetail } from '../api/blueprint'

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['open'])

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')

const previewVisible = ref(false)
const previewLoading = ref(false)
const previewData = ref(null)
const previewContent = ref('')

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return String(iso)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchList = async (toPage = page.value) => {
  if (!props.user || !props.user.user_id) return
  loading.value = true
  try {
    const res = await getAnalysisHistory(props.user.user_id, toPage, pageSize.value)
    items.value = (res.data && res.data.items) ? res.data.items : []
    total.value = (res.data && typeof res.data.total === 'number') ? res.data.total : 0
    page.value = (res.data && res.data.page) ? res.data.page : toPage
  } catch (e) {
    ElMessage.error(`获取历史失败：${e.message || e}`)
  } finally {
    loading.value = false
  }
}

const filteredItems = computed(() => {
  const k = (keyword.value || '').trim().toLowerCase()
  if (!k) return items.value
  return items.value.filter((it) => {
    const f = (it.filename || '').toLowerCase()
    const p = (it.content_preview || '').toLowerCase()
    return f.includes(k) || p.includes(k)
  })
})

const fetchDetail = async (row) => {
  if (!props.user || !props.user.user_id) return null
  previewLoading.value = true
  try {
    const res = await getAnalysisHistoryDetail(props.user.user_id, row.id)
    return res.data || null
  } catch (e) {
    ElMessage.error(`获取详情失败：${e.message || e}`)
    return null
  } finally {
    previewLoading.value = false
  }
}

const openPreview = async (row) => {
  previewVisible.value = true
  previewData.value = null
  previewContent.value = ''
  const detail = await fetchDetail(row)
  if (!detail) return
  previewData.value = detail
  previewContent.value = detail.content || ''
}

const emitOpen = (row, content) => {
  emit('open', { row, content })
  previewVisible.value = false
}

const openToMain = async (row) => {
  const detail = await fetchDetail(row)
  if (!detail) return
  emitOpen(detail, detail.content || '')
}

const handleRowClick = (row) => {
  openPreview(row)
}

watch(
  () => props.user && props.user.user_id,
  () => {
    fetchList(1)
  }
)

onMounted(() => {
  fetchList(1)
})
</script>

<style scoped>
.history {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search {
  flex: 1 1 auto;
}

.pager {
  display: flex;
  justify-content: flex-end;
}

.drawer-body {
  min-height: 200px;
}

.meta {
  display: grid;
  gap: 6px;
}

.meta-row {
  display: grid;
  grid-template-columns: 70px 1fr;
  gap: 10px;
  align-items: center;
}

.meta-key {
  color: #909399;
}

.meta-val {
  color: #303133;
  word-break: break-all;
}

.content {
  white-space: pre-wrap;
  word-break: break-word;
  background: #0b1220;
  color: #e5e7eb;
  border-radius: 10px;
  padding: 12px 14px;
  line-height: 1.6;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 12px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

