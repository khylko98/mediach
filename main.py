import os
import re
import sys
import time
from typing import Iterable, Optional, Set
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup, Tag

# ---------------------- CONSTANTS ----------------------

VALID_THREAD_URL = re.compile(
    r"^https?://(?:"
    r"2ch\.[a-z]{2,5}/[a-z]+/res/\d+\.html"
    r"|arhivach\.[a-z]{2,5}/thread/\d+/?"
    r")$",
    re.IGNORECASE,
)

MEDIA_EXTENSIONS = {
    "image": ["jpg", "jpeg", "png", "gif", "webp"],
    "video": ["mp4", "webm", "avi", "mov", "wmv", "mkv"],
}
MEDIA_EXTENSIONS["both"] = MEDIA_EXTENSIONS["image"] + MEDIA_EXTENSIONS["video"]

THREAD_FOLDER_NAME_REGEX = re.compile(r"/(\d+)(?:\.html)?(?:#.*)?/?$")


# ---------------------- UTILITIES ----------------------


def extract_href(tag: Tag) -> Optional[str]:
    """Safely extract an href attribute from a BeautifulSoup tag."""
    href = tag.get("href")

    if isinstance(href, str):
        return href

    if isinstance(href, list) and len(href) == 1 and isinstance(href[0], str):
        return href[0]

    return None


def fetch_html(client: httpx.Client, url: str) -> Optional[str]:
    """Download page HTML or return None on failure."""
    try:
        response = client.get(url)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None


def get_media_links(html: str, base_url: str, extensions: Iterable[str]) -> Set[str]:
    """Parse all media links from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    media_links: Set[str] = set()

    for tag in soup.find_all("a", href=True):
        href = extract_href(tag)
        if not href:
            continue

        href_lower = href.lower()
        if any(href_lower.endswith(ext) for ext in extensions):
            media_links.add(urljoin(base_url, href))

    return media_links


def extract_thread_id(url: str) -> Optional[str]:
    """Extract only the thread numeric ID for folder name."""
    match = THREAD_FOLDER_NAME_REGEX.search(url)
    return match.group(1) if match else None


def download_file(client: httpx.Client, url: str, dest_path: str) -> None:
    """Download a file to a specific path."""
    try:
        with client.stream("GET", url) as resp:
            resp.raise_for_status()

            with open(dest_path, "wb") as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)

        print(f"✓ Saved: {url}")
    except httpx.HTTPError as e:
        print(f"[ERROR] Failed to download {url}: {e}")


# ---------------------- MAIN LOGIC ----------------------


def process_thread(
    client: httpx.Client, thread_url: str, output_root: str, media_option: str
) -> None:
    html = fetch_html(client, thread_url)
    if not html:
        print(f"[WARN] Skipping unreachable thread: {thread_url}")
        return

    extensions = MEDIA_EXTENSIONS[media_option]
    media_links = get_media_links(html, thread_url, extensions)

    if not media_links:
        print(f"[WARN] No media found in: {thread_url}")
        return

    print(f"[OK] Found {len(media_links)} media files in {thread_url}")

    thread_id = extract_thread_id(thread_url)
    if not thread_id:
        print(f"[WARN] Cannot extract folder name from URL: {thread_url}")
        return

    thread_folder = os.path.join(output_root, thread_id)
    os.makedirs(thread_folder, exist_ok=True)

    for media_link in media_links:
        filename = media_link.rsplit("/", 1)[-1]
        file_path = os.path.join(thread_folder, filename)
        download_file(client, media_link, file_path)


def parse_args() -> tuple[str, str, list[str]]:
    """Validate CLI arguments and return parsed values."""
    if len(sys.argv) < 4:
        print(
            "Usage:\n  python main.py <output_path> <image|video|both> <thread_url...>"
        )
        sys.exit(1)

    out_path = sys.argv[1]
    option = sys.argv[2].lower()
    urls = sys.argv[3:]

    if not os.path.isdir(out_path):
        print(f"Error: '{out_path}' is not an existing directory.")
        sys.exit(1)

    if option not in MEDIA_EXTENSIONS:
        print("Error: media option must be: image, video, both")
        sys.exit(1)

    valid_urls = [u for u in urls if VALID_THREAD_URL.match(u)]
    invalid_urls = [u for u in urls if u not in valid_urls]

    for bad in invalid_urls:
        print(f"Incorrect URL: {bad}")

    if not valid_urls:
        print("Error: No valid thread URLs provided.")
        sys.exit(1)

    return out_path, option, valid_urls


def main():
    out_path, option, thread_urls = parse_args()

    # One shared client — faster and cleaner
    with httpx.Client(verify=False, timeout=30.0) as client:
        for url in thread_urls:
            process_thread(client, url, out_path, option)


# ---------------------- ENTRY POINT ----------------------

if __name__ == "__main__":
    start = time.perf_counter()
    main()
    print(f"\nTime: {time.perf_counter() - start:.2f} seconds.")
