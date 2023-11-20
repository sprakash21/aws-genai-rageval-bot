from rag_application_framework.config.app_config import ConfluenceConfig
from rag_application_framework.modules.file_uploader.file_uploader import (
    FilesUploaderBase,
    FileUpload,
)
from langchain.document_loaders import ConfluenceLoader


class ConfluenceFilePipeline:
    def __init__(
        self, file_uploader: FilesUploaderBase, confluence_config: ConfluenceConfig
    ) -> None:
        self.file_uploader = file_uploader
        self.confluence_config = confluence_config

    def _prepare_content_to_upload(self, documents) -> list[FileUpload]:
        prepared_content_to_upload: list[FileUpload] = []

        for document in documents:
            doc_title = document.metadata["title"]
            doc_content = document.page_content.encode("utf-8")
            doc_source = document.metadata["source"]
            doc_id = document.metadata["id"]

            file_name = f"{doc_id}_{doc_title}.txt".replace("/", "_")

            file_to_upload = FileUpload(
                file_content=doc_content,
                file_name=file_name,
                custom_metadata={
                    "confluence_source": doc_source,
                    "confluence_id": doc_id,
                    "confluence_title": doc_title,
                },
            )
            prepared_content_to_upload.append(file_to_upload)
        return prepared_content_to_upload

    def load_from_confluence(self, space_key):
        loader = ConfluenceLoader(
            url=self.confluence_config.url,
            api_key=self.confluence_config.api_key,
            username=self.confluence_config.username,
        )

        documents = loader.load(
            space_key=space_key,
            include_attachments=False,
            limit=1000,
            max_pages=1000,
        )

        documents = self._prepare_content_to_upload(documents=documents)

        result = self.file_uploader.upload_and_get_url(list_of_files=documents)

        return result
