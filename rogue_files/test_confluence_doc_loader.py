from langchain.document_loaders import ConfluenceLoader


def test_test():
    loader = ConfluenceLoader(
        url="https://nordcloud.atlassian.net/wiki",
        api_key="...",
        username="muhammad.taha-khan@nordcloud.com",
    )

    documents = loader.load(
        space_key="ED",
        include_attachments=False,
        limit=10,
        max_pages=10,
    )

    assert len(documents) > 0
