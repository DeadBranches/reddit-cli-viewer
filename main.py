import argparse
import datetime
import json
import time

import humanize
import requests


def get_reddit_json(page_url: str):
    """Fetch the json for any reddit page."""

    final_character = page_url[-1]
    json_url = f"{page_url[:-1]}.json" if final_character == "/" else f"{page_url}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en,en-US;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Connection": "keep-alive",
        "Sec-GPC": "1",
        "Priority": "u=0, i",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    response = requests.get(json_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Automatically parse JSON
    else:
        return {
            "error": f"Failed to fetch data (Status Code: {response.status_code})",
            "details": response.text,
        }


# helper functions


def get_file(json_path: str):
    """Read the JSON file."""

    with open(json_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    return json_data


def write_file(markdown_path: str):
    """Write the markdown output to a file."""

    output_path = "/mnt/data/reddit_post.md"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(markdown_output)


def relative_time(past_epoch: int):
    """Convert epoch difference to a human-readable relative time."""
    now = time.time()
    past_time = datetime.datetime.fromtimestamp(past_epoch)
    now_time = datetime.datetime.fromtimestamp(now)

    difference = now_time - past_time
    return humanize.naturaltime(difference)


def extract_post_details(reddit_data: dict) -> str:
    """Format a reddit post from json markdown."""

    post_data = reddit_data[0]["data"]["children"][0]["data"]
    subreddit = post_data["subreddit_name_prefixed"]
    title = post_data["title"]
    post_text = post_data["selftext"]

    markdown_output = f"""# {subreddit} Reddit Post 

**title:** {title}  

## Post Text  

{post_text}  

"""
    return markdown_output


def format_comment(comment_json: dict, depth=1) -> str:
    """Recursively format comments and replies into Markdown."""
    author: str = comment_json["data"]["author"]
    body: str = comment_json["data"]["body"]
    permalink: str = f"https://www.reddit.com{comment_json['data']['permalink']}"
    is_op: str = "**OP**" if comment_json["data"]["is_submitter"] == True else ""
    time_posted: str = relative_time(comment_json["data"]["created_utc"])
    score: int = comment_json["data"]["score"]
    indent = "#" * (depth + 2)  # More # means deeper reply levels
    formatted = f"""{indent} Reply by *u/{author}* {is_op}

{body}\n\n

posted: **{time_posted}** | score: **{score}**
[permalink: ]({permalink})\n\n"""

    # Recursively add replies if available
    if "replies" in comment_json["data"] and isinstance(
        comment_json["data"]["replies"], dict
    ):
        replies = comment_json["data"]["replies"]["data"]["children"]
        for reply in replies:
            if reply["kind"] == "t1":  # Ensure it's a comment, not "more" placeholder
                formatted += format_comment(reply, depth + 1)

    return formatted


def main():
    parser = argparse.ArgumentParser(
        description="A script that accepts a URL as an argument."
    )
    parser.add_argument("url", type=str, help="The URL to process")
    args = parser.parse_args()

    url = args.url
    # url = "https://www.reddit.com/r/machinelearningnews/comments/1iw2cmu/moonshot_ai_and_ucla_researchers_release/"

    reddit_data = get_reddit_json(url)
    comments_data = reddit_data[1]["data"]["children"]

    markdown_output = extract_post_details(reddit_data)
    # Process top-level comments
    for comment in comments_data:
        if comment["kind"] == "t1":  # Ensure it's a comment
            markdown_output += format_comment(comment)

    print(markdown_output)


if __name__ == "__main__":
    main()
