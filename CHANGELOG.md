# Changelog

本项目所有值得注意的变更都记录在此文件。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循语义化版本。

## [1.4.0] - 2026-10-07

第二轮审查版本：在 v1.3 基础上又修复 **8 项缺陷**，其中包含一个可绕过 SSRF 防护的
安全漏洞。新增 8 个针对性用例与 1 个真实进程级验证脚本，全部通过。

### 安全

- **修复可绕过 SSRF 防护的重定向漏洞（高危）**：原来只校验订阅地址本身，
  而 `requests` 默认自动跟随重定向；一个公网 feed 只要返回
  `302 Location: http://169.254.169.254/...` 就能让服务端去访问内网，
  防护形同虚设。现在改为不自动跟随重定向，逐跳校验后再跳（最多 5 跳），
  正文抽取路径同样处理。
- **限制响应体大小**：恶意源可以返回几十 GB 响应，原来会被整份读入内存导致进程被打爆。
  新增 `fetch.max_bytes`（默认 8 MB）与 `fulltext.max_bytes`（默认 2 MB），超出即截断。

### 修复

- **调试模式 / 多进程下调度器重复启动**：`flask run --debug` 会派生父/子两个进程，
  两者都会执行引导逻辑；原来只判断配置里的 `server.debug`，而 `--debug` 时该值仍是
  `false`，实测两个进程各起一个调度器（重复抓取、重复发信）。
  现在同时判断 `FLASK_DEBUG` 环境变量与 `app.debug`，并新增逐进程开关
  `RSS_AGGREGATOR_SCHEDULER=off`（多 worker 部署时只让一个进程跑调度器）。
- **`/healthz` 不校验数据库**：原来无条件返回 `ok`，数据库或表结构损坏时容器仍被判定为
  健康、不会重启；现在会真的查询 `source` / `article` 表，失败返回 503。
- **`read` 为 NULL 的文章在「只看未读」里消失**：过滤条件只有 `read IS false`，
  历史数据或外部写入的 NULL 行会被静默隐藏；现在 NULL 与 false 一并视为未读。
- **通知邮件列出并未入库的文章**：并发冲突导致部分文章被跳过时，
  邮件正文仍会列出全部候选条目；现在只列出真正写入数据库的文章。
- **正文抽取按原始字节解析**：交给 BeautifulSoup 的是响应字节而非
  `response.text`，由它按 meta/BOM 判断编码，避免 GBK 等页面正文乱码。

### 修复 · 打包遗漏（v1.3 上传时丢失）

- 补回 `.dockerignore`（缺失会把 `.git`、本地数据库打进镜像）。
- 补回 `.gitignore` 中的运行时忽略项（`data/`、`*.db`、`*.sqlite3`、`*.log`、`logs/`）。
- 删除 `app/.dockerfile`：它已被仓库根目录的 `Dockerfile` 取代，
  留着会让 `docker build` 的行为取决于使用哪一份，容易误构建。
- 补上 `tests/` 测试目录（v1.3 未包含）。

### 测试

| 套件 | 结果 |
|---|---|
| `tests/test_bugfixes.py`（第一轮回归，30 例） | 30 / 30 通过 |
| `tests/test_v13_bugs.py`（本轮新增，8 例） | 8 / 8 通过 |
| `tests/test_e2e_smoke.py`（端到端） | 21 / 21 通过 |
| `tests/test_debug_reloader.py`（`flask run --debug` 进程级验证） | 修复前 2 个调度器 → 修复后 1 个 |

测试随仓库一起分发，只用标准库 `unittest.mock`，不引入额外依赖：

```bash
python tests/test_bugfixes.py        # 第一轮 30 项回归
python tests/test_v13_bugs.py        # 本轮 8 项
python tests/test_e2e_smoke.py       # 端到端（会真的起一次服务）
python tests/test_debug_reloader.py  # 进程级：确认调度器只启动一次
```

镜像里不包含 `tests/`（见 `.dockerignore`）。Dockerfile 在构建期额外做一次模块导入检查，
确保镜像内所有模块都能正常加载。

### 配置新增

```yaml
fetch:
  max_bytes: 8388608       # feed 响应体上限（字节）
fulltext:
  max_bytes: 2097152       # 文章页响应体上限（字节）
```

多进程部署时，除运行调度器的那个进程外，其余进程设置环境变量
`RSS_AGGREGATOR_SCHEDULER=off`。

## [1.3.0] - 2026-10-07

本次为缺陷修复版本：共修复 **30 项缺陷**，其中 7 项导致程序在修复前**完全无法使用**。
同时新增 30 个回归用例与 21 项端到端冒烟检查，全部通过。

### 修复 · 致命（修复前程序不可用）

- **`create_app()` 必然崩溃，应用无法启动**：`app/config.py` 的 `_load_config()` 把配置写在
  实例属性上，而 `get()` / `to_flask_config()` 读的是类属性（恒为 `None`），
  导致 `to_flask_config()` 抛 `TypeError: argument of type 'NoneType' is not iterable`。
- **`ConfigLoader.get()` 恒返回默认值**：同上的类/实例属性错位；异常被
  `except (KeyError, TypeError)` 静默吞掉，所有通过它读取的配置都失效。
- **每个页面都返回 500**：模板位于 `app/web/templates/`，但蓝图未声明 `template_folder`，
  Jinja 只会在 `app/templates/` 查找 → `TemplateNotFound: index.html`。
- **`flash()` 一律 500**：从未设置 `SECRET_KEY`，`RuntimeError: The session is unavailable
  because no secret key was set`，表现为「添加源」写库成功却返回 500。
- **定时抓取 100% 失败**：`fetch_source` 被直接交给 APScheduler，
  而应用上下文只在注册任务时推入；任务在调度线程执行时 `Source.query` 抛
  `RuntimeError: Working outside of application context`。
- **OPML 导入必然失败**：使用了 lxml 专有的 `outline.getparent()`，
  而模块导入的是标准库 `xml.etree.ElementTree`，异常被宽泛捕获后恒返回 `(0, 1)`。
- **抓取失败不回滚**：失败分支只记日志便返回，已 `add` 未提交的文章残留在 session 中，
  会被之后任意一次 `commit()` 悄悄写进数据库。

### 修复 · 安全

- **新增 SSRF 防护**（`app/urlsafety.py`）：只允许 http/https，
  拒绝回环、私有、链路本地与保留地址；已接入抓取、正文抽取、OPML 导入、新增源四条路径。
  纯内网场景可用 `security.allow_private_networks` 放开。
- **改状态的接口不再接受 GET**：`delete_source` / `refresh_source` 由 GET 改为 POST
  （原来浏览器预取、`<img>` 标签或爬虫即可删库）。
- **新增跨站请求来源校验**（`app/security.py`）：POST 的 `Origin`/`Referer` 与本站不一致
  直接 403，可通过 `security.csrf_origin_check` 关闭。
- **转义 LIKE 通配符**：原来用户输入 `%` 会退化成全表匹配，`_` 会匹配任意单字符。

### 修复 · 数据正确性

- **`Article.link` 增加唯一索引**：原来只靠「先查再插」去重，
  手动刷新（请求线程）与定时任务（调度线程）并发时会重复入库。
- **并发冲突降级重试**：批量提交撞唯一约束时改为逐条 savepoint 重试，不再整批失败。
- **新增 `app/schema.py`**：为已有数据库幂等补索引，并先清理历史重复文章
  （同一 `link` 保留 id 最小的一条），删除条数写入日志。
- **去重查询由 N+1 改为一次批量查询**（按 400 分批，避开 SQLite 变量上限）。

### 修复 · 健壮性与性能

- **新增/导入的源立即注册调度任务**（原来必须重启才会自动更新）。
- **全文抽取加配额与超时**：原来每个没有 `content` 的条目都同步抓一次网页，
  单次请求最坏可阻塞 50 × 10 秒；现由 `fulltext.enabled` / `max_per_fetch` / `timeout` 控制。
- **`interval` 容错解析并强制 ≥ 5 分钟**（原来非数字直接 500，0/负数注册非法任务）。
- **重复 URL 友好提示**，不再抛 `IntegrityError` 500。
- **分页链接保留查询条件**：原来用 `request.view_args`，把 `q` / `source_id` / `unread` / `lang`
  全丢掉，搜索翻到第二页会变成全量列表。
- **`unread` 过滤形成闭环**：新增「标记已读 / 标记未读」接口与按钮
  （原来 `Article.read` 永远是 `False`）。
- **`init_scheduler` 尊重 `scheduler.enabled`**，并在调试重载器父进程中不启动，
  避免起两个调度器重复抓取。
- **引导逻辑移出 `__main__` 分支**：用 gunicorn/uwsgi（`main:app`）或 `flask run` 启动时
  同样会建表（原来首个请求报 no such table）。
- **日志只配置一次**：支持绝对路径与 UTF-8，并让 `app.logger` 只做透传，
  消除每条日志被输出两次的问题。
- **调度器实例移入 `app/scheduler.py`**：同名子模块会把包属性 `app.scheduler` 覆盖成模块对象，
  导致 `from app import scheduler` 拿到模块而非实例。
- **邮件通知支持多收件人**（逗号/分号分隔）、显式 `ehlo()`、配置不全时明确报错。
- **时间统一为 naive UTC**，避开 Python 3.12 起废弃的 `datetime.utcnow()`。
- **页面显示 `app.name`**：原来模板只取 i18n 字典，配置里的应用名配了也不会显示。

### 修复 · 部署与配置

- **`Dockerfile` 移到仓库根目录**：原来位于 `app/.dockerfile`，
  而 compose 使用 `build: .`，`docker compose build` 必然失败。
- **数据库不再随容器重启丢失**：`sqlite:///rss.db` 是相对路径，
  Flask-SQLAlchemy 3.x 会解析到 instance 目录（`/app/instance/rss.db`），
  而 compose 只挂载了 `./data:/app/data`；现改为 `sqlite:///data/rss.db`，
  并在代码中把相对 SQLite 路径锚定到项目根目录（容器内即 `/app/data`）。
- **新增 `.dockerignore`**：避免把 `.git`、本地数据库、`__pycache__` 打进镜像。
- **`docker-compose.yaml`**：移除已废弃的 `version` 字段，补充时区环境变量。
- **修正 README 与仓库不一致之处**：补上缺失的 `CHANGELOG.md`，
  改正 `docker-compose.yml` → `docker-compose.yaml`，更新项目结构与配置示例，
  并显著提示「本项目无鉴权，请勿直接暴露公网」。

### 新增

- `app/urlsafety.py` — 出站 URL 安全校验（SSRF 防护）。
- `app/security.py` — 跨站请求来源校验。
- `app/schema.py` — 建表、幂等补索引、清理重复数据。
- `Dockerfile`（仓库根目录）、`.dockerignore`。
- `/healthz` 健康检查路由，以及容器 `HEALTHCHECK`。
- `tests/test_bugfixes.py` — 30 个回归用例，`python tests/test_bugfixes.py` 直接运行。
- `tests/test_e2e_smoke.py` — 端到端冒烟：真启动 `main.py`、真发 HTTP、真抓本地 RSS 源。

### 变更（可能影响已有部署）

- **数据库默认路径**：`sqlite:///rss.db` → `sqlite:///data/rss.db`。
  升级时请把旧库文件移动到 `data/rss.db`，或在 `config.yaml` 中写回原路径。
- **接口方法**：删除源、刷新源、标记已读/未读改为 **POST**。
- **默认拒绝内网抓取**：需要订阅内网源时设置 `security.allow_private_networks: true`。
- **全文抽取默认每次最多 5 篇**：需要更多请调大 `fulltext.max_per_fetch`。
- **新增配置段**：`fetch`、`fulltext`、`security`、`logging`，以及 `app.secret_key`（可选）。

### 测试

| 套件 | 结果 |
|---|---|
| `tests/test_bugfixes.py`（回归） | 30 / 30 通过 |
| `tests/test_e2e_smoke.py`（端到端） | 21 / 21 通过 |

修复前后对比（同一套回归用例）：

| 阶段 | 结果 |
|---|---|
| 原始代码 | 0 / 27 失败（全部被「应用无法启动」挡住） |
| 仅修 `create_app` | 10 通过 / 19 失败（其余缺陷逐条暴露） |
| 全部修复后 | 30 / 30 通过 |
