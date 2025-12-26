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
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.markmap-svg {
  width: 100%;
  height: 100%;
}

.toolbar {
  position: absolute;
  bottom: 20px;
  right: 20px;
}
</style>