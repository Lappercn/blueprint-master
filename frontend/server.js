// 文件名：server.js
/**
 * 功能说明：前端生产环境服务器
 * 核心功能：
 * 1. 托管 dist 目录下的静态文件
 * 2. 代理 /api 请求到后端
 * 3. 处理 SPA 路由回退 (Fallback to index.html)
 */
import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import path from 'path';
import { fileURLToPath } from 'url';

// 获取 __dirname (ESM 模式)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
// 默认端口 8080，避免 80 端口权限问题。如果需要公网访问且不想带端口，可以改为 80 (需管理员权限)
const PORT = process.env.PORT || 8080;
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:5000';

console.log('Starting Blueprint Master Frontend Server...');

// 1. 配置 API 代理
// 将所有 /api 开头的请求转发到后端
app.use('/api', createProxyMiddleware({
    target: BACKEND_URL,
    changeOrigin: true,
    pathRewrite: {
        // 如果后端不需要 /api 前缀，可以在这里重写
        // '^/api': '' 
    },
    onProxyReq: (proxyReq, req, res) => {
        // 可以在这里添加自定义 header
    },
    onError: (err, req, res) => {
        console.error('Proxy Error:', err);
        res.status(500).send('Proxy Error');
    }
}));

// 2. 托管静态文件
// 指向 build 生成的 dist 目录
const distPath = path.join(__dirname, 'dist');
app.use(express.static(distPath));

// 3. SPA 路由回退
// 所有未匹配的请求都返回 index.html，让 Vue Router 接管
app.get('*', (req, res) => {
    res.sendFile(path.join(distPath, 'index.html'));
});

// 启动服务
app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n✅ Server is running!`);
    console.log(`📡 Access URL: http://localhost:${PORT}`);
    console.log(`🔗 Proxy Target: ${BACKEND_URL}\n`);
});
