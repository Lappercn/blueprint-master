<template>
  <div class="app-container">
    <el-container class="main-layout">
      <!-- 侧边栏/头部 -->
      <el-header class="header">
        <div class="header-content">
          <div class="logo">
            <div class="logo-icon">
              <el-icon :size="24"><Monitor /></el-icon>
            </div>
            <div class="logo-text">
              <h1>蓝图大师</h1>
              <span class="subtitle">Blueprint Master</span>
            </div>
          </div>
          <div class="header-right">
             <div class="user-info" v-if="currentUser">
               <span class="username">欢迎, {{ currentUser.username }}</span>
               <el-button type="warning" link @click="showDashboardDialog = true">
                 <el-icon><DataLine /></el-icon> 看板
               </el-button>
               <el-button type="primary" link @click="showFeedbackDialog = true">
                 <el-icon><ChatDotSquare /></el-icon> 反馈
               </el-button>
             </div>
             <div class="header-tags desktop-only" v-else>
               <el-tag type="danger" effect="dark" size="small">Huawei Methodology</el-tag>
               <el-tag type="warning" effect="dark" size="small">Alibaba Middle Platform</el-tag>
               <el-tag type="primary" effect="dark" size="small">ByteDance Data-Driven</el-tag>
             </div>
          </div>
        </div>
      </el-header>

      <el-main class="main-content">
        <div class="content-wrapper">
          <!-- 上传与输入区域 -->
          <transition name="fade-slide" mode="out-in">
            <div class="input-panel" v-if="!analyzing && !result">
              <div class="hero-text">
                <h2>数字化转型，从一份靠谱的蓝图开始</h2>
                <p>上传文档进行深度评审，或输入需求直接生成蓝图方案</p>
              </div>

              <el-card class="upload-card" shadow="hover">
                <!-- 模式切换 -->
                <el-tabs v-model="activeMode" class="mode-tabs" stretch>
                  <el-tab-pane label="文档评审 (Analysis)" name="analysis">
                    <!-- 文件选择状态 -->
                    <div v-if="currentFile" class="file-selected-state">
                      <div class="file-info">
                        <el-icon :size="40" color="#409EFF"><Document /></el-icon>
                        <div class="file-details">
                          <h3>{{ currentFile.name }}</h3>
                          <p>{{ (currentFile.size / 1024 / 1024).toFixed(2) }} MB</p>
                        </div>
                        <el-button type="danger" link @click="clearCurrentFile">
                           <el-icon><CircleClose /></el-icon>
                        </el-button>
                      </div>
                      
                      <div class="action-buttons">
                        <div class="action-card" @click="startAnalysis(currentFile)">
                            <div class="action-icon action-icon-report">
                                <el-icon><ChatLineRound /></el-icon>
                            </div>
                            <div class="action-content">
                                <h4>大师深度评审</h4>
                                <p>生成详细的图文分析报告</p>
                            </div>
                            <el-icon class="arrow-icon"><ArrowRight /></el-icon>
                        </div>

                        <div class="action-card" @click="startDiagnosisMindmap">
                            <div class="action-icon action-icon-mindmap">
                                <el-icon><Connection /></el-icon>
                            </div>
                            <div class="action-content">
                                <h4>诊断架构图</h4>
                                <p>直接生成蓝图结构与问题标注</p>
                            </div>
                            <el-icon class="arrow-icon"><ArrowRight /></el-icon>
                        </div>

                        <div class="action-card" @click="startSmartMindmap">
                            <div class="action-icon action-icon-smart">
                                <el-icon><MagicStick /></el-icon>
                            </div>
                            <div class="action-content">
                                <h4>智能绘图</h4>
                                <p>AI 帮你梳理文档逻辑为思维导图</p>
                            </div>
                            <el-icon class="arrow-icon"><ArrowRight /></el-icon>
                        </div>
                      </div>
                    </div>

                    <!-- 初始上传状态 -->
                    <div v-else>
                        <div class="custom-prompt-section">
                          <div class="section-label-row">
                            <div class="section-label">
                              <el-icon><ChatLineRound /></el-icon>
                              <span>大师，我想说... (可选)</span>
                            </div>
                          </div>
                          <el-input
                            v-model="customPrompt"
                            type="textarea"
                            :rows="3"
                            placeholder="例如：这是针对一家传统制造业工厂的蓝图，请重点评估其工业互联网平台的落地性..."
                            class="custom-prompt-input"
                            resize="none"
                          />
                        </div>

                        <el-upload
                          class="upload-area"
                          drag
                          action="#"
                          :auto-upload="false"
                          :on-change="handleFileChange"
                          :show-file-list="false"
                        >
                          <div class="upload-content">
                            <el-icon class="el-icon--upload" :size="60"><upload-filled /></el-icon>
                            <div class="upload-text">
                              <h3>点击或拖拽上传蓝图文档</h3>
                              <p>支持 PDF, Word, JPG, PNG 等格式</p>
                            </div>
                          </div>
                        </el-upload>
                    </div>
                  </el-tab-pane>

                  <el-tab-pane label="方案生成 (Generation)" name="generation">
                    <el-tabs v-model="generationMode" class="mode-tabs" stretch>
                      <el-tab-pane label="从需求生成" name="from_needs">
                        <div class="generation-form">
                          <div class="form-item">
                            <div class="section-label-row">
                              <div class="section-label">
                                <el-icon><Aim /></el-icon>
                                <span>客户需求 (Client Needs)</span>
                              </div>
                            </div>
                            <el-input
                              v-model="clientNeeds"
                              type="textarea"
                              :rows="4"
                              placeholder="例如：客户是一家连锁餐饮企业，希望建立一套会员数字化营销系统，提升复购率..."
                              resize="none"
                            />
                          </div>

                          <div class="form-item">
                            <div class="section-label-row">
                              <div class="section-label">
                                <el-icon><Opportunity /></el-icon>
                                <span>我的想法/参考资料 (My Ideas)</span>
                              </div>
                            </div>
                            <el-input
                              v-model="userIdeas"
                              type="textarea"
                              :rows="4"
                              placeholder="例如：我觉得可以参考星巴克的会员体系；或者我有以下几点初步构思..."
                              resize="none"
                            />

                            <div style="margin-top: 12px;">
                              <div v-if="referenceFile" class="file-selected-state">
                                <div class="file-info">
                                  <el-icon :size="40" color="#409EFF"><Document /></el-icon>
                                  <div class="file-details">
                                    <h3>{{ referenceFile.name }}</h3>
                                    <p>{{ (referenceFile.size / 1024 / 1024).toFixed(2) }} MB</p>
                                  </div>
                                  <el-button type="danger" link @click="clearReferenceFile">
                                    <el-icon><CircleClose /></el-icon>
                                  </el-button>
                                </div>
                              </div>
                              <el-upload
                                v-else
                                class="upload-area"
                                drag
                                action="#"
                                :auto-upload="false"
                                :on-change="handleReferenceFileChange"
                                :show-file-list="false"
                              >
                                <div class="upload-content">
                                  <el-icon class="el-icon--upload" :size="60"><upload-filled /></el-icon>
                                  <div class="upload-text">
                                    <h3>点击或拖拽上传参考资料（可选）</h3>
                                    <p>支持 PDF, Word, JPG, PNG 等格式</p>
                                  </div>
                                </div>
                              </el-upload>
                            </div>
                          </div>
                        </div>
                      </el-tab-pane>

                      <el-tab-pane label="生成子方案" name="from_parent">
                        <div class="generation-form">
                          <div class="form-item">
                            <div class="section-label-row">
                              <div class="section-label">
                                <el-icon><Document /></el-icon>
                                <span>父方案文档 (Parent Plan)</span>
                              </div>
                            </div>

                            <div v-if="parentPlanFile" class="file-selected-state">
                              <div class="file-info">
                                <el-icon :size="40" color="#409EFF"><Document /></el-icon>
                                <div class="file-details">
                                  <h3>{{ parentPlanFile.name }}</h3>
                                  <p>{{ (parentPlanFile.size / 1024 / 1024).toFixed(2) }} MB</p>
                                </div>
                                <el-button type="danger" link @click="clearParentPlanFile">
                                  <el-icon><CircleClose /></el-icon>
                                </el-button>
                              </div>
                            </div>
                            <el-upload
                              v-else
                              class="upload-area"
                              drag
                              action="#"
                              :auto-upload="false"
                              :on-change="handleParentPlanFileChange"
                              :show-file-list="false"
                            >
                              <div class="upload-content">
                                <el-icon class="el-icon--upload" :size="60"><upload-filled /></el-icon>
                                <div class="upload-text">
                                  <h3>点击或拖拽上传父方案文档</h3>
                                  <p>支持 PDF, Word, JPG, PNG 等格式</p>
                                </div>
                              </div>
                            </el-upload>
                          </div>

                          <div class="form-item">
                            <div class="section-label-row">
                              <div class="section-label">
                                <el-icon><Aim /></el-icon>
                                <span>要生成的子专项/子方案 (Sub Plan)</span>
                              </div>
                            </div>
                            <el-input v-model="subPlanTitle" placeholder="例如：会员体系子方案 / 数据中台子专项 / CRM子方案..." />
                          </div>

                          <div class="form-item">
                            <div class="section-label-row">
                              <div class="section-label">
                                <el-icon><Opportunity /></el-icon>
                                <span>初步想法与范围 (Details)</span>
                              </div>
                            </div>
                            <el-alert
                              type="info"
                              show-icon
                              :closable="false"
                              title="建议描述更详细：涉及的流程、部门、角色、系统、接口、数据口径、里程碑、约束条件等"
                              style="margin-bottom: 10px;"
                            />
                            <el-input
                              v-model="subPlanDetails"
                              type="textarea"
                              :rows="6"
                              placeholder="例如：\n1) 覆盖门店-总部-供应链的会员拉新/促活/复购流程\n2) 涉及部门：市场部、运营部、IT部、财务部\n3) 涉及系统：POS、CRM、营销自动化、数据仓库\n4) 关键指标：复购率、客单价、会员渗透率\n5) 约束：3个月上线、预算50万、门店网络不稳定..."
                              resize="none"
                            />
                          </div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </el-tab-pane>
                </el-tabs>

                <div class="common-settings">
                    <div class="divider-dashed"></div>
                    
                    <div class="methodology-section">
                      <div class="role-selector-section">
                         <div class="section-label-row">
                          <div class="section-label">
                            <el-icon><User /></el-icon>
                            <span>我是谁？(点击角色自动匹配场景)</span>
                          </div>
                        </div>
                        <el-radio-group v-model="selectedRole" @change="handleRoleChange" class="role-group">
                          <el-radio-button v-for="(cfg, key) in rolePresets" :key="key" :label="key" :value="key">
                            <div class="role-item">
                              <span class="role-name">{{ cfg.label }}</span>
                            </div>
                          </el-radio-button>
                        </el-radio-group>
                      </div>

                      <div class="section-label-row" style="margin-top: 15px;">
                        <div class="section-label">
                          <el-icon><Collection /></el-icon>
                          <span>已选方法论/依据（可手动微调）</span>
                        </div>
                      </div>
                        
                      <el-cascader
                          v-model="selectedMethodologies"
                          :options="methodologyOptions"
                          :props="cascaderProps"
                          placeholder="请选择评审场景或营销理论"
                          class="methodology-cascader"
                          clearable
                          collapse-tags
                          collapse-tags-tooltip
                        >
                          <template #default="{ node, data }">
                            <span>{{ data.label }}</span>
                            <span v-if="!node.isLeaf" style="color: #999; font-size: 12px; margin-left: 5px;">({{ data.children.length }})</span>
                          </template>
                        </el-cascader>
                        
                        <div class="custom-methodology-input">
                        <el-input
                          v-model="newCustomMethodology"
                          placeholder="输入自定义参考书籍 (如: 《定位》、《增长黑客》...)"
                          class="input-with-select"
                          @keyup.enter="addCustomMethodology"
                        >
                          <template #append>
                            <el-button @click="addCustomMethodology">
                              <el-icon><Plus /></el-icon> 添加书籍
                            </el-button>
                          </template>
                        </el-input>
                      </div>
                      
                      <div class="custom-methodology-tags" v-if="customMethodologies.length > 0">
                        <el-tag
                          v-for="tag in customMethodologies"
                          :key="tag"
                          closable
                          :disable-transitions="false"
                          @close="removeCustomMethodology(tag)"
                          class="custom-tag"
                          effect="plain"
                        >
                          <el-icon><Notebook /></el-icon> {{ tag }}
                        </el-tag>
                      </div>
                    </div>
                </div>

                <div class="action-footer" v-if="activeMode === 'generation'">
                   <el-button v-if="generationMode === 'from_needs'" type="primary" size="large" @click="startProposalGeneration" class="generate-btn">
                     <el-icon><MagicStick /></el-icon> 生成蓝图方案
                   </el-button>
                   <el-button v-else type="primary" size="large" @click="startSubProposalGeneration" class="generate-btn">
                     <el-icon><MagicStick /></el-icon> 生成子方案
                   </el-button>
                </div>
              </el-card>
            </div>

            <!-- 分析结果展示区域 -->
            <div class="result-panel" v-else>
              <div class="result-header">
                <div class="status-badge" :class="{ 'analyzing': analyzing }">
                  <span v-if="analyzing" class="status-text">
                    <el-icon class="is-loading"><Loading /></el-icon> 深度思考中...
                    <el-button link type="danger" size="small" @click="stopAnalysis" style="margin-left: 10px;">
                      <el-icon><VideoPause /></el-icon> 停止
                    </el-button>
                  </span>
                  <span v-else class="status-text">
                    <el-icon><CircleCheckFilled /></el-icon> 评审完成
                  </span>
                </div>
                <div class="actions">
                  <el-button @click="reset" :disabled="analyzing" plain size="small" class="action-btn">
                    <el-icon><RefreshLeft /></el-icon> <span class="btn-text">重新评审</span>
                  </el-button>
                  <el-button type="warning" @click="handleGenerateMindmap" :disabled="analyzing || !result" size="small" class="action-btn">
                    <el-icon><Connection /></el-icon> <span class="btn-text">{{ activeMode === 'analysis' ? '生成整改导图' : '生成方案导图' }}</span>
                  </el-button>
                  <el-button type="success" @click="handleExportDocx" :disabled="analyzing || !result || exporting" :loading="exporting" size="small" class="action-btn">
                    <el-icon><Document /></el-icon> <span class="btn-text">导出 Word</span>
                  </el-button>
                  <el-button type="primary" @click="exportMarkdown" :disabled="analyzing || !result" size="small" class="action-btn">
                    <el-icon><Download /></el-icon> <span class="btn-text">导出 MD</span>
                  </el-button>
                </div>
              </div>

              <div class="markdown-container" :class="{ 'paper-mode': activeMode === 'generation' }">
                <div v-if="!result && analyzing" class="skeleton-loader">
                  <el-skeleton :rows="10" animated />
                  <div class="loading-tips">
                    <p>正在解析文档内容...</p>
                    <p>正在构建基于您选择的方法论的评审框架...</p>
                    <p>大师正在深度思考...</p>
                  </div>
                </div>
                
                <div class="markdown-paper" :class="{ 'paper-mode': activeMode === 'generation' }">
                  <div class="markdown-body" v-html="renderedMarkdown" ref="markdownContent"></div>
                </div>
                
                <div v-if="analyzing && result" class="streaming-cursor">
                  <span class="cursor"></span>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </el-main>

      <el-footer class="site-footer">
        <div class="site-footer-content">
          <div class="site-footer-left">
            <span>官网：</span>
            <a href="https://tongzhilian.cn" target="_blank" rel="noopener noreferrer">tongzhilian.cn</a>
            <span class="separator">·</span>
            <span>邮箱：</span>
            <a href="mailto:shibaizhelianmeng@163.com">shibaizhelianmeng@163.com</a>
          </div>
          <div class="site-footer-right">欢迎更多人加入我们</div>
        </div>
      </el-footer>
    </el-container>

    <!-- 思维导图弹窗 -->
    <el-dialog
      v-model="showMindmapDialog"
      :title="mindmapDialogTitle"
      width="95%"
      class="responsive-dialog mindmap-dialog"
      align-center
      destroy-on-close
    >
      <div v-loading="generatingMindmap" :element-loading-text="mindmapLoadingText">
         <MindMapViewer :content="mindmapContent" :loading="generatingMindmap" style="height: 70vh;" />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showMindmapDialog = false">关闭</el-button>
          <el-button type="primary" @click="downloadMindmapImage">
             <el-icon><Picture /></el-icon> 下载图片
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 登录弹窗 -->
    <el-dialog
      v-model="showLoginDialog"
      title="欢迎使用蓝图大师"
      width="90%"
      class="responsive-dialog small-dialog login-dialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      align-center
    >
      <div class="login-content">
        <p class="login-desc">请输入您的中文姓名以开始使用，系统将自动绑定您的设备。</p>
        <el-input 
          v-model="loginUsername" 
          placeholder="请输入中文姓名" 
          :prefix-icon="User"
          @keyup.enter="handleLogin"
        />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="handleLogin" :loading="loginLoading" style="width: 100%">
            开始使用
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 仪表盘弹窗 -->
    <el-dialog
      v-model="showDashboardDialog"
      title="数据看板"
      width="90%"
      class="responsive-dialog"
      align-center
    >
      <Dashboard v-if="showDashboardDialog" />
    </el-dialog>

    <!-- 反馈弹窗 -->
    <el-dialog
      v-model="showFeedbackDialog"
      title="意见反馈"
      width="90%"
      class="responsive-dialog small-dialog"
      align-center
    >
      <el-input
        v-model="feedbackContent"
        type="textarea"
        :rows="5"
        placeholder="请告诉我们您的建议或遇到的问题..."
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showFeedbackDialog = false">取消</el-button>
          <el-button type="primary" @click="handleFeedback" :loading="feedbackLoading">
            提交反馈
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { UploadFilled, Monitor, Loading, ChatLineRound, RefreshLeft, Download, CircleCheckFilled, Collection, Plus, User, ChatDotSquare, SwitchButton, Document, VideoPause, Notebook, DataLine, Connection, CircleClose, ArrowRight, Picture, MagicStick, Aim, Opportunity } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownIt from 'markdown-it'
import mermaid from 'mermaid'
import html2canvas from 'html2canvas'
import FingerprintJS from '@fingerprintjs/fingerprintjs'
import { analyzeBlueprintStream, exportDocx, generateMindmapStream, analyzeBlueprintToMindmapStream, generateSmartMindmapStream, generateProposalStream, generateSubProposalStream } from './api/blueprint'
import { login } from './api/auth'
import { submitFeedback } from './api/feedback'
import Dashboard from './components/Dashboard.vue'
import MindMapViewer from './components/MindMapViewer.vue'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// 状态
const analyzing = ref(false)
const result = ref('')
const customPrompt = ref('')
// 默认选中华为的战略层
const selectedMethodologies = ref([['huawei', 'strategy']])
const newCustomMethodology = ref('')
const customMethodologies = ref([])
const exporting = ref(false)
const abortController = ref(null)
const selectedRole = ref('')
const showMindmapDialog = ref(false)
const mindmapContent = ref('')
const generatingMindmap = ref(false)
const currentFile = ref(null)
const referenceFile = ref(null)
const markdownContent = ref(null)

// 新增状态
const activeMode = ref('analysis')
const generationMode = ref('from_needs')
const clientNeeds = ref('')
const userIdeas = ref('')
const parentPlanFile = ref(null)
const subPlanTitle = ref('')
const subPlanDetails = ref('')
const mindmapPurpose = ref('')

const hasMethodologyBasis = computed(() => {
  return selectedMethodologies.value.length > 0 || customMethodologies.value.length > 0
})

const ensureMethodologyBasis = (message) => {
  if (!hasMethodologyBasis.value) {
    ElMessage.warning(message)
    return false
  }
  return true
}

const mindmapDialogTitle = computed(() => {
  if (mindmapPurpose.value === 'analysis') return '整改行动思维导图'
  if (mindmapPurpose.value === 'diagnosis') return '诊断架构图'
  if (mindmapPurpose.value === 'smart') return '智能思维导图'
  if (mindmapPurpose.value === 'sub_proposal') return '子方案思维导图'
  if (mindmapPurpose.value === 'proposal') return '方案思维导图'
  return '思维导图'
})

const mindmapLoadingText = computed(() => {
  if (mindmapPurpose.value === 'analysis') return '大师正在为您规划整改路径...'
  if (mindmapPurpose.value === 'diagnosis') return '大师正在为您扫描蓝图结构...'
  if (mindmapPurpose.value === 'smart') return '大师正在为您梳理文档逻辑...'
  return '大师正在为您梳理方案结构...'
})

const mindmapDownloadName = computed(() => {
  if (mindmapPurpose.value === 'analysis') return '蓝图大师整改导图.png'
  if (mindmapPurpose.value === 'diagnosis') return '蓝图诊断架构图.png'
  if (mindmapPurpose.value === 'smart') return '蓝图智能导图.png'
  if (mindmapPurpose.value === 'sub_proposal') {
    const name = subPlanTitle.value && subPlanTitle.value.trim() ? subPlanTitle.value.trim() : '子方案'
    return `${name}-思维导图.png`
  }
  return '蓝图大师方案导图.png'
})

// 角色预设配置
const rolePresets = {
  'cxo': {
    label: 'CEO/高管 (CXO)',
    desc: '关注战略落地与数字化转型',
    presets: [['huawei', 'strategy'], ['huawei', 'digital_transformation']]
  },
  'ar': {
    label: '客户经理 (AR)',
    desc: '铁三角-客户关系负责',
    presets: [['huawei', 'marketing'], ['huawei', 'project_delivery']]
  },
  'sr': {
    label: '解决方案专家 (SR)',
    desc: '铁三角-方案与技术负责',
    presets: [['huawei', 'project_delivery'], ['huawei', 'product_dev']]
  },
  'fr': {
    label: '交付经理 (FR)',
    desc: '铁三角-项目交付与履约',
    presets: [['huawei', 'project_delivery'], ['huawei', 'issue_mgmt']]
  },
  'pdt': {
    label: 'PDT经理 (Product)',
    desc: '关注产品全生命周期管理',
    presets: [['huawei', 'product_dev']]
  },
  'cfo': {
    label: 'CFO/财经 (Finance)',
    desc: '关注全面预算与业财融合',
    presets: [['huawei', 'finance_mgmt']]
  },
  'supply': {
    label: '供应链 (Supply Chain)',
    desc: '关注计划/采购/制造流程',
    presets: [['huawei', 'issue_mgmt']] // 暂时映射到ITR，后续可扩展ISC
  },
  'hr': {
    label: 'HR/政委 (HR)',
    desc: '关注组织与人才发展',
    presets: [['huawei', 'strategy']] // 暂时映射到BLM中的组织部分
  },
  'cio': {
    label: 'CIO/IT总监',
    desc: '关注技术架构与标准规范',
    presets: [['huawei', 'digital_transformation'], ['general', 'enterprise_arch']]
  }
}

const handleRoleChange = (role) => {
  if (role && rolePresets[role]) {
    selectedMethodologies.value = rolePresets[role].presets
    // 自动更新 selectedRole 状态
    selectedRole.value = role
    ElMessage.success(`已切换至【${rolePresets[role].label}】评审视角`)
  }
}

// 级联选择器配置
const cascaderProps = { multiple: true, emitPath: true }
const methodologyOptions = [
  {
    value: 'huawei',
    label: '华为 (Huawei)',
    children: [
      { value: 'strategy', label: '战略规划层 (BLM/BEM) - 参考《价值为纲》' },
      { value: 'finance_mgmt', label: '财经管理层 (IFS) - 参考《华为财经密码》' },
      { value: 'marketing', label: '市场营销层 (MTL) - 参考《华为营销法》' },
      { value: 'project_delivery', label: '项目交付/销售层 (LTC) - 参考《华为铁三角》' },
      { value: 'product_dev', label: '产品研发层 (IPD) - 参考《华为研发》' },
      { value: 'issue_mgmt', label: '问题到解决层 (ITR) - 售后与运维' },
      { value: 'digital_transformation', label: '数字化转型层 (Digital) - 参考《数字化转型之道》' }
    ]
  },
  {
    value: 'advertising',
    label: '广告营销大师 (Advertising)',
    children: [
        { value: 'positioning', label: '定位理论 (Positioning) - 特劳特/里斯' },
        { value: 'integrated_marketing', label: '整合营销 (IMC) - 舒尔茨' },
        { value: 'creative', label: '创意与文案 (Ogilvy) - 奥格威' },
        { value: 'growth_hacking', label: '增长黑客 (Growth Hacking)' }
    ]
  },
  {
    value: 'general',
    label: '通用/行业标准 (General)',
    children: [
      { value: 'enterprise_arch', label: '企业架构层 (TOGAF) - 参考《TOGAF标准》' },
      { value: 'it_management', label: 'IT服务与管理层 (ITIL/DevOps)' },
      { value: 'project_management', label: '项目管理层 (PMP/Agile)' }
    ]
  }
]

// 用户相关状态
const currentUser = ref(null)
const showLoginDialog = ref(false)
const loginUsername = ref('')
const loginLoading = ref(false)

// 反馈相关状态
const showFeedbackDialog = ref(false)
const feedbackContent = ref('')
const feedbackLoading = ref(false)

// 仪表盘状态
const showDashboardDialog = ref(false)

const renderedMarkdown = computed(() => {
  return md.render(result.value)
})

let mermaidSeq = 0

const renderMermaidInMarkdown = async () => {
  if (!markdownContent.value) return
  await nextTick()

  const container = markdownContent.value
  const codeBlocks = Array.from(container.querySelectorAll('pre > code'))

  const targets = codeBlocks
    .map((code) => {
      const pre = code.parentElement
      if (!pre) return null
      if (pre.dataset.mermaidRendered === '1') return null

      const lang = (code.className || '').toLowerCase()
      const text = (code.textContent || '').trim()

      const isMermaidFence = lang.includes('language-mermaid')
      const looksLikeMermaid =
        text.startsWith('graph ') ||
        text.startsWith('flowchart ') ||
        text.startsWith('sequenceDiagram') ||
        text.startsWith('classDiagram') ||
        text.startsWith('stateDiagram') ||
        text.startsWith('erDiagram') ||
        text.startsWith('journey') ||
        text.startsWith('gantt') ||
        text.startsWith('mindmap') ||
        text.startsWith('timeline')

      if (!isMermaidFence && !looksLikeMermaid) return null

      return { pre, text }
    })
    .filter(Boolean)

  if (targets.length === 0) return

  for (const { pre, text } of targets) {
    try {
      const id = `mermaid-${Date.now()}-${mermaidSeq++}`
      const { svg, bindFunctions } = await mermaid.render(id, text)
      const wrapper = document.createElement('div')
      wrapper.className = 'mermaid-rendered'
      wrapper.innerHTML = svg
      if (bindFunctions) bindFunctions(wrapper)
      pre.replaceWith(wrapper)
    } catch (e) {
      pre.dataset.mermaidRendered = '0'
    }
  }
}

const debounce = (fn, delay) => {
  let timer = null
  return (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

const debouncedRenderMermaidInMarkdown = debounce(renderMermaidInMarkdown, 200)

onMounted(() => {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    theme: 'default'
  })

  const storedUser = localStorage.getItem('blueprint_user')
  if (storedUser) {
    currentUser.value = JSON.parse(storedUser)
  } else {
    showLoginDialog.value = true
  }
})

watch(renderedMarkdown, () => {
  debouncedRenderMermaidInMarkdown()
})

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？退出后将需要重新输入姓名登录。',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      localStorage.removeItem('blueprint_user')
      currentUser.value = null
      showLoginDialog.value = true
      ElMessage.success('已退出登录')
    })
    .catch(() => {})
}

// 登录逻辑
const handleLogin = async () => {
  if (!loginUsername.value.trim()) {
    ElMessage.warning('请输入中文姓名')
    return
  }

  loginLoading.value = true
  try {
    const fp = await FingerprintJS.load()
    const result = await fp.get()
    const fingerprint = result.visitorId

    const response = await login(loginUsername.value, fingerprint)
    
    currentUser.value = response.data
    localStorage.setItem('blueprint_user', JSON.stringify(response.data))
    showLoginDialog.value = false
    ElMessage.success('登录成功')
  } catch (error) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loginLoading.value = false
  }
}

// 反馈逻辑
const handleFeedback = async () => {
  if (!feedbackContent.value.trim()) {
    ElMessage.warning('请输入反馈内容')
    return
  }

  feedbackLoading.value = true
  try {
    await submitFeedback(
      currentUser.value.user_id,
      currentUser.value.username,
      feedbackContent.value
    )
    ElMessage.success('感谢您的反馈！')
    showFeedbackDialog.value = false
    feedbackContent.value = ''
  } catch (error) {
    ElMessage.error(error.message || '提交失败')
  } finally {
    feedbackLoading.value = false
  }
}

const addCustomMethodology = () => {
  const val = newCustomMethodology.value.trim()
  if (val) {
    if (!customMethodologies.value.includes(val)) {
      customMethodologies.value.push(val)
      newCustomMethodology.value = ''
    } else {
      ElMessage.warning('该方法论已添加')
    }
  }
}

const removeCustomMethodology = (tag) => {
  customMethodologies.value = customMethodologies.value.filter(m => m !== tag)
}

const stopAnalysis = () => {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
    analyzing.value = false
    ElMessage.info('已停止生成')
  }
}

const handleFileChange = (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  
  // 保存当前文件，但不立即开始分析
  currentFile.value = file
  ElMessage.success(`已选择文件: ${file.name}`)
}

const clearCurrentFile = () => {
  currentFile.value = null
  result.value = ''
  analyzing.value = false
}

const handleReferenceFileChange = (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  referenceFile.value = file
  ElMessage.success(`已选择参考资料: ${file.name}`)
}

const clearReferenceFile = () => {
  referenceFile.value = null
}

const handleParentPlanFileChange = (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  parentPlanFile.value = file
  ElMessage.success(`已选择父方案: ${file.name}`)
}

const clearParentPlanFile = () => {
  parentPlanFile.value = null
}

const startDiagnosisMindmap = async () => {
  if (!currentFile.value) return
  if (!ensureMethodologyBasis('请至少选择系统内置方法论或添加书籍作为评审依据')) return
  if (!currentUser.value) {
    showLoginDialog.value = true
    return
  }

  mindmapPurpose.value = 'diagnosis'
  showMindmapDialog.value = true
  mindmapContent.value = ''
  generatingMindmap.value = true
  
  // 初始占位符
  mindmapContent.value = '# 🚀 正在扫描蓝图结构...'
  
  try {
    let isFirstChunk = true
    await analyzeBlueprintToMindmapStream(
      currentFile.value,
      (chunk) => {
        if (isFirstChunk) {
            mindmapContent.value = chunk
            isFirstChunk = false
        } else {
            mindmapContent.value += chunk
        }
      },
      (error) => {
        ElMessage.error('生成诊断导图失败: ' + error.message)
        generatingMindmap.value = false
        mindmapContent.value = '# ❌ 生成失败\n请重试'
      },
      () => {
        generatingMindmap.value = false
        if (!mindmapContent.value || mindmapContent.value === '# 🚀 正在扫描蓝图结构...') {
            mindmapContent.value = '# 暂无内容'
        }
      }
    )
  } catch (error) {
    console.error('Diagnosis Mindmap error:', error)
    generatingMindmap.value = false
  }
}

const startSmartMindmap = async () => {
  if (!currentFile.value) return
  if (!ensureMethodologyBasis('请至少选择系统内置方法论或添加书籍作为评审依据')) return
  if (!currentUser.value) {
    showLoginDialog.value = true
    return
  }

  mindmapPurpose.value = 'smart'
  showMindmapDialog.value = true
  mindmapContent.value = ''
  generatingMindmap.value = true
  
  // 初始占位符
  mindmapContent.value = '# 🧠 正在梳理文档逻辑...'
  
  try {
    let isFirstChunk = true
    await generateSmartMindmapStream(
      currentFile.value,
      (chunk) => {
        if (isFirstChunk) {
            mindmapContent.value = chunk
            isFirstChunk = false
        } else {
            mindmapContent.value += chunk
        }
      },
      (error) => {
        ElMessage.error('生成智能导图失败: ' + error.message)
        generatingMindmap.value = false
        mindmapContent.value = '# ❌ 生成失败\n请重试'
      },
      () => {
        generatingMindmap.value = false
        if (!mindmapContent.value || mindmapContent.value === '# 🧠 正在梳理文档逻辑...') {
            mindmapContent.value = '# 暂无内容'
        }
      }
    )
  } catch (error) {
    console.error('Smart Mindmap error:', error)
    generatingMindmap.value = false
  }
}

const startAnalysis = async (file) => {
  if (!ensureMethodologyBasis('请至少选择系统内置方法论或添加书籍作为评审依据')) return

  if (!currentUser.value) {
    showLoginDialog.value = true
    return
  }

  analyzing.value = true
  result.value = ''
  
  // 初始化 AbortController
  abortController.value = new AbortController()
  
  // 转换级联选择器的值为后端所需格式 ['vendor:scenario', ...]
  const formattedMethodologies = selectedMethodologies.value.map(item => {
    if (Array.isArray(item) && item.length === 2) {
      return `${item[0]}:${item[1]}`
    }
    return item
  })
  
  // 准备用户信息（包含角色）
  const userInfoWithRole = {
    ...currentUser.value,
    role: selectedRole.value // 将当前选择的角色传递给后端
  }

  await analyzeBlueprintStream(
    file,
    customPrompt.value,
    formattedMethodologies,
    customMethodologies.value,
    userInfoWithRole,
    abortController.value.signal,
    (chunk) => {
      result.value += chunk
    },
    (error) => {
      ElMessage.error('分析过程中发生错误: ' + error.message)
      analyzing.value = false
      abortController.value = null
    },
    () => {
      analyzing.value = false
      // 如果 abortController 还有值，说明是自然结束（非手动停止）
      if (abortController.value) { 
          if (!result.value || result.value.trim().length === 0) {
             ElMessage.warning('分析结束，但未收到任何内容。可能是后端服务异常。')
          } else {
             ElMessage.success('大师评审完成')
          }
      }
      abortController.value = null
    }
  )
}

const startProposalGeneration = async () => {
    if (!clientNeeds.value.trim()) {
        ElMessage.warning('请输入客户需求')
        return
    }
    
    if (!ensureMethodologyBasis('请至少选择系统内置方法论或添加书籍作为设计依据')) return
    
    if (!currentUser.value) {
        showLoginDialog.value = true
        return
    }

    analyzing.value = true
    result.value = ''
    
    abortController.value = new AbortController()

    const formattedMethodologies = selectedMethodologies.value.map(item => {
        if (Array.isArray(item) && item.length === 2) {
          return `${item[0]}:${item[1]}`
        }
        return item
    })

    await generateProposalStream(
        clientNeeds.value,
        userIdeas.value,
        formattedMethodologies,
        customMethodologies.value,
        referenceFile.value,
        (chunk) => {
          result.value += chunk
        },
        (error) => {
          ElMessage.error('方案生成失败: ' + error.message)
          analyzing.value = false
          abortController.value = null
        },
        () => {
          analyzing.value = false
          if (abortController.value) {
              if (!result.value || result.value.trim().length === 0) {
                 ElMessage.warning('生成结束，但无内容。')
              } else {
                 ElMessage.success('方案设计完成')
              }
          }
          abortController.value = null
        }
    )
}

const startSubProposalGeneration = async () => {
    if (!parentPlanFile.value) {
        ElMessage.warning('请先上传父方案文档')
        return
    }

    if (!subPlanTitle.value.trim()) {
        ElMessage.warning('请输入要生成的子专项/子方案名称')
        return
    }

    if (!ensureMethodologyBasis('请至少选择系统内置方法论或添加书籍作为设计依据')) return

    if (!currentUser.value) {
        showLoginDialog.value = true
        return
    }

    if (!subPlanDetails.value.trim()) {
        ElMessage.warning('建议补充流程/部门/系统等信息，生成效果更好')
    }

    analyzing.value = true
    result.value = ''

    abortController.value = new AbortController()

    const formattedMethodologies = selectedMethodologies.value.map(item => {
        if (Array.isArray(item) && item.length === 2) {
          return `${item[0]}:${item[1]}`
        }
        return item
    })

    await generateSubProposalStream(
        parentPlanFile.value,
        subPlanTitle.value,
        subPlanDetails.value,
        formattedMethodologies,
        customMethodologies.value,
        (chunk) => {
          result.value += chunk
        },
        (error) => {
          ElMessage.error('子方案生成失败: ' + error.message)
          analyzing.value = false
          abortController.value = null
        },
        () => {
          analyzing.value = false
          if (abortController.value) {
              if (!result.value || result.value.trim().length === 0) {
                 ElMessage.warning('生成结束，但无内容。')
              } else {
                 ElMessage.success('子方案生成完成')
              }
          }
          abortController.value = null
        }
    )
}

const reset = () => {
  result.value = ''
  analyzing.value = false
  customPrompt.value = ''
  customMethodologies.value = []
  newCustomMethodology.value = ''
  referenceFile.value = null
  parentPlanFile.value = null
  subPlanTitle.value = ''
  subPlanDetails.value = ''
  generationMode.value = 'from_needs'
}

const exportMarkdown = () => {
  const blob = new Blob([result.value], { type: 'text/markdown;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = '蓝图大师评审报告.md'
  link.click()
  URL.revokeObjectURL(link.href)
}

const handleGenerateMindmap = async () => {
  if (!result.value) return
  mindmapPurpose.value = activeMode.value === 'analysis' ? 'analysis' : (generationMode.value === 'from_parent' ? 'sub_proposal' : 'proposal')
  showMindmapDialog.value = true
  mindmapContent.value = ''
  generatingMindmap.value = true
  
  // 初始占位符
  mindmapContent.value = mindmapPurpose.value === 'analysis' ? '# 🚀 正在规划整改路径...' : '# 🧭 正在梳理方案结构...'
  
  try {
    let isFirstChunk = true
    await generateMindmapStream(
      result.value,
      (chunk) => {
        if (isFirstChunk) {
            mindmapContent.value = chunk
            isFirstChunk = false
        } else {
            mindmapContent.value += chunk
        }
      },
      (error) => {
        ElMessage.error('生成思维导图失败: ' + error.message)
        generatingMindmap.value = false
        mindmapContent.value = '# ❌ 生成失败\n请重试'
      },
      () => {
        generatingMindmap.value = false
        if (!mindmapContent.value || mindmapContent.value === (mindmapPurpose.value === 'analysis' ? '# 🚀 正在规划整改路径...' : '# 🧭 正在梳理方案结构...')) {
            mindmapContent.value = '# 暂无内容'
        }
      }
    )
  } catch (error) {
    console.error('Mindmap error:', error)
    generatingMindmap.value = false
  }
}

const downloadMindmapImage = () => {
  // 查找思维导图容器
  const container = document.querySelector('.mindmap-container')
  if (!container) {
    ElMessage.warning('未找到思维导图内容')
    return
  }

  // 使用 html2canvas 截图
  html2canvas(container, {
    backgroundColor: '#ffffff', // 确保背景是白色的
    scale: 2, // 2倍清晰度
    useCORS: true // 允许跨域图片
  }).then(canvas => {
    // 下载
    const link = document.createElement('a')
    link.download = mindmapDownloadName.value
    link.href = canvas.toDataURL('image/png')
    link.click()
  }).catch(error => {
    console.error('Image generation failed:', error)
    ElMessage.error('图片生成失败，请重试')
  })
}

const handleExportDocx = async () => {
  if (!result.value) return
  
  exporting.value = true
  try {
    await exportDocx(result.value, '蓝图大师评审报告.docx')
    ElMessage.success('导出 Word 成功')
  } catch (error) {
    ElMessage.error('导出 Word 失败: ' + error.message)
  } finally {
    exporting.value = false
  }
}
</script>

<style>
/* 全局样式覆盖 */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
  background-color: #f0f2f5;
  -webkit-font-smoothing: antialiased;
}

 .markdown-body {
  font-size: 15.5px;
  line-height: 1.75;
  color: #111827;
  font-family: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  letter-spacing: 0.1px;
}

.markdown-body > :first-child {
  margin-top: 0 !important;
}

.markdown-body > :last-child {
  margin-bottom: 0 !important;
}

.markdown-body .mermaid,
.markdown-body .mermaid-rendered {
  display: flex;
  justify-content: center;
  overflow-x: auto;
  padding: 10px 0;
}

.markdown-body .mermaid-rendered svg {
  max-width: 100%;
  height: auto;
}

.markdown-body h1 {
  font-size: 24px;
  line-height: 1.25;
  color: #0f172a;
  margin: 0 0 18px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5e7eb;
}

.markdown-body h2 {
  font-size: 18px;
  line-height: 1.35;
  color: #0f172a;
  margin: 22px 0 12px;
}

.markdown-body h3 {
  font-size: 16px;
  line-height: 1.4;
  color: #111827;
  margin: 18px 0 10px;
}

.markdown-body p {
  margin: 0 0 12px;
  color: #374151;
}

.markdown-body a {
  color: #2563eb;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 1.35em;
  margin: 0 0 12px;
  color: #374151;
}

.markdown-body li {
  margin: 6px 0;
}

.markdown-body blockquote {
  margin: 14px 0;
  padding: 10px 14px;
  border-left: 4px solid #e5e7eb;
  background: #f9fafb;
  color: #374151;
}

.markdown-body hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 18px 0;
}

.markdown-body code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 0.95em;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 2px 6px;
}

.markdown-body pre {
  background: #0b1020;
  color: #e5e7eb;
  border-radius: 8px;
  padding: 12px 14px;
  overflow: auto;
  margin: 14px 0;
}

.markdown-body pre code {
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
  font-size: 0.95em;
}

.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
}

.markdown-body table th,
.markdown-body table td {
  border: 1px solid #e5e7eb;
  padding: 8px 10px;
}

.markdown-body table th {
  background: #f9fafb;
  color: #111827;
}

.markdown-body img {
  max-width: 100%;
}

/* 移动端 Markdown 适配 */
@media (max-width: 768px) {
  .markdown-body {
    font-size: 14.5px;
  }
  .markdown-body h1 {
    font-size: 22px;
  }
  .markdown-body h2 {
    font-size: 18px;
  }
}

/* 响应式弹窗样式 */
.responsive-dialog {
  border-radius: 8px;
}

/* 仅限制登录和普通弹窗的宽度 */
.small-dialog {
  max-width: 500px;
}

.login-dialog .el-dialog__body {
  padding-top: 10px;
  padding-bottom: 20px;
}

.login-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 20px;
  line-height: 1.5;
}
</style>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.site-footer {
  padding: 12px 16px;
  color: #475569;
  background: rgba(255, 255, 255, 0.65);
  border-top: 1px solid rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(8px);
}

.site-footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
  line-height: 1.4;
}

.site-footer a {
  color: #2563eb;
  text-decoration: none;
}

.site-footer a:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 10px;
  color: #94a3b8;
}

@media (max-width: 768px) {
  .site-footer-content {
    flex-direction: column;
    align-items: flex-start;
  }
  .separator {
    margin: 0 8px;
  }
  .site-footer-right {
    color: #64748b;
  }
}

.role-selector-section {
  margin-bottom: 15px;
}

.role-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.role-group .el-radio-button__inner {
  border-radius: 4px !important;
  border: 1px solid #dcdfe6;
  padding: 8px 15px;
  box-shadow: none !important;
}

.role-group .el-radio-button.is-active .el-radio-button__inner {
  background-color: #d81e06;
  border-color: #d81e06;
  color: white;
}

.divider-dashed {
  height: 1px;
  border-top: 1px dashed #e4e7ed;
  margin: 15px 0;
}

.methodology-cascader {
  width: 100%;
  margin-bottom: 15px;
}

.custom-methodology-input {
  display: flex;
  margin-bottom: 15px;
}

.input-sub-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.custom-methodology-tags {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.custom-tag {
  font-size: 13px;
}

.header {
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 0 20px;
}

.header-content {
  max-width: 95%;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Mode Switcher */
.mode-tabs {
  margin-bottom: 20px;
}

.mode-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: transparent !important;
}

.generation-form {
  padding: 10px 0;
}

.form-item {
  margin-bottom: 20px;
}

.action-footer {
  margin-top: 25px;
  display: flex;
  justify-content: center;
}

.generate-btn {
  width: 100%;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #409EFF 0%, #3a8ee6 100%);
  border: none;
  padding: 12px 20px;
  height: auto;
  transition: all 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}
</style>

<style scoped>
/* 文件选择状态样式 */
.file-selected-state {
  padding: 20px;
}

.file-info {
  display: flex;
  align-items: center;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 25px;
}

.file-details {
  flex: 1;
  margin-left: 15px;
}

.file-details h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #303133;
}

.file-details p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}

.action-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fff;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #c6e2ff;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 15px;
}

.action-icon-report {
  background-color: #ecf5ff;
  color: #409eff;
}

.action-icon-mindmap {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.action-icon-smart {
  background-color: #f0f9eb;
  color: #67c23a;
}

.action-content {
  flex: 1;
}

.action-content h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #303133;
}

.action-content p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.arrow-icon {
  color: #c0c4cc;
}

@media (max-width: 768px) {
  .action-buttons {
    grid-template-columns: 1fr;
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  background: linear-gradient(45deg, #d81e06, #ff4d4f);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(216, 30, 6, 0.3);
}

.logo-text h1 {
  margin: 0;
  font-size: 18px;
  color: #303133;
  line-height: 1.2;
}

.logo-text .subtitle {
  font-size: 12px;
  color: #909399;
  letter-spacing: 0.5px;
  display: block;
}

.header-tags {
  display: flex;
  gap: 8px;
}

.content-wrapper {
  width: 95%;
  max-width: 1400px;
  margin: 20px auto;
  padding: 0 10px;
}

/* 输入面板 */
.input-panel {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 30px;
  width: 100%;
}

.hero-text {
  text-align: center;
  margin-top: 20px;
  padding: 0 10px;
  align-self: center;
}

.hero-text h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}

.hero-text p {
  font-size: 14px;
  color: #606266;
}

.upload-card {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  border: none;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

.custom-prompt-section, .methodology-section {
  padding: 15px 20px;
  background-color: #f9fafc;
}

.methodology-section {
  background-color: #fff;
}

.section-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-weight: 500;
  font-size: 14px;
}

.methodology-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.methodology-label {
  font-weight: bold;
  margin-right: 5px;
}

.methodology-desc {
  font-size: 12px;
  color: #909399;
}

.divider {
  height: 1px;
  background-color: #ebeef5;
}

.upload-area :deep(.el-upload-dragger) {
  border: none;
  border-radius: 0;
  padding: 40px 0;
  background-color: #fff;
}

.upload-text h3 {
  font-size: 16px;
  color: #303133;
  margin: 10px 0 5px;
}

.upload-text p {
  color: #909399;
  font-size: 12px;
}

/* 结果面板 */
.result-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: auto;
  min-height: 60vh;
  width: 100%;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #67c23a;
  font-weight: 500;
}

.status-badge.analyzing {
  color: #409eff;
}

.actions {
  display: flex;
  gap: 8px;
}

.markdown-container {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.markdown-container.paper-mode {
  background: #f3f4f6;
}

.markdown-paper.paper-mode {
  max-width: 210mm;
  margin: 10px auto 30px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 10px 30px rgba(17, 24, 39, 0.10);
  padding: 18mm 18mm;
}

.markdown-paper.paper-mode .markdown-body {
  font-family: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  color: #111827;
  font-size: 15px;
  line-height: 1.75;
}

.markdown-paper.paper-mode .markdown-body h1 {
  text-align: left;
  color: #111827;
  font-size: 22px;
  margin: 0 0 18px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5e7eb;
}

.markdown-paper.paper-mode .markdown-body h2 {
  background: transparent;
  border-left: none;
  border-radius: 0;
  padding: 0;
  margin-top: 22px;
  color: #111827;
  font-size: 18px;
}

.markdown-paper.paper-mode .markdown-body h3 {
  margin-top: 16px;
  font-size: 16px;
  color: #111827;
}

.markdown-paper.paper-mode .markdown-body p,
.markdown-paper.paper-mode .markdown-body li {
  color: #374151;
}

.markdown-paper.paper-mode .markdown-body blockquote {
  color: #374151;
  border-left: 4px solid #e5e7eb;
  background: #fafafa;
  padding: 10px 14px;
  margin: 16px 0;
}

.markdown-paper.paper-mode .markdown-body hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 18px 0;
}

.markdown-paper.paper-mode .markdown-body pre {
  background: #0b1020;
  color: #e5e7eb;
  border-radius: 6px;
  padding: 12px 14px;
  overflow: auto;
}

.markdown-paper.paper-mode .markdown-body code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.markdown-paper.paper-mode .markdown-body table {
  width: 100%;
  border-collapse: collapse;
}

.markdown-paper.paper-mode .markdown-body table th,
.markdown-paper.paper-mode .markdown-body table td {
  border: 1px solid #e5e7eb;
  padding: 8px 10px;
}

.markdown-paper.paper-mode .markdown-body table th {
  background: #f9fafb;
}

.markdown-paper.paper-mode .markdown-body .mermaid,
.markdown-paper.paper-mode .markdown-body .mermaid-rendered {
  background: #ffffff;
}

/* 响应式媒体查询 */
@media (max-width: 768px) {
  .desktop-only {
    display: none !important;
  }
  
  .header {
    padding: 0 15px;
  }
  
  .hero-text h2 {
    font-size: 20px;
  }
  
  .hero-text p {
    font-size: 13px;
  }
  
  .upload-area :deep(.el-upload-dragger) {
    padding: 30px 0;
  }
  
  .btn-text {
    display: none;
  }
  
  .markdown-container {
    padding: 15px;
  }

  .markdown-paper.paper-mode {
    max-width: 100%;
    margin: 0;
    padding: 16px 14px;
    border-radius: 10px;
  }
  
  .result-header {
    padding: 10px 15px;
  }
  
  .methodology-group :deep(.el-checkbox) {
    margin-right: 0;
    width: 100%;
  }
}

/* 动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.file-details {
  overflow: hidden;
}

.file-details h3 {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
