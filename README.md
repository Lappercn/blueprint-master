# 蓝图大师（Blueprint Master）

基于“方法论 + 文档识别 + 大模型”的蓝图评审与方案生成工具，支持流式生成、思维导图、Mermaid 架构图展示，并可导出 DOCX。

## 使用声明（严禁商用/抄袭）

- 本项目仅供学习与技术交流使用
- 严禁将本项目（含代码、界面、文档与输出内容）用于任何商业用途
- 严禁抄袭、搬运、二次分发或改头换面后对外发布/售卖
- 如需商业授权或转载，请先联系作者取得书面许可

## 功能概览

- 蓝图评审：上传蓝图/方案文档，选择方法论或参考书籍，流式生成评审报告
- 思维导图：
  - 诊断思维导图：基于上传文件直接生成诊断向导图
  - 智能思维导图：基于上传文件生成结构化导图（非诊断模式）
  - 报告转导图：将已生成的 Markdown 报告转换为 Markmap 导图
- 方案生成：输入客户需求与想法（可选参考文件），基于方法论流式生成方案（含 Mermaid 架构图）
- 子专项方案生成：上传父方案 + 描述子专项名称与细节，自动识别父方案并生成子方案
- 导出：将 Markdown 报告导出为 DOCX
- 运营能力：用户登录（用户名 + 浏览器指纹）、使用日志、反馈与看板接口（基于 MongoDB）

## 技术栈

- 前端：Vue 3 + Vite + Element-Plus
- 后端：Flask（SSE 流式输出）+ Flask-CORS + Waitress（生产）
- 数据库：MongoDB（用户、日志、统计、反馈等）

## 目录结构

```text
.
├─ backend/                 # Flask 后端
│  ├─ run.py               # 开发启动（debug）
│  ├─ run_prod.py          # 生产启动（waitress）
│  ├─ requirements.txt
│  └─ .env                 # 后端环境变量（建议本地自建，不要提交）
├─ frontend/                # Vue 前端
│  ├─ server.js            # 生产静态服务 + /api 代理
│  ├─ vite.config.js       # 开发代理 /api -> 5000
│  ├─ package.json
│  └─ .env                 # 前端环境变量（VITE_API_BASE_URL）
└─ start_server.ps1         # 一键生产模式启动脚本（Windows）
```

## 快速开始（开发模式）

### 1) 准备环境

- Python 3.10+（建议 3.11/3.12）
- Node.js 18+（建议 20+）
- MongoDB 6+（本机或远程均可）

依赖镜像（可选）：

```powershell
# npm 使用国内镜像
npm config set registry https://registry.npmmirror.com
```

### 2) 配置后端环境变量

在 `backend/.env` 中配置（示例，勿填入真实密钥到仓库）：

```env
TEXTIN_APP_ID=your_textin_app_id
TEXTIN_SECRET_CODE=your_textin_secret_code

OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://your-openai-compatible-base-url
LLM_MODEL=your_model_name

MONGO_URI=mongodb://localhost:27017/blueprint_master
```

### 3) 启动后端（5000）

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 使用清华镜像安装依赖（推荐）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

python run.py
```

后端默认监听：

- http://localhost:5000
- API 前缀：`/api/v1/*`

### 4) 启动前端（开发 5173）

打开新 PowerShell 窗口：

```powershell
cd frontend
npm install
npm run dev
```

访问 Vite 输出的本地地址（通常为）：

- http://localhost:5173

说明：开发模式下，`frontend/vite.config.js` 已将 `/api` 代理到 `http://localhost:5000`。

## 生产部署（本机/服务器）

### 方式 A：一键启动（Windows）

确保已安装并可直接使用 `python`、`node`、`npm`，并已安装依赖后：

```powershell
.\start_server.ps1
```

脚本会：

- 若 `frontend/dist` 不存在，自动执行 `npm run build`
- 后端使用 `backend/run_prod.py`（Waitress）启动在 `127.0.0.1:5000`
- 前端使用 `frontend/server.js`（Express）启动在 `0.0.0.0:8080`

访问：

- http://localhost:8080

### 方式 B：分别启动

```powershell
# 后端（生产）
cd backend
python run_prod.py
```

```powershell
# 前端（生产静态服务 + 代理）
cd frontend
npm run build
node server.js
```

可选环境变量：

- `PORT`：前端生产服务端口（默认 8080）
- `BACKEND_URL`：前端代理目标（默认 http://127.0.0.1:5000）

## 接口与前端配置说明

- 后端统一挂载：`/api/v1`
  - 蓝图相关：`/api/v1/blueprint/*`（分析、思维导图、方案/子方案生成、导出）
  - 登录：`/api/v1/auth/login`
  - 反馈：`/api/v1/feedback/*`
  - 看板：`/api/v1/dashboard/*`
- 前端请求 BaseURL：`frontend/.env` 中的 `VITE_API_BASE_URL`（默认 `/api/v1`），禁止在代码中硬编码
- 生产环境下由 `frontend/server.js` 代理 `/api` 到后端，前端只访问自身域名即可

## 常见问题

- 生成内容为空或识别失败：检查上传文档清晰度/格式，以及 OCR（TextIn）配置是否正确
- 接口报 500：优先查看后端控制台日志；多数为外部模型/网络/密钥配置问题
- 无法写入日志/登录失败：确认 MongoDB 可连接，或在 `backend/.env` 中设置正确的 `MONGO_URI`
