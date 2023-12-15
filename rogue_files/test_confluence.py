from sys import api_version
from atlassian import Confluence
import os


def get_all_pages(confluence: Confluence, space_key):
    # Initialize the Confluence client

    # Retrieve all pages in the specified space
    space_pages = confluence.get_all_pages_from_space(space=space_key, limit=1000)

    # Extract relevant information from the pages
    page_info = []
    for page in space_pages:
        page_data = {
            "title": page["title"],
            "id": page["id"],
            "url": confluence.url + page["_links"]["webui"],
        }
        page_info.append(page_data)

    return page_info


def test_get_all_pages():
    # Example usage
    username = "muhammad.taha-khan@nordcloud.com"
    url = "https://nordcloud.atlassian.net/wiki"
    api_token = "..."
    space_key = "ED"

    confluence = Confluence(
        url=url,
        username=username,
        password=api_token,
        api_version="cloud",
    )

    pages = get_all_pages(confluence, space_key)

    os.makedirs("./confluence_pages", exist_ok=True)

    for page in pages:
        title = page["title"]
        print(f"page: {title}")
        with open(
            f"""./confluence_pages/{title.replace('/','_').replace("'", "_")}.pdf""",
            "wb",
        ) as f:
            pdf = confluence.get_page_as_pdf(
                page["id"],
            )
            f.write(pdf)
