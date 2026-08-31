# RSS 聚合器

[English](README.md) | [中文](README-zh.md)

一个功能丰富、可自托管的 RSS 订阅聚合器。支持定时抓取、OPML 导入导出、全文提取、关键词搜索过滤、邮件通知，并提供中英文双语 Web 界面。适合个人或团队用于信息聚合、内容监控和阅读管理。

---

## ✨ 功能特性

### 核心功能

- **RSS 源管理**：添加、删除、编辑 RSS 源，支持分类（如“科技”“新闻”“博客”）。
- **定时抓取**：基于 APScheduler，每个源可独立设置更新间隔（最低 5 分钟）。
- **数据持久化**：使用 SQLite（默认）或 PostgreSQL，通过 SQLAlchemy 实现。
- **Web 界面**：基于 Flask 的响应式界面，支持中英文切换。
- **文章阅读**：展示标题、摘要、发布时间，点击跳转原文。

### 高级功能

- **OPML 导入/导出**：一键迁移订阅源，兼容主流 RSS 阅读器。
- **全文提取**：对只提供摘要的源，尝试自动抓取网页正文（基于 BeautifulSoup）。
- **关键词过滤与全文搜索**：支持按标题、摘要、正文搜索，可结合源分类和未读状态过滤。
- **自定义更新频率**：每个源可单独配置抓取间隔，灵活控制资源占用。
- **邮件推送通知**：配置 SMTP 后，抓取到新文章可自动发送邮件提醒。
- **Docker 部署**：提供 Dockerfile 和 docker-compose.yml，方便快速部署。

---

## 🛠 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | Flask |
| 数据库 | SQLite / PostgreSQL（通过 SQLAlchemy） |
| RSS 解析 | feedparser |
| 定时任务 | APScheduler |
| 全文提取 | BeautifulSoup4 + requests |
| 邮件通知 | smtplib |
| 国际化 | 自定义 i18n 模块 |
| 部署 | Docker / Docker Compose |

---

## 📁 项目结构

```
rss_aggregator/
├── app/
│   ├── __init__.py          # 应用初始化
│   ├── config.py            # 配置加载器
│   ├── models.py            # ORM 模型（Source、Article）
│   ├── fetcher.py           # RSS 抓取与重试逻辑
│   ├── scheduler.py         # 后台调度器
│   ├── i18n.py              # 中英文翻译
│   ├── opml.py              # OPML 导入导出
│   ├── fulltext.py          # 全文提取
│   ├── search.py            # 搜索过滤
│   ├── notifications.py     # 邮件通知
│   └── web/
│       ├── __init__.py
│       ├── routes.py        # 路由与视图
│       └── templates/
│           ├── index.html   # 主页面模板
├── main.py                  # 程序入口
├── config.yaml              # 配置文件
├── requirements.txt         # Python 依赖
├── Dockerfile
├── docker-compose.yml
├── CHANGELOG.md             # 版本历史
├── .gitignore
└── README.md                # 本文件（英文版）
```

---

## 🚀 快速开始

### 环境要求

- Python 3.9 或更高版本
- pip
- （可选）Docker 和 Docker Compose

### 本地运行

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/rss_aggregator.git
   cd rss_aggregator
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置**
   复制并编辑 `config.yaml`，根据需要设置语言、数据库、邮件等（见[配置说明](#配置说明)）。

4. **启动应用**
   ```bash
   python main.py
   ```

5. **访问界面**
   打开浏览器访问 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ⚙️ 配置说明

配置文件为 `config.yaml`，示例及注释如下：

```yaml
app:
  name: "RSS Aggregator"       # 应用名称
  language: "zh"               # 默认语言：en 或 zh
  timezone: "Asia/Shanghai"    # 调度器时区

database:
  url: "sqlite:///rss.db"      # SQLite 或 PostgreSQL 连接字符串
  # PostgreSQL 示例：postgresql://user:password@localhost/dbname

scheduler:
  enabled: true                # 是否启用自动抓取
  default_interval: 30         # 默认更新间隔（分钟）

server:
  host: "0.0.0.0"              # 监听地址
  port: 5000
  debug: false

notifications:
  email:
    enabled: false             # 是否启用邮件通知
    smtp_server: "smtp.example.com"
    smtp_port: 587
    username: "user@example.com"
    password: "password"
    from_addr: "user@example.com"
    to_addr: "user@example.com"
```

---

## 🧩 使用说明

### 添加 RSS 源

在首页表单中输入：
- **名称**：便于识别的源名称。
- **URL**：RSS 或 Atom 地址。
- **分类**：可选，如“新闻”“科技”。
- **更新间隔**：自动抓取间隔（分钟，最低 5）。

提交后立即抓取一次，随后按间隔自动更新。

### 搜索与过滤

使用页面顶部的搜索框：
- 输入关键词，搜索范围包括标题、摘要和正文。
- 可选按特定源过滤。
- 勾选“仅未读”只查看未读文章。

### OPML 导入导出

- **导出**：点击“导出 OPML”下载包含所有源的 XML 文件。
- **导入**：点击“导入 OPML”选择文件上传，源会自动添加并保留分类。

### 邮件通知

要接收新文章邮件提醒：
1. 在 `config.yaml` 中将 `notifications.email.enabled` 设为 `true`。
2. 填写 SMTP 服务器信息及收件地址。
3. 当源被抓取（手动或定时）并发现新文章时，系统自动发送邮件。

---

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
docker compose up -d --build
```

该命令会构建镜像并后台启动容器。应用将在 `http://localhost:5000` 可用。

### 数据持久化

SQLite 数据库存储在 `./data` 卷中，配置文件以只读方式挂载。如需自定义设置，请先编辑 `config.yaml`。

### 自定义配置

如需覆盖默认 compose 文件，可自行修改：

```yaml
services:
  rss:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - ./data:/app/data
    restart: unless-stopped
```

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。请保持代码风格一致，并在本地测试。

---

## 📞 联系方式

- GitHub Issues：https://github.com/forestwolf-ai/RSS-Aggregator/issues
