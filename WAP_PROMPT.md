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

页面结构（不要强制固定结构）：
- **必须遵循原论文的行文逻辑与章节顺序**来组织网页结构。
- 不要强制出现“方法/实验/局限”等固定标题；仅在论文中真实存在或合理对应时再使用。
- 可以用“贡献/挑战/问题设置/实验设置/结果/消融/讨论/局限”等，但应以论文原始结构为主线。
- 允许为可读性做标题合并或轻微拆分，但不得改变逻辑顺序与重点。
- **保留基础信息区块**（标题/作者/日期/资源链接/引用），其余结构跟随论文。

内容深度要求（关键）：
- 研究生版本必须显著更深入：包含问题挑战、动机、关键假设、核心技术细节、实验设置（数据/指标/对比/消融）、数值结果与对比、失败案例或局限。
- 高中版本保持准确与通俗，但也要完整，不只是一句话摘要。
- 避免“过度简略”，研究生版建议至少 2–3 屏内容量。

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

注意事项（必须遵守）：
- 由于 /<slug> 使用 rewrites 映射到 /papers/<slug>/index.html，页面内所有资源与互链必须使用**绝对路径**：`/papers/<slug>/styles.css`、`/papers/<slug>/script.js`、`/papers/<slug>/hs-en.html` 等。否则在访问 /<slug> 时会错误解析为站点根路径导致 404 或样式/脚本失效。

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
