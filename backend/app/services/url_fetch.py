import asyncio, ipaddress, socket
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
from app.core.config import get_settings

def validate_public_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only valid http and https URLs are allowed")
    host = parsed.hostname.lower()
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("Local and private network URLs are not allowed")
    try:
        addresses = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("URL host could not be resolved") from exc
    for result in addresses:
        if not ipaddress.ip_address(result[4][0]).is_global:
            raise ValueError("URLs resolving to private or reserved IP addresses are not allowed")

async def fetch_url_text(url: str):
    settings = get_settings()
    current = url
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, follow_redirects=False,
                                 headers={"User-Agent": "TuriumKnowledgeInbox/1.0"}) as client:
        for _ in range(4):
            await asyncio.to_thread(validate_public_url, current)
            async with client.stream("GET", current) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get("location")
                    if not location:
                        response.raise_for_status()
                    current = urljoin(current, location)
                    continue
                response.raise_for_status()
                ctype = response.headers.get("content-type", "").lower()
                if ctype and not any(t in ctype for t in ("text/html", "text/plain", "application/xhtml")):
                    raise ValueError("URL must return HTML or plain text")
                parts, size = [], 0
                async for part in response.aiter_bytes():
                    size += len(part)
                    if size > settings.max_url_bytes:
                        raise ValueError("Page exceeds the maximum download size")
                    parts.append(part)
                html = b"".join(parts).decode(response.encoding or "utf-8", errors="replace")
                break
        else:
            raise ValueError("Too many redirects")
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
        node.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else urlparse(current).netloc
    content = soup.get_text(" ", strip=True)
    if len(content.strip()) < 30:
        raise ValueError("Could not extract enough readable text from this page")
    return title[:500], content
