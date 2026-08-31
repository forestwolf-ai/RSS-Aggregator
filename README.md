# RSS Aggregator

A feature-rich, self-hosted RSS feed aggregator. Supports scheduled fetching, OPML import/export, full-text extraction, keyword search and filtering, email notifications, and a bilingual web interface (English / Chinese). Ideal for personal or team use in information aggregation, content monitoring, and reading management.

---
[English](README.md) | [中文](README-zh.md)

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
## 📞 联系方式

- GitHub Issues：https://github.com/forestwolf-ai/RSS-Aggregator/issues
