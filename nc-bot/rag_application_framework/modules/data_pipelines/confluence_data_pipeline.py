from atlassian import Confluence
from rag_application_framework.config.app_config import ConfluenceConfig
from rag_application_framework.modules.file_uploader.file_uploader import (
    FilesUploaderBase,
    FileUpload,
    UploadedFile,
)
from langchain_community.document_loaders import ConfluenceLoader
from dataclasses import dataclass
from rag_application_framework.logging.logging import Logging
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

logger = Logging.get_logger(__name__)


@dataclass
class ConfluenceApiPageMetadata:
    title: str
    id: str
    url: str


class ConfluenceFilePipeline:
    def __init__(
        self, file_uploader: FilesUploaderBase, confluence_config: ConfluenceConfig
    ) -> None:
        self.file_uploader = file_uploader
        self.confluence_config = confluence_config

    def _prepare_content_to_upload_from_confluence(
        self, documents: list[ConfluenceApiPageMetadata], confluence: Confluence
    ) -> list[UploadedFile]:
        batch_size = 10

        result = []
        failed_docs: list[tuple[ConfluenceApiPageMetadata, Exception]] = []
        total_docs = len(documents)

        logger.info("Got %s documents to load.", len(documents))

        for i in range(0, len(documents), batch_size):
            logger.info(
                "Loading %s-%s / %s documents", i + 1, i + batch_size, total_docs
            )
            documents_batch = documents[i : i + batch_size]

            def download_pdf(document: ConfluenceApiPageMetadata):
                try:
                    doc_title = document.title
                    doc_source = document.url
                    doc_id = document.id

                    doc_content = confluence.get_page_as_pdf(document.id)

                    if not isinstance(doc_content, bytes):
                        raise ValueError(
                            f"Invalid type returned from confluence: {doc_content}"
                        )

                    doc_content = doc_content.replace(b"\x00", b"")

                    file_name = f"{doc_id}_{doc_title}.pdf".replace("/", "_").replace(
                        "'", "_"
                    )
                    return FileUpload(
                        file_content=doc_content,
                        file_name=file_name,
                        custom_metadata={
                            "confluence_source": doc_source,
                            "confluence_id": doc_id,
                            "confluence_title": doc_title,
                        },
                    )
                except Exception as e:
                    failed_docs.append((document, e))
                    return None

            prepared_content_to_upload: list[FileUpload] = []

            with ThreadPoolExecutor() as executor:
                future_to_document = {
                    executor.submit(download_pdf, doc): doc for doc in documents_batch
                }
                for future in concurrent.futures.as_completed(future_to_document):
                    file_upload = future.result()
                    if file_upload:
                        prepared_content_to_upload.append(file_upload)
            try:
                batch_result = self.file_uploader.upload_and_get_url(
                    prepared_content_to_upload
                )
                result.extend(batch_result)
            except Exception as e:
                failed_docs.extend([(doc, e) for doc in documents_batch])

        if failed_docs:
            logger.error(
                "Failed to upload %s documents from confluence.", len(failed_docs)
            )

            for failed_doc in failed_docs:
                logger.error(
                    "Failed to upload %s: %s\nReason: %s",
                    failed_doc[0].title,
                    failed_doc[0].url,
                    str(failed_doc[1]),
                )
        logger.info("Successfully uploaded %s documents from confluence.", len(result))

        return result

    def load_from_confluence(self, space_key):
        # Initialize the Confluence client
        confluence = Confluence(
            url=self.confluence_config.url,
            username=self.confluence_config.username,
            password=self.confluence_config.api_key,
            api_version="cloud",
        )

        # Retrieve all pages in the specified space
        space_pages = confluence.get_all_pages_from_space(space=space_key, limit=10000)

        # Extract relevant information from the pages
        documents = []
        for page in space_pages:
            page_data = ConfluenceApiPageMetadata(
                title=page["title"],
                id=page["id"],
                url=confluence.url + page["_links"]["webui"],
            )
            documents.append(page_data)

        result = self._prepare_content_to_upload_from_confluence(
            documents=documents, confluence=confluence
        )

        return result

    def _prepare_content_to_upload_from_confluence_loader(
        self, documents
    ) -> list[FileUpload]:
        prepared_content_to_upload: list[FileUpload] = []

        for document in documents:
            doc_title = document.metadata["title"]
            doc_content = document.page_content.encode("utf-8")
            doc_source = document.metadata["source"]
            doc_id = document.metadata["id"]

            file_name = f"{doc_id}_{doc_title}.txt".replace("/", "_").replace("'", "_")

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

    def load_from_confluence_loader(self, space_key):
        loader = ConfluenceLoader(
            url=self.confluence_config.url,
            api_key=self.confluence_config.api_key,
            username=self.confluence_config.username,
        )

        documents = loader.load(
            space_key=space_key,
            include_attachments=True,
            limit=1000,
            max_pages=1000,
        )

        documents = self._prepare_content_to_upload_from_confluence_loader(
            documents=documents
        )

        result = self.file_uploader.upload_and_get_url(list_of_files=documents)

        return result
