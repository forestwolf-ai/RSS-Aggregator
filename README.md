# RSS Aggregator

A feature-rich, self-hosted RSS feed aggregator. Supports scheduled fetching, OPML import/export, full-text extraction, keyword search and filtering, email notifications, and a bilingual web interface (English / Chinese). Ideal for personal or team use in information aggregation, content monitoring, and reading management.

---
[English](#README.md) | [中文](#中文)

## ✨ Features

### Core Features
- **RSS Source Management**: Add, delete, and edit RSS feeds with categories (e.g., "Tech", "News", "Blogs").
- **Scheduled Fetching**: Powered by APScheduler, each source can have its own update interval (minimum 5 minutes).
- **Persistent Storage**: Uses SQLite (default) or PostgreSQL via SQLAlchemy.
- **Web Interface**: Flask-based responsive UI with English/Chinese language switching.
- **Article Reading**: Displays title, summary, publish time, and links to the original article.

### Advanced Features
- **OPML Import/Export**: One-click migration of feed subscriptions, compatible with mainstream RSS readers.
- **Full-Text Extraction**: For sources that provide only summaries, attempts to extract the full article text using BeautifulSoup.
- **Keyword Filtering & Full-Text Search**: Search across title, summary, and content, with optional filtering by source and unread status.
- **Custom Update Frequency**: Each source can have its own fetch interval.
- **Email Notifications**: Configure SMTP to receive email alerts when new articles are fetched.
- **Multi-User Support**: The current version focuses on single-user/self-hosting; can be extended by deploying multiple instances.

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Web Framework | Flask |
| Database | SQLite / PostgreSQL (through SQLAlchemy) |
| RSS Parsing | feedparser |
| Scheduled Tasks | APScheduler |
| Full-Text Extraction | BeautifulSoup4 + requests |
| Email Notifications | smtplib |
| Internationalization | Custom i18n module |
| Deployment | Docker / Docker Compose |

---

## 📁 Project Structure

```
rss_aggregator/
├── app/
│   ├── __init__.py          # Application initialization
│   ├── config.py            # Configuration loader
│   ├── database.py          # Database instance
│   ├── models.py            # ORM models
│   ├── fetcher.py           # RSS fetching with retry logic
│   ├── scheduler.py         # Background scheduler
│   ├── i18n.py              # English/Chinese translations
│   ├── opml.py              # OPML import/export
│   ├── fulltext.py          # Full-text extraction
│   ├── search.py            # Search and filter
│   ├── notifications.py     # Email notifications
│   └── web/
│       ├── __init__.py
│       ├── routes.py        # Routes and views
│       └── templates/
│           ├── base.html
│           └── index.html
├── main.py                  # Entry point
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md                # English documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip
- (Optional) Docker and Docker Compose

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rss_aggregator.git
   cd rss_aggregator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure**
   Edit `config.yaml` to set language, database, email, etc.

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open the web interface**
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ⚙️ Configuration

The configuration file is `config.yaml`:

```yaml
app:
  name: "RSS Aggregator"
  language: "en"           # Default language: en or zh
  timezone: "Asia/Shanghai"

database:
  url: "sqlite:///rss.db"  # Or PostgreSQL: postgresql://user:pass@localhost/dbname

scheduler:
  enabled: true
  default_interval: 30     # Default update interval (minutes)

server:
  host: "0.0.0.0"
  port: 5000
  debug: false

notifications:
  email:
    enabled: false         # Set to true and fill in SMTP details to enable
    smtp_server: "smtp.example.com"
    smtp_port: 587
    username: "user@example.com"
    password: "password"
    from_addr: "user@example.com"
    to_addr: "user@example.com"
```

---

## 🧩 Usage

### Adding an RSS Source
In the home page form, enter:
- **Name**: for easy identification
- **URL**: RSS or Atom feed address
- **Category**: e.g., "News", "Blogs"
- **Update Interval**: minutes (minimum 5)

Submitting fetches immediately, then the source updates according to the interval.

### Search and Filter
Use the search bar to enter keywords. You can optionally filter by a specific source and show only unread articles.

### OPML Import/Export
- **Export**: Click "Export OPML" to download an XML file containing all sources.
- **Import**: Upload an OPML file; categories are automatically recognized and imported.

### Email Notifications
1. Enable `email.enabled` in `config.yaml` and fill in the SMTP details.
2. When new articles are fetched, an email notification is sent automatically.

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
docker compose up -d
```

The application will be available at `http://localhost:5000`. The `./data` volume persists the SQLite database.

### Custom Configuration
Mount your own `config.yaml`:

```yaml
services:
  rss:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./data:/app/data
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Issues and pull requests are welcome. Please keep the code style consistent and test locally.

---

## 📞 Contact

- GitHub Issues: https://github.com/forestwolf-ai/RSS-Aggregator/issues

---

#中文
# RSS Aggregator

一个功能丰富、可自托管的 RSS 订阅聚合器。支持定时抓取、OPML 导入导出、全文提取、关键词搜索过滤、邮件通知，并提供中英文双语 Web 界面。适合个人或团队用于信息聚合、内容监控和阅读管理。

---

[English](#README.md) | [中文](#中文)

## ✨ 功能特性

### 核心功能
- **RSS 源管理**：添加、删除、编辑 RSS 源，支持分类（如“科技”“新闻”“博客”）。
- **定时抓取**：基于 APScheduler，每个源可独立设置更新间隔（最低 5 分钟）。
- **数据持久化**：使用 SQLite（默认）或 PostgreSQL 存储，数据安全可靠。
- **Web 界面**：基于 Flask 的响应式界面，支持中英文切换。
- **文章阅读**：展示标题、摘要、发布时间，点击跳转原文。

### 高级功能
- **OPML 导入/导出**：一键迁移订阅源，兼容主流 RSS 阅读器。
- **全文提取**：对部分只提供摘要的源，尝试自动抓取网页正文（基于 BeautifulSoup）。
- **关键词过滤与全文搜索**：支持按标题、摘要、正文搜索，可结合源分类和未读状态过滤。
- **自定义更新频率**：每个源可单独配置抓取间隔，灵活控制资源占用。
- **邮件推送通知**：配置 SMTP 后，抓取到新文章可自动发送邮件提醒。
- **多用户支持**：可通过部署多个实例或后续扩展实现，当前版本聚焦单用户/自托管。

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
│   ├── database.py          # 数据库实例
│   ├── models.py            # ORM 模型
│   ├── fetcher.py           # RSS 抓取与重试
│   ├── scheduler.py         # 定时任务调度
│   ├── i18n.py              # 中英文翻译
│   ├── opml.py              # OPML 导入导出
│   ├── fulltext.py          # 全文提取
│   ├── search.py            # 搜索过滤
│   ├── notifications.py     # 邮件通知
│   └── web/
│       ├── __init__.py
│       ├── routes.py        # 路由与视图
│       └── templates/
│           ├── base.html
│           └── index.html
├── main.py                  # 程序入口
├── config.yaml              # 配置文件
├── requirements.txt         # Python 依赖
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md                # 英文说明
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

3. **修改配置**
   编辑 `config.yaml`，根据需要调整语言、数据库、邮件等参数。

4. **启动应用**
   ```bash
   python main.py
   ```

5. **访问界面**
   打开浏览器访问 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ⚙️ 配置说明

配置文件为 `config.yaml`，示例：

```yaml
app:
  name: "RSS Aggregator"
  language: "zh"           # 默认语言：en 或 zh
  timezone: "Asia/Shanghai"

database:
  url: "sqlite:///rss.db"  # 或 PostgreSQL: postgresql://user:pass@localhost/dbname

scheduler:
  enabled: true
  default_interval: 30     # 默认更新间隔（分钟）

server:
  host: "0.0.0.0"
  port: 5000
  debug: false

notifications:
  email:
    enabled: false         # 开启邮件通知后，下面必填
    smtp_server: "smtp.example.com"
    smtp_port: 587
    username: "user@example.com"
    password: "password"
    from_addr: "user@example.com"
    to_addr: "user@example.com"
```

---

## 🧩 功能使用

### 添加 RSS 源
在首页表单中输入：
- **名称**：便于识别
- **URL**：RSS 或 Atom 地址
- **分类**：如“新闻”“博客”
- **更新间隔**：分钟数，最低 5

提交后立即抓取一次，随后按间隔自动更新。

### 搜索与过滤
顶部搜索框输入关键词，可选择特定源和“仅未读”状态。

### OPML 导入导出
- **导出**：点击“导出 OPML”，下载包含所有源的 XML 文件。
- **导入**：选择 OPML 文件上传，自动识别分类并导入。

### 邮件通知
1. 在 `config.yaml` 中启用 `email.enabled` 并填写 SMTP 信息。
2. 每次抓取到新文章后，系统自动发送邮件通知。

---

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
docker compose up -d
```

应用将在 `http://localhost:5000` 启动。数据卷 `./data` 用于持久化 SQLite 数据库。

### 自定义配置
挂载你的 `config.yaml`：

```yaml
services:
  rss:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./data:/app/data
```

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](#LICENSE) 文件。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。请确保代码风格一致，并通过本地测试。

---

## 📞 联系方式

- GitHub Issues：https://github.com/forestwolf-ai/RSS-Aggregator/issues
