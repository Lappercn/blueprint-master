<template>
  <div class="mindmap-container">
    <svg ref="svgRef" class="markmap-svg"></svg>
    <div class="toolbar" ref="toolbarRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'
import { Toolbar } from 'markmap-toolbar'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const svgRef = ref(null)
const toolbarRef = ref(null)
let mm = null
const transformer = new Transformer()
let isFirstRender = true

const debounce = (fn, delay) => {
  let timer = null
  return (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn(...args)
    }, delay)
  }
}

const updateMindmap = () => {
  if (!mm || !props.content) return
  
  try {
    const { root } = transformer.transform(props.content)
    mm.setData(root)
    
    if (isFirstRender) {
      mm.fit()
      isFirstRender = false
    }
  } catch (error) {
    console.warn('Mindmap render skipped due to incomplete markdown:', error)
  }
}

const debouncedUpdate = debounce(updateMindmap, 200)

onMounted(() => {
  if (svgRef.value) {
    mm = Markmap.create(svgRef.value, {
      autoFit: false, // 禁用自动缩放，由代码控制
      duration: 0, // 禁用动画以提高流式渲染性能
      zoom: true,
      pan: true
    })
    
    if (toolbarRef.value) {
        const toolbar = Toolbar.create(mm)
        toolbar.setBrand(false)
        toolbarRef.value.append(toolbar.el)
    }
    updateMindmap()
  }
})

onUnmounted(() => {
  if (mm) {
    mm.destroy()
    mm = null
  }
})

watch(() => props.content, () => {
  debouncedUpdate()
})

// 当加载结束时，重新适配视图，防止视图停留在初始状态
watch(() => props.loading, (newVal) => {
  if (newVal === false && mm) {
    setTimeout(() => {
        mm.fit()
    }, 300) // 稍作延迟确保渲染完成
  }
})
</script>

<style scoped>
.mindmap-container {
  width: 100%;
  height: 600px;
  position: relative;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f9fafc;
}

.markmap-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.toolbar {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 4px;
  z-index: 10;
}

/* 覆盖 markmap toolbar 默认样式（如果有必要，通常 markmap 自身样式已足够，这里主要做容器美化） */
:deep(.mm-toolbar-brand) {
  display: none;
}

:deep(.mm-toolbar-item) {
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
  border-radius: 4px;
  cursor: pointer;
  color: #606266;
  transition: all 0.2s;
}

:deep(.mm-toolbar-item:hover) {
  background-color: #ecf5ff;
  color: #409eff;
}
</style>