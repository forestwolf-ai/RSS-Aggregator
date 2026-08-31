# RSS Aggregator

[English](README.md) | [中文](README-zh.md)

A feature-rich, self-hosted RSS feed aggregator with scheduled fetching, OPML import/export, full-text extraction, search, email notifications, and a bilingual web interface. Ideal for personal or team use in information aggregation, content monitoring, and reading management.

---

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
- **Docker Deployment**: Dockerfile and docker-compose.yml provided for easy deployment.

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
│   ├── models.py            # ORM models (Source, Article)
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
│           ├── index.html   # Main page template
├── main.py                  # Entry point
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
├── Dockerfile
├── docker-compose.yml
├── CHANGELOG.md             # Version history
├── .gitignore
└── README.md                # This file
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
   Copy `config.yaml` and edit it according to your needs (see [Configuration](#configuration)).

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open the web interface**
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ⚙️ Configuration

The configuration file is `config.yaml`. Below is a sample with comments:

```yaml
app:
  name: "RSS Aggregator"       # Application name
  language: "en"               # Default language: en or zh
  timezone: "Asia/Shanghai"    # Timezone for scheduler

database:
  url: "sqlite:///rss.db"      # SQLite or PostgreSQL URL
  # Example PostgreSQL: postgresql://user:password@localhost/dbname

scheduler:
  enabled: true                # Enable/disable automatic fetching
  default_interval: 30         # Default update interval (minutes)

server:
  host: "0.0.0.0"              # Listen address
  port: 5000
  debug: false

notifications:
  email:
    enabled: false             # Enable email notifications
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

On the home page, fill in the form:
- **Name**: A friendly name for the source.
- **URL**: The RSS or Atom feed URL.
- **Category**: Optional category, e.g., "News", "Tech".
- **Update Interval**: Minutes between automatic fetches (minimum 5).

Click submit; the source will be fetched immediately and then updated according to the interval.

### Searching and Filtering

Use the search bar at the top of the page:
- Enter keywords to search across title, summary, and full text.
- Optionally filter by a specific source.
- Check "Unread only" to see only unread articles.

### OPML Import/Export

- **Export**: Click "Export OPML" to download an XML file containing all your sources.
- **Import**: Click "Import OPML" and choose an OPML file; sources will be added automatically, preserving categories.

### Email Notifications

To receive email alerts when new articles are fetched:
1. Set `notifications.email.enabled` to `true` in `config.yaml`.
2. Fill in your SMTP server details and recipient addresses.
3. When a source is fetched (manually or scheduled) and new articles are found, an email will be sent.

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
docker compose up -d --build
```

This will build the image and start the container in detached mode. The application will be available at `http://localhost:5000`.

### Data Persistence

The SQLite database is stored in the `./data` volume, and the configuration file is mounted read-only. To customize settings, edit `config.yaml` before starting.

### Custom Configuration

Override the default compose file if needed:

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

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Issues and pull requests are welcome. Please ensure code style consistency and test locally.

---

## 📞 Contact

- GitHub Issues: https://github.com/forestwolf-ai/RSS-Aggregator/issues
