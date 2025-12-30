# 文件名：analysis_service.py
"""
功能说明：蓝图分析业务逻辑服务
核心功能：
1. 调用OCR识别文件内容
2. 构建提示词工程
3. 调用LLM进行流式分析
依赖模块：ocr_client, llm_client, config
"""
import logging
import re
from typing import Generator, List
from app.config import Config
from app.utils.ocr_client import OCRClient
from app.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

# 定义结构化的场景方法论库
METHODOLOGIES_STRUCTURED = {
    "huawei": {
        "label": "华为 (Huawei)",
        "scenarios": {
            "strategy": {
                "label": "战略规划层 (Strategy - BLM/BEM)",
                "description": "适用于公司战略解码、顶层设计、业务蓝图规划。",
                "content": """
                *   **华为战略规划方法论** (参考书籍：《价值为纲》、《以客户为中心》)：
                    *   **BLM (Business Leadership Model, 业务领先模型)**：
                        *   **差距分析**：从业绩差距（结果）和机会差距（未来）入手。
                        *   **战略意图**：愿景、战略目标、近期目标。
                        *   **市场洞察**：五看（看趋势、看市场、看客户、看竞争、看自己）。
                        *   **创新焦点**：未来业务组合、创新模式（产品/服务/商业模式）。
                        *   **业务设计**：客户选择、价值主张、盈利模式、战略控制点、风险管理。
                    *   **BEM (Business Engineering Methodology, 业务工程方法)**：战略解码，将战略目标分解为关键业务指标（KPI）和重点工作（PBC）。
                """
            },
            "finance_mgmt": {
                "label": "财经管理层 (IFS)",
                "description": "适用于财经流程、全面预算管理、内控。",
                "content": """
                *   **华为IFS (Integrated Financial Services, 集成财经服务)** (参考书籍：《华为财经密码》)：
                    *   **业财融合**：财经切入业务前端，从“记账员”转变为“业务伙伴”。
                    *   **全面预算管理**：战略决定预算，预算保障战略。
                    *   **项目四算**：概算、预算、核算、决算。
                """
            },
            "marketing": {
                "label": "市场营销层 (MTL)",
                "description": "适用于市场洞察、品牌管理、线索生成。",
                "content": """
                *   **华为MTL (Market to Lead, 市场到线索)** (参考书籍：《华为营销法》)：
                    *   **市场洞察 (MI)**：理解宏观环境、行业趋势、客户声音。
                    *   **市场管理 (MM)**：细分市场、目标市场选择、定位。
                    *   **活动管理**：通过营销活动生成高质量销售线索。
                """
            },
            "issue_mgmt": {
                "label": "问题到解决层 (ITR)",
                "description": "适用于售后服务、客户投诉处理、运维。",
                "content": """
                *   **华为ITR (Issue to Resolution, 问题到解决)**：
                    *   **端到端闭环**：受理 -> 处理 -> 关闭 -> 评价。
                    *   **分层分级**：一线快速响应，二线专家支持，三线研发攻关。
                    *   **知识沉淀**：将问题转化为知识库 (KB)，避免重复造轮子。
                """
            },
            "project_delivery": {
                "label": "项目交付/销售层 (LTC/LTC-P)",
                "description": "适用于销售项目管理、交付实施、合同履约。",
                "content": """
                *   **华为LTC (Lead to Cash) 流程** (参考书籍：《华为营销法》、《华为铁三角工作法》)：
                    *   **管理线索 (ML)**：线索挖掘、培育、分发。
                    *   **管理机会点 (MO)**：机会点验证、立项、投标、合同谈判。
                    *   **管理合同执行 (MCE)**：合同交接、发货/交付、验收、回款。
                    *   **铁三角组织**：AR (客户经理)、SR (解决方案经理)、FR (交付经理) 协同作战。
                """
            },
            "product_dev": {
                "label": "产品研发层 (IPD)",
                "description": "适用于产品开发、技术架构设计、研发管理。",
                "content": """
                *   **华为IPD (Integrated Product Development, 集成产品开发)** (参考书籍：《IPD：华为研发之道》、《华为研发》)：
                    *   **结构化流程**：概念、计划、开发、验证、发布、生命周期管理。
                    *   **异步开发**：技术开发与产品开发分离。
                    *   **跨部门团队 (PDT)**：打破部门墙，对商业成功负责。
                    *   **CBB (Common Building Block)**：共用基础模块，提升研发效率。
                """
            },
            "digital_transformation": {
                "label": "数字化转型层 (Digital)",
                "description": "适用于企业数字化转型规划、数据治理、IT架构。",
                "content": """
                *   **华为数字化转型方法论** (参考书籍：《华为数字化转型之道》)：
                    *   **1套方法**：对象数字化、过程数字化、规则数字化。
                    *   **5转**：转意识、转组织、转文化、转方法、转模式。
                    *   **“五看三定”**：看行业、看客户、看自己、看机会、看技术；定战略、定模式、定路径。
                    *   **数据底座**：数据入湖、数据资产化、数据服务化。
                """
            }
        }
    },
    "general": {
        "label": "通用/行业标准 (General)",
        "scenarios": {
            "enterprise_arch": {
                "label": "企业架构层 (Enterprise Architecture)",
                "description": "适用于顶层架构规划、业务与IT对齐。",
                "content": """
                *   **通用企业架构标准** (参考书籍：《TOGAF标准》、《企业架构的数字化转型》)：
                    *   **TOGAF (The Open Group Architecture Framework)**：
                        *   **ADM (Architecture Development Method)**：架构开发方法循环。
                        *   **4A架构**：业务架构 (Business)、数据架构 (Data)、应用架构 (Application)、技术架构 (Technology)。
                """
            },
            "it_management": {
                "label": "IT服务与管理层 (IT Management)",
                "description": "适用于IT运维管理、服务流程规范。",
                "content": """
                *   **通用IT管理标准** (参考书籍：《ITIL 4 实践指南》、《DevOps 实践指南》)：
                    *   **ITIL (Information Technology Infrastructure Library)**：IT服务管理最佳实践。
                    *   **DevOps**：开发与运维融合，持续交付 (CI/CD)。
                """
            },
            "project_management": {
                "label": "项目管理层 (Project Management)",
                "description": "适用于通用项目管理、敏捷开发。",
                "content": """
                *   **通用项目管理标准** (参考书籍：《PMBOK指南》、《Scrum精髓》)：
                    *   **PMP/PMBOK**：五大过程组（启动、规划、执行、监控、收尾）、十大知识领域。
                    *   **Agile/Scrum**：敏捷开发、迭代冲刺、每日站会。
                """
            }
        }
    },
    "advertising": {
        "label": "广告营销大师 (Advertising & Marketing)",
        "scenarios": {
            "positioning": {
                "label": "定位理论 (Positioning)",
                "description": "适用于品牌定位、心智占领。",
                "content": """
                *   **定位理论 (Positioning)** (参考书籍：《定位》、《商战》 - 特劳特/里斯)：
                    *   **心智阶梯**：品牌在消费者心智中的排名。
                    *   **差异化**：寻找竞争对手无法占据的优势位置。
                    *   **聚焦**：集中资源攻击一点。
                """
            },
            "integrated_marketing": {
                "label": "整合营销 (IMC)",
                "description": "适用于全案策划、品牌传播。",
                "content": """
                *   **整合营销传播 (IMC)** (参考书籍：《整合营销传播》 - 舒尔茨)：
                    *   **4C理论**：消费者(Consumer)、成本(Cost)、便利(Convenience)、沟通(Communication)。
                    *   **品牌接触点**：管理所有与消费者接触的环节。
                """
            },
            "creative": {
                "label": "创意与文案 (Creative)",
                "description": "适用于广告创意、文案写作。",
                "content": """
                *   **奥格威广告法则** (参考书籍：《一个广告人的自白》 - 大卫·奥格威)：
                    *   **品牌形象**：每一则广告都是对品牌个性的长期投资。
                    *   **大创意 (Big Idea)**：除非你的广告基于一个大创意，否则它就像夜航的船，无人知晓。
                    *   **销售力**：广告的目的是销售，不是娱乐。
                """
            },
            "growth_hacking": {
                "label": "增长黑客 (Growth)",
                "description": "适用于用户增长、流量运营。",
                "content": """
                *   **增长黑客** (参考书籍：《增长黑客》 - 肖恩·埃利斯)：
                    *   **AARRR模型**：获取(Acquisition)、激活(Activation)、留存(Retention)、变现(Revenue)、推荐(Referral)。
                    *   **北极星指标**：指引全公司向着长期价值增长方向发展的唯一关键指标。
                """
            }
        }
    }
}

class AnalysisService:
    def __init__(self):
        # 初始化 OCR 客户端
        self.ocr_client = OCRClient(
            app_id=Config.TEXTIN_APP_ID,
            secret_code=Config.TEXTIN_SECRET_CODE
        )
        # 初始化 LLM 客户端
        self.llm_client = LLMClient(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL,
            model=Config.LLM_MODEL
        )

    def _compress_methodology_text(self, text: str, max_chars: int) -> str:
        if not text:
            return ""
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        if len(normalized) <= max_chars:
            return normalized
        lines = []
        total = 0
        for line in normalized.splitlines():
            s = line.strip()
            keep = (
                s == ""
                or s.startswith("###")
                or s.startswith("*")
                or s.startswith("-")
                or s.startswith("1.")
                or s.startswith("2.")
                or s.startswith("3.")
            )
            if not keep:
                continue
            if total + len(line) + 1 > max_chars:
                break
            lines.append(line)
            total += len(line) + 1
        compact = "\n".join(lines).strip()
        if not compact:
            compact = normalized[:max_chars]
        return compact[:max_chars]

    def _compress_context_text(self, text: str, max_chars: int) -> tuple[str, bool]:
        if not text:
            return "", False

        original_len = len(text)
        t = text.replace("\r\n", "\n").replace("\r", "\n")
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r"\n{3,}", "\n\n", t)
        t = re.sub(r"```[\s\S]{2000,}?```", "```(已省略超长代码块)```", t)

        if len(t) <= max_chars:
            return t, len(t) != original_len

        lines = t.splitlines()
        heading_indexes: List[int] = []
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith("#"):
                heading_indexes.append(i)

        keep_line_indexes = set()
        for i in heading_indexes[:200]:
            for j in range(i, min(i + 6, len(lines))):
                keep_line_indexes.add(j)

        extracted_lines = [lines[i] for i in range(len(lines)) if i in keep_line_indexes]
        extracted = "\n".join(extracted_lines).strip()

        head = t[:8000]
        tail = t[-2000:] if len(t) > 2000 else ""
        combined = "\n\n".join([p for p in [head.strip(), extracted, tail.strip()] if p])
        combined = re.sub(r"\n{3,}", "\n\n", combined)
        combined = combined[:max_chars]
        return combined, True

    def analyze_blueprint(self, file_content: bytes, file_name: str, custom_prompt: str = "", selected_methodologies: List[str] = None, custom_methodologies: List[str] = None) -> Generator[str, None, None]:
        """
        分析蓝图文件
        :param file_content: 文件内容
        :param file_name: 文件名
        :param custom_prompt: 用户自定义提示词
        :param selected_methodologies: 用户选择的方法论列表 ['huawei', 'alibaba', ...]
        :param custom_methodologies: 用户自定义的方法论列表
        :return: LLM 流式响应生成器
        """
        try:
            # 0. 发送初始状态，确保流连接建立
            yield f"🔄 正在解析文档内容，请稍候...\n\n"
            
            # 定时发送心跳包的生成器函数
            def keep_alive_ocr():
                import time
                while True:
                    time.sleep(2) # 每2秒检查一次
                    yield f": keep-alive\n\n"

            # 1. OCR 识别
            logger.info(f"Starting OCR for file: {file_name}")
            
            # 由于OCR是同步阻塞调用，我们无法在其中插入yield。
            # 如果OCR非常慢（超过60秒），仍然可能导致超时。
            # 理想方案是将OCR放入独立线程，主线程yield心跳。
            # 这里先尝试更激进的padding和更快的响应。
            
            import threading
            import queue
            
            ocr_queue = queue.Queue()
            
            def run_ocr_thread():
                try:
                    text = self.ocr_client.recognize(file_content)
                    ocr_queue.put({"status": "success", "data": text})
                except Exception as e:
                    ocr_queue.put({"status": "error", "error": e})
            
            ocr_thread = threading.Thread(target=run_ocr_thread)
            ocr_thread.start()
            
            # 等待OCR结果，期间发送心跳
            # 使用 SSE 协议标准的注释格式 ": comment\n\n"
            # 许多代理服务器（如Nginx）需要看到 \n\n 才会刷新缓冲区
            # 且注释行以冒号开头是 SSE 规范，避免前端解析错误
            while ocr_thread.is_alive():
                ocr_thread.join(timeout=2.0) # 每2秒醒来一次
                if ocr_thread.is_alive():
                     yield f": processing ocr keep-alive\n\n" 
            
            # 获取结果
            if not ocr_queue.empty():
                result = ocr_queue.get()
                if result["status"] == "error":
                     raise result["error"]
                ocr_text = result["data"]
            else:
                ocr_text = ""
            
            logger.info(f"OCR result length: {len(ocr_text) if ocr_text else 0}")

            if not ocr_text or len(ocr_text.strip()) == 0:
                logger.warning("OCR returned empty text")
                yield "无法识别文件内容，请检查文件是否清晰或格式是否正确。"
                return

            logger.info("OCR completed, constructing prompt...")

            # 2. 构建提示词
            compressed_text, compressed = self._compress_context_text(ocr_text, max_chars=18000)
            if compressed:
                yield "📉 文档内容较长，已自动提炼关键内容以适配模型上下文限制。\n\n"

            prompt_messages = self._build_prompt(compressed_text, custom_prompt, selected_methodologies, custom_methodologies)
            logger.info(f"Prompt constructed with {len(prompt_messages)} messages")

            # 3. LLM 流式分析
            logger.info("Starting LLM stream...")
            for chunk in self.llm_client.chat_stream(prompt_messages):
                logger.debug(f"Yielding chunk: {len(chunk)} chars")
                yield chunk
            logger.info("LLM stream completed")

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            yield f"\n\n**系统错误**: {str(e)}"

    def generate_mindmap(self, markdown_content: str) -> Generator[str, None, None]:
        """
        基于分析报告生成思维导图 (Markmap 格式)
        :param markdown_content: 分析报告内容
        :return: LLM 流式响应生成器
        """
        try:
            system_prompt = """
            你是一个战略实施顾问和思维导图专家。
            你的任务是将一份《蓝图大师深度评审报告》或《蓝图设计方案》转化为一张**面向落地的整改行动思维导图**。
            
            ### 核心要求：
            **必须完全使用中文输出**，除非专有名词（如BLM, IPD）必须保留英文。请再次确认所有解释和描述均为中文。

            ### 转换目标：
            1. **如果是评审报告**（包含“关键缺陷”、“深度剖析”等章节）：
               请重新组织为“**问题 -> 归因 -> 行动**”的闭环结构。让用户一眼就能看懂“哪里有问题”以及“具体怎么改”。
            2. **如果是设计方案**（包含“核心策略”、“总体架构”、“关键行动”等章节）：
               请直接梳理其核心逻辑，重点展示“**策略 -> 架构 -> 行动**”的层级结构。

            ### 转换规则（Markmap Markdown 格式）：
            1.  **根节点**：使用一级标题 # 作为根节点，命名为“🚀 蓝图落地行动指南”。
            2.  **内容提取**：
                *   提取核心观点、关键举措、实施路径。
                *   使用 ✅ Emoji 标记具体的行动项。
                *   使用 📅 Emoji 标记建议的实施阶段（如：速赢、中期）。
            
            ### 示例输出（通用结构）：
            # 🚀 蓝图落地行动指南
            ## 1. 核心战略/问题域
            ### 原因/背景：...
            ### ✅ 核心行动方案
            #### 📅 短期：...
            #### 📅 长期：...
            """
            
            user_prompt = f"请根据以下内容，生成一份落地行动思维导图：\n\n{markdown_content}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            for chunk in self.llm_client.chat_stream(messages):
                yield chunk
                
        except Exception as e:
            logger.error(f"Mindmap generation failed: {str(e)}", exc_info=True)
            yield f"思维导图生成失败: {str(e)}"

    def analyze_blueprint_to_mindmap(self, file_content: bytes, file_name: str) -> Generator[str, None, None]:
        """
        分析蓝图文件并直接生成诊断思维导图
        :param file_content: 文件内容
        :param file_name: 文件名
        :return: LLM 流式响应生成器 (Markmap Markdown)
        """
        try:
            # 1. OCR 识别
            logger.info(f"Starting OCR for diagnosis mindmap: {file_name}")
            yield "# 🚀 正在解析蓝图结构...\n"
            
            # 使用多线程+心跳机制处理OCR
            import threading
            import queue
            
            ocr_queue = queue.Queue()
            
            def run_ocr_thread():
                try:
                    text = self.ocr_client.recognize(file_content)
                    ocr_queue.put({"status": "success", "data": text})
                except Exception as e:
                    ocr_queue.put({"status": "error", "error": e})
            
            ocr_thread = threading.Thread(target=run_ocr_thread)
            ocr_thread.start()
            
            # 等待OCR结果，期间发送心跳
            while ocr_thread.is_alive():
                ocr_thread.join(timeout=2.0)
                if ocr_thread.is_alive():
                     yield f": processing ocr keep-alive\n\n" 
            
            # 获取结果
            if not ocr_queue.empty():
                result = ocr_queue.get()
                if result["status"] == "error":
                     raise result["error"]
                ocr_text = result["data"]
            else:
                ocr_text = ""
            
            if not ocr_text or len(ocr_text.strip()) == 0:
                logger.warning("OCR returned empty text")
                yield "无法识别文件内容，请检查文件是否清晰或格式是否正确。"
                return

            logger.info("OCR completed, starting mindmap generation...")
            
            # 2. 生成思维导图
            yield "\n# 🧠 正在生成诊断思维导图...\n"
            
            # 构建生成思维导图的 Prompt
            prompt_messages = [
                {"role": "system", "content": """
                你是一个战略咨询专家。请根据用户提供的文档内容，直接生成一份**Markmap格式**的诊断思维导图。
                
                **输出要求：**
                1. 根节点为：`# 🚀 [文档标题] - 深度诊断图`
                2. 第一层节点必须包含：`## 核心问题`、`## 潜在风险`、`## 改进建议`。
                3. 使用 Emoji 增强可读性。
                4. 只输出 Markmap Markdown 代码，不要包含 ```markdown 代码块标记。
                """},
                {"role": "user", "content": f"文档内容如下：\n\n{ocr_text[:50000]}"} # 截断防止超长
            ]
            
            for chunk in self.llm_client.chat_stream(prompt_messages):
                yield chunk

        except Exception as e:
            logger.error(f"Mindmap analysis failed: {str(e)}", exc_info=True)
            yield f"\n# ❌ 分析失败: {str(e)}"

    def generate_smart_mindmap(self, file_content: bytes, file_name: str) -> Generator[str, None, None]:
        """
        生成智能思维导图
        """
        try:
             # 1. OCR 识别
            logger.info(f"Starting OCR for smart mindmap: {file_name}")
            yield "# 🚀 正在读取文档内容...\n"
            
            # 使用多线程+心跳机制处理OCR
            import threading
            import queue
            
            ocr_queue = queue.Queue()
            
            def run_ocr_thread():
                try:
                    text = self.ocr_client.recognize(file_content)
                    ocr_queue.put({"status": "success", "data": text})
                except Exception as e:
                    ocr_queue.put({"status": "error", "error": e})
            
            ocr_thread = threading.Thread(target=run_ocr_thread)
            ocr_thread.start()
            
            # 等待OCR结果，期间发送心跳
            while ocr_thread.is_alive():
                ocr_thread.join(timeout=2.0)
                if ocr_thread.is_alive():
                     yield f": processing ocr keep-alive\n\n"
            
            # 获取结果
            if not ocr_queue.empty():
                result = ocr_queue.get()
                if result["status"] == "error":
                     raise result["error"]
                ocr_text = result["data"]
            else:
                ocr_text = ""
                
            if not ocr_text:
                yield "无法识别文件内容"
                return

            logger.info("OCR completed, generating mindmap...")
            yield "\n# 💡 正在构建思维导图...\n"
            
            prompt_messages = [
                {"role": "system", "content": """
                请将以下文档内容整理为清晰的 Markmap 思维导图。
                保持结构化，提取关键信息。
                只输出 Markdown 内容。
                """},
                {"role": "user", "content": ocr_text[:50000]}
            ]
            
            for chunk in self.llm_client.chat_stream(prompt_messages):
                yield chunk

        except Exception as e:
            logger.error(f"Smart mindmap failed: {str(e)}", exc_info=True)
            yield f"\n# ❌ 生成失败: {str(e)}"

    def generate_proposal(self, client_needs: str, user_ideas: str, selected_methodologies: List[str] = None, custom_methodologies: List[str] = None, reference_file_content: bytes | None = None, reference_file_name: str | None = None) -> Generator[str, None, None]:
        """
        根据需求和想法生成蓝图方案
        :param client_needs: 客户需求
        :param user_ideas: 用户想法/参考资料
        :param selected_methodologies: 选择的方法论
        :param custom_methodologies: 自定义方法论
        :return: LLM 流式响应生成器
        """
        try:
            # 0. 发送初始状态
            yield "🔄 正在构建方案生成模型，请稍候...\n\n"

            reference_text = ""
            if reference_file_content and reference_file_name:
                yield "📎 正在解析参考资料，请稍候...\n\n"
                try:
                    reference_text = self.ocr_client.recognize(reference_file_content)
                except Exception as e:
                    logger.error(f"Reference file OCR failed: {str(e)}", exc_info=True)

            ideas_parts = []
            if user_ideas and user_ideas.strip():
                ideas_parts.append(user_ideas.strip())
            if reference_text and reference_text.strip():
                compressed_ref, compressed = self._compress_context_text(reference_text.strip(), max_chars=12000)
                if compressed:
                    yield "📉 参考资料较长，已自动提炼关键内容以适配模型上下文限制。\n\n"
                ideas_parts.append(f"### 参考资料附件：{reference_file_name}\n{compressed_ref}")

            merged_user_ideas = "\n\n".join(ideas_parts)

            # 1. 构建提示词
            prompt_messages = self._build_proposal_prompt(client_needs, merged_user_ideas, selected_methodologies, custom_methodologies)
            logger.info(f"Proposal prompt constructed with {len(prompt_messages)} messages")

            # 2. LLM 流式生成
            logger.info("Starting LLM stream for proposal...")
            for chunk in self.llm_client.chat_stream(prompt_messages):
                yield chunk
            logger.info("LLM stream completed")

        except Exception as e:
            logger.error(f"Proposal generation failed: {str(e)}", exc_info=True)
            yield f"\n\n**系统错误**: {str(e)}"

    def generate_sub_proposal(self, parent_file_content: bytes, parent_file_name: str, sub_topic: str, user_ideas: str, selected_methodologies: List[str] = None, custom_methodologies: List[str] = None) -> Generator[str, None, None]:
        try:
            yield "🔄 正在解析父方案内容，请稍候...\n\n"

            parent_text = self.ocr_client.recognize(parent_file_content)
            if not parent_text or len(parent_text.strip()) == 0:
                yield "❌ 无法识别父方案内容，请检查文件是否清晰或格式是否正确。"
                return

            yield "🔄 正在生成子专项方案，请稍候...\n\n"

            compressed_parent, compressed = self._compress_context_text(parent_text, max_chars=18000)
            if compressed:
                yield "📉 父方案内容较长，已自动提炼关键内容以适配模型上下文限制。\n\n"

            prompt_messages = self._build_sub_proposal_prompt(compressed_parent, parent_file_name, sub_topic, user_ideas, selected_methodologies, custom_methodologies)
            logger.info(f"Sub proposal prompt constructed with {len(prompt_messages)} messages")

            for chunk in self.llm_client.chat_stream(prompt_messages):
                yield chunk

        except Exception as e:
            logger.error(f"Sub proposal generation failed: {str(e)}", exc_info=True)
            yield f"\n\n**系统错误**: {str(e)}"

    def _build_sub_proposal_prompt(self, parent_text: str, parent_file_name: str, sub_topic: str, user_ideas: str, selected_methodologies: List[str] = None, custom_methodologies: List[str] = None) -> list:
        methodology_text = ""

        if selected_methodologies:
            for item in selected_methodologies:
                if ":" in item:
                    vendor, scenario = item.split(":", 1)
                    if vendor in METHODOLOGIES_STRUCTURED and scenario in METHODOLOGIES_STRUCTURED[vendor]["scenarios"]:
                        scenario_data = METHODOLOGIES_STRUCTURED[vendor]["scenarios"][scenario]
                        methodology_text += f"\n### 【{METHODOLOGIES_STRUCTURED[vendor]['label']} - {scenario_data['label']}】\n{scenario_data['content']}\n"
                else:
                    vendor = item
                    if vendor in METHODOLOGIES_STRUCTURED:
                        methodology_text += f"\n### 【{METHODOLOGIES_STRUCTURED[vendor]['label']} (全场景)】\n"
                        for s_key, s_data in METHODOLOGIES_STRUCTURED[vendor]["scenarios"].items():
                            methodology_text += f"{s_data['content']}\n"

        if custom_methodologies:
            methodology_text += "\n### 【部门默认参考书籍/理论】\n"
            for cm in custom_methodologies:
                if cm.strip():
                    methodology_text += f"*   📖 **{cm}**\n"

        methodology_text = self._compress_methodology_text(methodology_text, max_chars=8000)

        system_prompt = f"""
        你是一位**资深解决方案架构师**。

        ### 你的核心方法论库（本次子专项方案设计依据）：
        {methodology_text}

        ### 你的任务：
        用户上传了一份《父方案》，并指定要输出其中某一个“子专项/子方案”。
        你需要先阅读父方案内容，理解总体目标、边界、核心策略与约束，然后基于用户的子专项描述与方法论，生成一份可落地的子专项方案。

        ### 输出要求：
        - 必须完全中文输出（专有名词除外）
        - 必须与父方案保持一致：目标、术语、口径、约束
        - 必须可执行：包含流程、部门/角色、输入输出、里程碑、风险与保障
        - 如果用户描述不足，允许你在方案中显式列出“需要用户补充的信息清单”

        ### 输出格式（Markdown）：
        # 🧩 子专项方案 - {sub_topic}
        
        > 📎 父方案来源：{parent_file_name}

        ## 1. 子专项定位与目标
        ## 2. 与父方案的一致性对齐（目标/范围/约束/依赖）
        ## 3. 现状与问题（基于父方案摘要 + 用户补充）
        ## 4. 方案设计（策略/流程/系统/数据/组织）
        ## 5. 关键流程与协作机制（部门/角色/职责/RACI）
        ## 6. 交付物清单（模板/表单/规范/看板）
        ## 7. 实施计划（里程碑/迭代节奏/验收标准）
        ## 8. 风险与对策
        ## 9. 需要补充的信息清单（如果有）
        """

        user_input_content = f"""
        ### 父方案内容（OCR 提取，可能存在排版噪声）：
        {parent_text}

        ### 需要生成的子专项：
        {sub_topic}

        ### 用户对子专项的初步想法/补充信息（建议包含流程、涉及部门、系统、数据口径、边界）：
        {user_ideas}
        """

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input_content}
        ]

    def _build_proposal_prompt(self, client_needs: str, user_ideas: str, selected_methodologies: List[str] = None, custom_methodologies: List[str] = None) -> list:
        """
        构建方案生成提示词
        """
        # 复用 _build_prompt 中的方法论构建逻辑
        methodology_text = ""
        
        if selected_methodologies:
            for item in selected_methodologies:
                if ":" in item:
                    vendor, scenario = item.split(":", 1)
                    if vendor in METHODOLOGIES_STRUCTURED and scenario in METHODOLOGIES_STRUCTURED[vendor]["scenarios"]:
                        scenario_data = METHODOLOGIES_STRUCTURED[vendor]["scenarios"][scenario]
                        methodology_text += f"\n### 【{METHODOLOGIES_STRUCTURED[vendor]['label']} - {scenario_data['label']}】\n{scenario_data['content']}\n"
                else:
                    vendor = item
                    if vendor in METHODOLOGIES_STRUCTURED:
                        methodology_text += f"\n### 【{METHODOLOGIES_STRUCTURED[vendor]['label']} (全场景)】\n"
                        for s_key, s_data in METHODOLOGIES_STRUCTURED[vendor]["scenarios"].items():
                            methodology_text += f"{s_data['content']}\n"

        if custom_methodologies:
            methodology_text += "\n### 【部门默认参考书籍/理论】\n"
            for cm in custom_methodologies:
                if cm.strip():
                    methodology_text += f"*   📖 **{cm}**\n"

        methodology_text = self._compress_methodology_text(methodology_text, max_chars=8000)

        system_prompt = f"""
        你是一位**首席解决方案架构师**和**创意总监**。
        你精通各类商业模式、营销策略和企业架构设计。
        
        ### 你的核心方法论库（本次方案设计依据）：
        {methodology_text}

        ### 你的任务：
        根据用户提供的“客户需求”和“初步想法/参考资料”，结合上述方法论，**从0到1设计一份完整的蓝图方案**。
        
        ### 你的角色设定：
        *   **极度专业**：使用专业术语，逻辑严密。
        *   **落地导向**：不仅要有高大上的理论，还要有可执行的落地方案。
        *   **创新思维**：结合用户想法，提供超越预期的创意点。
        *   **语言要求**：**必须完全使用中文输出**，除非专有名词必须保留英文。请务必检查你的每一句输出，确保没有英文句子。

        ### 输出格式要求 (Markdown)：
        
        # 🚀 [项目名称] - 蓝图设计方案
        
        > 📋 **方案摘要**：
        > (简述方案核心价值和亮点)
        
        ## 1. 需求分析与背景 (Context)
        *   **客户痛点**：...
        *   **核心目标**：...
        
        ## 2. 核心策略与理念 (Strategy)
        (结合选定的方法论进行阐述)
        *   **理论支撑**：基于[某方法论]...
        *   **战略定位**：...
        
        ## 3. 总体架构设计 (Architecture)
        *   **业务架构**：...
        *   **关键流程**：...
        
        ## 4. 关键行动举措 (Key Actions)
        *   ✅ **行动1**：...
        *   ✅ **行动2**：...
        
        ## 5. 预期价值与成果 (Value)
        *   ...
        
        ---
        > 💡 **专家建议**：(给客户的一句核心建议)
        """

        user_input_content = f"""
        ### 客户需求 (Client Needs)：
        {client_needs}
        
        ### 我的想法/参考资料 (My Ideas/Reference)：
        {user_ideas}
        
        请基于以上信息，为我生成一份详细的蓝图方案。
        """

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input_content}
        ]

    def _build_prompt(self, context_text: str, custom_prompt: str, selected_methodologies: List[str] = None, custom_methodologies: List[str] = None) -> list:
        """
        构建提示词工程
        """
        # 构建方法论部分
        methodology_text = ""
        
        # 兼容旧逻辑：如果参数是 ['huawei', 'alibaba'] 这种顶层key，默认加载该厂商下的所有场景
        # 如果参数是 ['huawei:strategy', 'huawei:product_dev'] 这种具体场景，则按需加载
        
        selected_scenarios = []
        if selected_methodologies:
            for item in selected_methodologies:
                if ":" in item:
                    # 格式: "vendor:scenario"
                    vendor, scenario = item.split(":", 1)
                    if vendor in METHODOLOGIES_STRUCTURED and scenario in METHODOLOGIES_STRUCTURED[vendor]["scenarios"]:
                        scenario_data = METHODOLOGIES_STRUCTURED[vendor]["scenarios"][scenario]
                        methodology_text += f"\n### 【{METHODOLOGIES_STRUCTURED[vendor]['label']} - {scenario_data['label']}】\n{scenario_data['content']}\n"
                else:
                    # 格式: "vendor" (加载该厂商所有场景)
                    vendor = item
                    if vendor in METHODOLOGIES_STRUCTURED:
                        methodology_text += f"\n### 【{METHODOLOGIES_STRUCTURED[vendor]['label']} (全场景)】\n"
                        for s_key, s_data in METHODOLOGIES_STRUCTURED[vendor]["scenarios"].items():
                            methodology_text += f"{s_data['content']}\n"

        # 如果未选择任何方法论且无自定义，默认加载所有厂商的战略层场景（避免token过多）
        if not methodology_text and not custom_methodologies:
             for vendor, v_data in METHODOLOGIES_STRUCTURED.items():
                 if "strategy" in v_data["scenarios"]:
                     s_data = v_data["scenarios"]["strategy"]
                     methodology_text += f"\n### 【{v_data['label']} - {s_data['label']}】\n{s_data['content']}\n"

        
        # 添加用户自定义书籍/方法论
        if custom_methodologies:
            methodology_text += "\n### 【部门默认参考书籍/理论】\n"
            for cm in custom_methodologies:
                if cm.strip():
                    methodology_text += f"*   📖 **{cm}**\n"

        methodology_text = self._compress_methodology_text(methodology_text, max_chars=8000)

        system_prompt = f"""
你是一位**蓝图大师 (Blueprint Master)**，一位拥有20年实战经验的企业级架构治理专家。
你熟读并精通**华为（Huawei）**全套管理变革方法论，以及**TOGAF**、**ITIL**、**PMP**等国际标准。
你的核心能力是能够像“外科医生”一样，对企业的各类蓝图文档（战略/业务/技术/管理）进行精准诊断。

### 你的核心方法论库（本次评审依据）：
{methodology_text}

### 你的角色设定与自我认知：
*   **我是谁**：我不是一个简单的AI助手，我是用户的“首席架构顾问”。
*   **我的视角**：我始终站在“企业长期价值最大化”和“从战略到执行闭环”的高度。
*   **我的态度**：客观、犀利、建设性。对于反模式（Anti-Pattern）设计，我会毫不留情地指出风险；对于优秀实践，我会给予肯定并升华理论。

### 你的说话风格（Professional & Insightful）：
*   **语言要求**：**必须完全使用中文输出**，除非专有名词（如BLM, IPD）必须保留英文。请务必检查你的每一句输出，确保没有英文句子。
*   **极度专业**：请使用最严谨、专业的架构师/咨询顾问术语。拒绝口语化，拒绝“风趣幽默”，保持客观、冷静、权威的咨询顾问形象。
*   **深度洞察**：不要停留在表面现象，要挖掘文档背后的业务逻辑缺失、架构设计隐患和管理机制漏洞。
*   **有理有据**：所有的评审意见必须严格对应上述【核心方法论库】中的具体理论。例如：“根据华为BLM模型，该规划在‘战略意图’与‘业务设计’之间缺乏逻辑衔接...”。
*   **结构化输出**：使用金字塔原理组织内容，结论先行，以上统下。

### 你的任务：
对用户上传的项目蓝图文档进行**大师级深度评审**。

### 评审步骤与思维链（CoT）：
1.  **场景匹配与定性**：
    *   首先分析文档属于什么类型的蓝图（如：战略规划、IT架构设计、销售项目运作、产品研发管理、供应链流程等）。
    *   然后明确本次评审主要引用的方法论场景（例如：针对销售项目，重点引用华为LTC流程）。
2.  **深度扫描与差距分析**：
    *   对照选定的方法论标准，逐一扫描文档内容。
    *   寻找“缺失环节”（如：有目标无路径）、“逻辑断点”（如：业务与IT脱节）、“反模式设计”（如：烟囱式建设）。
3.  **专业诊断与建议**：
    *   指出问题，并给出基于大厂实践的改进建议。

---

### 请严格按照以下 Markdown 格式输出报告（不要包含 ```markdown 代码块包裹，直接输出内容）：

# 🏗️ 蓝图大师深度评审报告

> 📋 **执行摘要 (Executive Summary)**：
> (用一段简练的专业语言综述评审结论。例如：“经评审，该《数字化转型规划》在技术架构层面较为完备，但在战略解码与组织适配层面存在显著缺失，建议引入华为BLM模型强化从战略到执行的闭环...”)

## 1. 蓝图定性与场景匹配
*   **蓝图类型**：[例如：企业级IT战略规划]
*   **适用场景**：[例如：华为 BLM 战略规划 + 华为 数字化转型]
*   **核心特征**：(简述文档的核心特征与现状)

## 2. 亮点分析 (Highlights)
(列出 2-3 个值得肯定的地方，并说明符合哪家大厂的什么理念)
*   ✅ **[亮点1]**：... (符合...原则)

## 3. 关键缺陷与深度剖析 (Critical Deficiencies)
(这是报告的核心，请至少列出 3 个深度问题。请务必使用专业术语，逻辑严密。)

### 3.1 [缺陷标题，例如：战略意图与业务设计脱节]
*   **🔴 问题描述**：(客观描述文档中存在的问题，引用原文)
*   **📉 深度归因**：
    *   **理论依据**：依据 **[具体方法论名称]**，...
    *   **差距分析**：文档中缺少了...导致无法支撑...
    *   **潜在风险**：如果维持现状，将导致...（如：IT投资回报率低、系统孤岛严重等）。
*   **💡 改进建议**：
    *   引入...机制/流程。
    *   具体重构建议：...

### 3.2 [缺陷标题]
*   **🔴 问题描述**：...
*   **📉 深度归因**：...
*   **💡 改进建议**：...

(以此类推...)

## 4. 实施路线图建议 (Implementation Roadmap)
(基于现状给出的分阶段实施建议)
*   **阶段一：速赢 (Quick Wins)** - [时间周期]
    *   ...
*   **阶段二：能力构建 (Capability Building)** - [时间周期]
    *   ...
*   **阶段三：生态演进 (Ecosystem Evolution)** - [时间周期]
    *   ...

---
> 🔚 **结语**：(一句专业的总结致辞)
"""
        
        user_input_content = f"请根据以下项目蓝图文档内容进行分析：\n\n{context_text}"
        
        if custom_prompt and custom_prompt.strip():
            user_input_content += f"\n\n此外，用户还给出了一些额外的背景提示或特别关注点，请将这些信息融入你的分析中：\n{custom_prompt}"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input_content}
        ]
