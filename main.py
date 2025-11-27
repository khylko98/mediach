import os
import re
import sys
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

# Regex to validate 2ch / arhivach threads URLs
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


def extract_href(tag) -> str | None:
    href = tag.get("href")

    # Normal case: string
    if isinstance(href, str):
        return href

    # Case: ["url.jpg"]
    if isinstance(href, list) and len(href) == 1 and isinstance(href[0], str):
        return href[0]

    return None


def get_media_links(thread_url: str, media_option: str) -> set[str] | None:
    """Fetch thread HTML and extract media links based on extension."""
    try:
        response = httpx.get(thread_url, verify=False)
        response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Request error for {thread_url}: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"HTTP {e.response.status_code} for {thread_url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    valid_extensions = MEDIA_EXTENSIONS[media_option]

    media_links: set[str] = set()

    for tag in soup.find_all("a", href=True):
        href = extract_href(tag)
        if not href:
            continue

        if any(href.lower().endswith(ext) for ext in valid_extensions):
            media_links.add(urljoin(thread_url, href))

    return media_links


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: "
            "python "
            "main.py "
            "<output_path> "
            "<image | video | both> "
            "[<thread_url_1> <thread_url_2> ...]\n"
            #
            "Example: "
            "python3.14 "
            "main.py "
            "~/Downloads "
            "both "
            "https://2ch.hk/b/res/322069228.html "
            "https://arhivach.vc/thread/1222099/"
        )
        sys.exit(1)

    output_path = sys.argv[1]

    # Ensure output path exists
    if not os.path.isdir(output_path):
        print(
            f"Error: '{output_path}' does not exist or is not a directory.\n"
            "Please create the folder first or specify an existing path."
        )
        sys.exit(1)

    media_option = sys.argv[2]

    if media_option not in ("image", "video", "both"):
        print("Error: media option must be one of: image, video, both\n")
        sys.exit(1)

    threads_urls = sys.argv[3:]

    valid_threads_urls: set[str] = set()

    for thread_url in threads_urls:
        # Check if the URL is valid according to VALID_THREAD_URL
        if VALID_THREAD_URL.match(thread_url):
            valid_threads_urls.add(thread_url)
        else:
            print(f"Incorrect URL: {thread_url}")

    if not valid_threads_urls:
        print("Error: No valid threads URLs provided.")
        sys.exit(1)

    for valid_thread_url in valid_threads_urls:
        media_links = get_media_links(valid_thread_url, media_option)
        print(media_links)


if __name__ == "__main__":
    main()
