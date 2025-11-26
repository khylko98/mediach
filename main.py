import os
import re
import sys

# Regex to validate 2ch / arhivach threads URLs
VALID_THREAD_URL = re.compile(
    r"^https?://(?:"
    r"2ch\.[a-z]{2,10}/[a-z0-9_]+/res/\d+\.html"
    r"|arhivach\.[a-z]{2,10}/thread/\d+/?"
    r")$",
    re.IGNORECASE,
)


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

    valid_threads_urls = set()

    for thread_url in threads_urls:
        # Check if the URL is valid according to VALID_THREAD_URL
        if VALID_THREAD_URL.match(thread_url):
            valid_threads_urls.add(thread_url)
        else:
            print(f"Incorrect URL: {thread_url}")

    if not valid_threads_urls:
        print("Error: No valid threads URLs provided.")
        sys.exit(1)


if __name__ == "__main__":
    main()
