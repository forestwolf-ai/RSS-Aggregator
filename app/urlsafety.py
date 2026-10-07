"""URL 安全校验（SSRF 防护）。

抓取目标完全由用户输入决定（订阅地址、文章链接、OPML 文件），因此必须限制
协议与目标地址，避免把服务端变成探测内网的工具（例如云环境的
169.254.169.254 元数据接口）。

策略：
* 只允许 http / https；
* 目标是字面量 IP 或域名解析结果落在回环、私有、链路本地、保留网段时拒绝；
* 解析失败时放行——连不上的域名本来也抓不到内容，放行不会扩大攻击面，
  否则会把「DNS 临时故障的源」和「OPML 里的离线订阅」全部误杀。
  注意这留下了 DNS rebinding 的理论窗口（先解析到公网、连接时再解析到内网），
  对公网暴露的部署建议在网络层再加出站白名单。
"""
import ipaddress
import logging
import socket
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

ALLOWED_SCHEMES = ("http", "https")
DEFAULT_PORTS = {"http": 80, "https": 443}

# 这些主机名一律视为本机，不必等 DNS
_LOCAL_HOSTNAMES = {"localhost", "localhost.localdomain", "ip6-localhost", "ip6-loopback"}


def _default_resolver(host, port):
    """返回主机名解析出的所有 IP。"""
    infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    return [info[4][0] for info in infos]


def _is_internal(address):
    try:
        ip = ipaddress.ip_address(address.split("%")[0])  # 去掉 IPv6 的 scope id
    except ValueError:
        return True  # 无法解析成 IP 时按不安全处理
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def is_safe_url(url, allow_private=False, resolver=None):
    """判断该 URL 是否允许服务端主动请求。"""
    if not url or not isinstance(url, str):
        return False

    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return False

    scheme = (parts.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        return False

    host = parts.hostname
    if not host:
        return False

    try:
        port = parts.port
    except ValueError:  # 非法端口（例如 http://host:abc/）
        return False
    if port is not None and not 0 < port < 65536:
        return False

    if allow_private:
        return True

    if host.lower() in _LOCAL_HOSTNAMES:
        return False

    try:
        address = ipaddress.ip_address(host.split("%")[0])
    except ValueError:
        pass  # 不是字面量 IP，需要走 DNS
    else:
        return not _is_internal(str(address))

    resolve = resolver or _default_resolver
    try:
        addresses = resolve(host, port or DEFAULT_PORTS[scheme])
    except (socket.gaierror, OSError, UnicodeError) as exc:
        logger.debug("域名解析失败，按可抓取处理 %s: %s", host, exc)
        return True

    if not addresses:
        return True
    for address in addresses:
        if _is_internal(address):
            logger.warning("拒绝内网地址 %s（来自 %s）", address, url)
            return False
    return True
