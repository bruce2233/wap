# WAP Paper Page Generation Prompt

Use this prompt for Codex/agent runs to generate a **new paper page** in the WAP repo. It requires a GitHub push to `bruce2233/wap` and produces **four standalone pages** (HS/Grad × EN/中文).

```
你是一个负责为 WAP (Web Any Paper) 生成单篇论文网页的工程型 agent。
目标：为指定论文生成 4 个独立网页版本（高中/研究生 × 英文/中文），并接入 WAP 索引页。
注意：每个论文页面是独立的 HTML/CSS/JS，不使用 JSON 驱动内容。

输入参数（由用户提供）：
- paper_query: 论文标题/作者/ArXiv/DOI
- slug: URL slug（若未提供请从标题生成）
- repo_path: WAP 仓库路径（默认 /Users/yunpeng.zhang2/app/wap）
- repo_name: GitHub 仓库名（默认 bruce2233/wap）
- domain: 站点域名（默认 https://wap.bryan2233.top）

严格要求：
1) 必须使用 web.run 搜索并核实论文信息（标题/作者/日期/摘要/方法/实验/结果/限制/资源链接）。
2) 必须生成 4 个版本页面：
   - hs-en.html（高中英文）
   - grad-en.html（研究生英文）
   - hs-zh.html（高中中文）
   - grad-zh.html（研究生中文）
3) 每个版本都必须包含完整内容区块（而不是共享同一页面切换）。
4) 页面必须是静态页面（HTML/CSS/JS），不使用框架。
5) 将论文添加到首页索引中（WAP index.html）。
6) 必须提交并推送到指定 GitHub 仓库 repo_name（默认 bruce2233/wap）。
7) 不要输出或打印任何密钥；若需要认证，使用环境变量（如 GITHUB_TOKEN/VERCEL_TOKEN）。

页面结构建议（四个版本都包含）：
- Hero（标题、简短一句话摘要）
- Paper facts（作者、日期、venue、arXiv/DOI）
- Problem setup / 背景
- Method / 方法
- Experiments & Results / 实验与结果（包含指标与关键数值）
- Limitations / 局限
- Resources / 资源（论文、PDF、项目页、代码、数据集）
- Suggested citation / 推荐引用
- Footer（提示这是该版本：HS/Grad + EN/中文）

风格要求：
- 每个 paper 可独立设计，布局清晰，信息密度高但易读。
- 视觉风格大胆、有层次，避免模板化。
- 使用和 WAP 风格兼容的字体（如 Space Grotesk + Noto Sans SC）或自选合理搭配。

目录/文件要求：
/papers/<slug>/
  index.html        # 版本选择/或默认入口（可跳转到 hs-en.html）
  hs-en.html
  grad-en.html
  hs-zh.html
  grad-zh.html
  styles.css
  script.js         # 可用于高亮/导航/滚动等轻交互

WAP 路由：
- /<slug> -> /papers/<slug>/index.html（由 vercel.json rewrites 已配置）

索引页更新：
- 在 repo_path/index.html 中增加一张卡片：
  - href="/<slug>"
  - data-title/data-tags/data-arxiv
  - 简短双语摘要（HS/Grad 各一行）

流程步骤（必须执行）：
1) 用 web.run 搜索 paper_query，打开权威来源（arXiv/出版社/项目页/代码/数据集）。
2) 提取并核对信息，记录来源链接。
3) 生成 4 个页面内容（HS 与 Grad 信息深度明显不同；中英语言准确）。
4) 生成 /papers/<slug>/index.html：提供 4 个版本入口 + 简短导语。
5) 写入 styles.css 和 script.js（每个纸可以自定义风格，但保持可读性）。
6) 更新 WAP 首页索引（添加新卡片）。
7) git add/commit/push 到 repo_name（默认 bruce2233/wap）。
8) 在输出中给出最终可访问 URL（domain + slug + 具体版本文件路径）。

输出格式：
- 说明你读取了哪些 sources（列出链接，不要引用 token）
- 给出生成/修改的文件清单
- 给出最终访问 URL 列表：
  - https://domain/<slug>
  - https://domain/papers/<slug>/hs-en.html
  - https://domain/papers/<slug>/grad-en.html
  - https://domain/papers/<slug>/hs-zh.html
  - https://domain/papers/<slug>/grad-zh.html
```
