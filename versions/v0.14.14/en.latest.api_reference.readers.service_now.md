# Service now
##  SnowKBReader #
Bases: `BaseReader`
ServiceNow Knowledge Base reader using PySNC with username/password or password grant flow.
This reader requires custom parsers for processing different file types. At minimum, an HTML parser must be provided for processing article bodies. Additional parsers can be provided for other file types as needed.
The reader uses LlamaIndex's standard instrumentation event system to provide detailed tracking of the loading process. Events are fired at various stages during knowledge base article retrieval and attachment processing, allowing for monitoring and debugging.
Required file types: - FileType.HTML: For HTML content (required for article body processing)
Recommended file types to provide parsers for: - FileType.PDF: For PDF documents - FileType.DOCUMENT: For Word documents (.docx) - FileType.TEXT: For plain text files - FileType.SPREADSHEET: For Excel files (.xlsx) - FileType.PRESENTATION: For PowerPoint files (.pptx)
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`instance` |  `str` |  ServiceNow instance name (without .service-now.com) |  _required_  
`custom_parsers` |  `Dict[FileType, BaseReader]` |  Dictionary mapping FileType enum values to BaseReader instances. This is REQUIRED and must include at least FileType.HTML. Each parser must implement the load_data method. |  _required_  
`username` |  `Optional[str]` |  ServiceNow username for authentication (required) |  `None`  
`password` |  `Optional[str]` |  ServiceNow password for authentication (required) |  `None`  
`client_id` |  `Optional[str]` |  OAuth client ID for ServiceNow (optional, but if provided, client_secret is required) |  `None`  
`client_secret` |  `Optional[str]` |  OAuth client secret for ServiceNow (optional, but if provided, client_id is required) |  `None`  
`process_attachment_callback` |  `Optional[Callable[[str, int], tuple[bool, str]]]` |  Optional callback to filter attachments (content_type: str, size_bytes: int, file_name: str) -> tuple[bool, str] |  `None`  
`process_document_callback` |  `Optional[Callable[[str], bool]]` |  Optional callback to filter documents (kb_number: str) -> bool |  `None`  
`custom_folder` |  `Optional[str]` |  Folder for temporary files during parsing |  `None`  
`fail_on_error` |  `bool` |  Whether to fail on parsing errors or continue |  `True`  
`kb_table` |  `str` |  ServiceNow table name for knowledge base articles |  `'kb_knowledge'`  
`logger` |  |  Optional logger instance |  `None`  
Authentication
  * Basic auth: Provide username and password only
  * OAuth flow: Provide username, password, client_id, and client_secret

Events
The reader fires various events during processing using LlamaIndex's standard instrumentation system. Available events include page fetch events, attachment processing events, and error events. Use get_dispatcher() to subscribe to events.
Raises:
Type | Description  
---|---  
`ValueError` |  If required parameters are missing or invalid, or if HTML parser is not provided  
`TypeError` |  If custom_parsers types are incorrect  
Source code in `llama-index-integrations/readers/llama-index-readers-service-now/llama_index/readers/service_now/base.py`

| ```
class SnowKBReader(BaseReader):
    """
    ServiceNow Knowledge Base reader using PySNC with username/password or password grant flow.

    This reader requires custom parsers for processing different file types. At minimum,
    an HTML parser must be provided for processing article bodies. Additional parsers
    can be provided for other file types as needed.

    The reader uses LlamaIndex's standard instrumentation event system to provide detailed
    tracking of the loading process. Events are fired at various stages during knowledge base
    article retrieval and attachment processing, allowing for monitoring and debugging.

    Required file types:
    - FileType.HTML: For HTML content (required for article body processing)

    Recommended file types to provide parsers for:
    - FileType.PDF: For PDF documents
    - FileType.DOCUMENT: For Word documents (.docx)
    - FileType.TEXT: For plain text files
    - FileType.SPREADSHEET: For Excel files (.xlsx)
    - FileType.PRESENTATION: For PowerPoint files (.pptx)

    Args:
        instance: ServiceNow instance name (without .service-now.com)
        custom_parsers: Dictionary mapping FileType enum values to BaseReader instances.
                       This is REQUIRED and must include at least FileType.HTML.
                       Each parser must implement the load_data method.
        username: ServiceNow username for authentication (required)
        password: ServiceNow password for authentication (required)
        client_id: OAuth client ID for ServiceNow (optional, but if provided, client_secret is required)
        client_secret: OAuth client secret for ServiceNow (optional, but if provided, client_id is required)
        process_attachment_callback: Optional callback to filter attachments (content_type: str, size_bytes: int, file_name: str) -> tuple[bool, str]
        process_document_callback: Optional callback to filter documents (kb_number: str) -> bool
        custom_folder: Folder for temporary files during parsing
        fail_on_error: Whether to fail on parsing errors or continue
        kb_table: ServiceNow table name for knowledge base articles
        logger: Optional logger instance

    Authentication:
        - Basic auth: Provide username and password only
        - OAuth flow: Provide username, password, client_id, and client_secret

    Events:
        The reader fires various events during processing using LlamaIndex's standard
        instrumentation system. Available events include page fetch events, attachment
        processing events, and error events. Use get_dispatcher() to subscribe to events.

    Raises:
        ValueError: If required parameters are missing or invalid, or if HTML parser is not provided
        TypeError: If custom_parsers types are incorrect

    """

    def __init__(
        self,
        instance: str,
        custom_parsers: Dict[FileType, BaseReader],
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        process_attachment_callback: Optional[
            Callable[[str, int], tuple[bool, str]]
        ] = None,
        process_document_callback: Optional[Callable[[str], bool]] = None,
        custom_folder: Optional[str] = None,
        fail_on_error: bool = True,
        kb_table: str = "kb_knowledge",
        logger=None,
    ):
        # Validate required parameters
        if not instance:
            raise ValueError("instance parameter is required")

        if custom_parsers is None:
            raise ValueError("custom_parsers parameter is required and cannot be None")

        if not custom_parsers:
            raise ValueError("custom_parsers parameter is required and cannot be empty")

        if not isinstance(custom_parsers, dict):
            raise TypeError("custom_parsers must be a dictionary")

        # Validate custom_parsers dictionary - ensure it has at least one parser
        if len(custom_parsers) == 0:
            raise ValueError("custom_parsers must contain at least one parser")

        # Validate each custom parser
        for file_type, parser in custom_parsers.items():
            if not isinstance(file_type, FileType):
                raise TypeError(
                    f"custom_parsers keys must be FileType enum values, got {type(file_type)}"
                )

            if not isinstance(parser, BaseReader):
                raise TypeError(
                    f"custom_parsers values must be BaseReader instances, got {type(parser)} for {file_type}"
                )

            # Validate that parser has required load_data method
            if not hasattr(parser, "load_data") or not callable(parser.load_data):
                raise TypeError(
                    f"custom_parsers[{file_type}] must have a callable 'load_data' method"
                )

        # Validate authentication parameters
        # Username and password are always required
        if not username:
            raise ValueError("username parameter is required")
        if not password:
            raise ValueError("password parameter is required")

        # If client_id is provided, client_secret must also be provided (for OAuth flow)
        if client_id is not None and client_secret is None:
            raise ValueError("client_secret is required when client_id is provided")
        if client_secret is not None and client_id is None:
            raise ValueError("client_id is required when client_secret is provided")

        self.instance = instance
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

        self.custom_parsers = custom_parsers
        self.custom_folder = custom_folder or os.path.join(
            os.getcwd(), "custom_parsers"
        )

        # Validate recommended parsers and warn if missing
        self.logger = logger or internal_logger
        CustomParserManager.validate_recommended_parsers(custom_parsers, self.logger)

        # Ensure custom_folder exists and is writable
        try:
            os.makedirs(self.custom_folder, exist_ok=True)
            # Test write permissions
            test_file = os.path.join(self.custom_folder, ".test_write")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except (OSError, PermissionError) as e:
            raise ValueError(
                f"Custom folder '{self.custom_folder}' is not accessible or writable: {e}"
            )

        self.process_attachment_callback = process_attachment_callback
        self.process_document_callback = process_document_callback
        self.fail_on_error = fail_on_error

        self.kb_table = kb_table
        self.pysnc_client = None

        self.initialize_client()

        self.custom_parser_manager = CustomParserManager(
            custom_parsers=custom_parsers,
            custom_folder=self.custom_folder,
            logger=self.logger,
        )

    def _format_attachment_header(self, attachment: dict) -> str:
        """Formats the attachment title as a markdown header."""
        return f"# {attachment['file_name']}\n"

    def initialize_client(self):
        """Initialize a new ServiceNowClient instance with fresh credentials."""
        try:
            self.logger.info("Initializing ServiceNow client")
            instance = self.instance
            user = self.username
            password = self.password

            # Use OAuth flow if client_id and client_secret are provided, otherwise use basic auth
            if self.client_id and self.client_secret:
                client_id = self.client_id
                client_secret = self.client_secret
                self.pysnc_client = ServiceNowClient(
                    instance,
                    ServiceNowPasswordGrantFlow(
                        user, password, client_id, client_secret
                    ),
                )
            else:
                # Basic authentication with username and password
                self.pysnc_client = ServiceNowClient(instance, (user, password))
        except Exception as e:
            self.logger.error(f"Error initializing ServiceNow client: {e}")
            raise ValueError(f"Error initializing ServiceNow client: {e}")

    def load_data(
        self,
        article_sys_id: Optional[str] = None,
        numbers: Optional[List[str]] = None,
        status="Published",
    ) -> List[Document]:
        """
        Load a KB article by sys_id or number using PySNC. Returns a list with one Document.
        """
        gr = self.pysnc_client.GlideRecord(self.kb_table)
        if article_sys_id:
            gr.add_query("sys_id", article_sys_id)
        elif numbers:
            gr.add_query("number", "IN", ",".join(numbers))
        else:
            raise ValueError("Must provide article_sys_id or number")
        gr.add_query("latest", "true")  # Only fetch latest version
        gr.add_query(
            "workflow_state", status or DEFAULT_WORKFLOW_STATE
        )  # Include only published articles
        gr.query()
        if not gr.has_next():
            self.logger.error(
                f"No KB article found for sys_id {article_sys_id} or numbers {numbers}"
            )
            raise ValueError(
                f"No KB article found for sys_id {article_sys_id} or numbers {numbers}"
            )
        docs = []

        total_pages = gr.get_row_count()
        self.logger.info(
            f"Found {total_pages} KB articles matching criteria: sys_id={article_sys_id}, numbers={numbers}, status={status}"
        )
        dispatcher.event(SNOWKBTotalPagesEvent(total_pages=total_pages))

        while gr.next():
            try:
                kb_number = gr.number.get_value()
                dispatcher.event(SNOWKBPageFetchStartEvent(page_id=kb_number))

                # Check if document should be processed using callback
                if self.process_document_callback:
                    should_process = self.process_document_callback(kb_number)
                    if not should_process:
                        self.logger.info(
                            f"Skipping document {kb_number} based on process_document_callback"
                        )
                        continue

                # Process article text and attachments
                txt_lm = (
                    gr.article_body
                    if hasattr(gr, "article_body") and gr.article_body
                    else gr.text.get_value()
                )
                attachments = self.handle_attachments(
                    gr.sys_id.get_value(), kb_number=gr.number.get_value()
                )

                try:
                    article_markdown = (
                        self.custom_parser_manager.process_text_with_custom_parser(
                            FileType.HTML, txt_lm, "html"
                        )
                    )
                except ValueError as e:
                    self.logger.error(
                        f"Error processing article HTML with custom parser: {e}"
                    )
                    if self.fail_on_error:
                        raise
                    article_markdown = txt_lm  # Fallback to original text

                complete_text = (
                    article_markdown
                    + "\n\n"
                    + "\n".join(
                        self._format_attachment_header(attach) + attach["markdown_text"]
                        for attach in attachments
                        if "markdown_text" in attach
                    )
                )

                display_number = (
                    gr.get_display_value("display_number")
                    if hasattr(gr, "display_number")
                    else None
                )
                sys_updated_on = (
                    gr.get_value("sys_updated_on")
                    if hasattr(gr, "sys_updated_on")
                    else None
                )
                kb_number = gr.get_value("number") if hasattr(gr, "number") else None
                kb_status = (
                    gr.workflow_state.get_display_value()
                    if hasattr(gr, "workflow_state")
                    else "Unknown"
                )

                doc = Document(
                    text=complete_text,
                    extra_info={
                        "title": gr.short_description.get_display_value()
                        if hasattr(gr, "short_description")
                        else "No Title",
                        "page_id": kb_number,
                        "status": kb_status,
                        "version": display_number,
                        "sys_updated_on": sys_updated_on,
                        "kb_number": kb_number,
                    },
                )
                metadata = {
                    "version": display_number,
                    "sys_updated_on": sys_updated_on,
                    "kb_number": kb_number,
                }
                dispatcher.event(
                    SNOWKBPageFetchCompletedEvent(
                        page_id=kb_number,
                        document=doc,
                        metadata=metadata,
                    )
                )
                docs.append(doc)
            except Exception as e:
                self.logger.error(
                    f"Error processing KB article {gr.number.get_value()}: {e}"
                )
                dispatcher.event(
                    SNOWKBPageFailedEvent(
                        page_id=gr.number.get_value(),
                        error=str(e),
                    )
                )
                if self.fail_on_error:
                    raise
        return docs

    def _get_attachment_data(self, gr_attach: GlideRecord, page_id: str) -> dict:
        """Helper method to get attachment data for events."""
        return {
            "page_id": page_id,
            "attachment_id": f"{gr_attach.get_value('sys_id')}",
            "attachment_name": f"{gr_attach.get_value('file_name')}",
            "attachment_type": f"{gr_attach.get_value('content_type')}",
            "attachment_size": int(f"{gr_attach.get_value('size_bytes')}"),
            "attachment_link": f"https://{self.instance}.service-now.com/sys_attachment.do?sys_id={gr_attach.get_value('sys_id')}",
        }

    def handle_attachment(self, gr_attach: GlideRecord, kb_number: str) -> dict:
        """
        Process a single attachment GlideRecord and return its info dict.
        """
        if not hasattr(gr_attach, "file_name") or not hasattr(
            gr_attach, "content_type"
        ):
            self.logger.error(
                "Invalid GlideRecord for attachment, missing required fields."
            )
            return {}

        attachment_id = f"{gr_attach.get_value('sys_id')}"
        size_bytes = int(f"{gr_attach.get_value('size_bytes')}")
        file_name = f"{gr_attach.get_value('file_name')}"
        content_type = f"{gr_attach.get_value('content_type')}"

        self.logger.info(f"Processing attachment {file_name}")
        attachment_data = self._get_attachment_data(gr_attach, kb_number)
        dispatcher.event(SNOWKBAttachmentProcessingStartEvent(**attachment_data))

        if self.process_attachment_callback:
            can_process, message = self.process_attachment_callback(
                content_type, size_bytes, file_name
            )
            if not can_process:
                attachment_data = self._get_attachment_data(gr_attach, kb_number)
                dispatcher.event(
                    SNOWKBAttachmentSkippedEvent(**attachment_data, reason=message)
                )
                self.logger.info(f"Skipping attachment {file_name}: {message}")
                return {}

        try:
            res: requests.Response = self._download_attachment_content(gr_attach.sys_id)
            if not res or not getattr(res, "ok", False):
                self.logger.error(
                    f"Failed to download attachment content for {file_name}"
                )
                return {}
            else:
                file_content = res.content

            file_type = self.get_File_type(file_name)

            # Check if parser is available for this file type
            if file_type not in self.custom_parsers:
                self.logger.warning(
                    f"No custom parser available for file type {file_type.value} (file: {file_name}). Skipping attachment."
                )
                attachment_data = self._get_attachment_data(gr_attach, kb_number)
                dispatcher.event(
                    SNOWKBAttachmentSkippedEvent(
                        **attachment_data, reason=f"No parser for {file_type.value}"
                    )
                )
                return {}  # Skip this attachment if no parser available

            try:
                markdown_text = self.custom_parser_manager.process_with_custom_parser(
                    file_type, file_content, file_name.split(".")[-1]
                )
            except ValueError as e:
                self.logger.error(
                    f"Error processing attachment {file_name} with custom parser: {e}"
                )
                attachment_data = self._get_attachment_data(gr_attach, kb_number)
                dispatcher.event(
                    SNOWKBAttachmentFailedEvent(**attachment_data, error=str(e))
                )
                if self.fail_on_error:
                    raise
                return {}  # Skip this attachment if custom parser fails

            self.logger.debug(markdown_text)

            attachment_data = self._get_attachment_data(gr_attach, kb_number)
            dispatcher.event(SNOWKBAttachmentProcessedEvent(**attachment_data))
            return {
                "file_name": file_name,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "markdown_text": markdown_text,
                "sys_id": gr_attach.sys_id,
            }
        except Exception as e:
            self.logger.error(f"Error processing attachment {file_name}: {e}")
            attachment_data = self._get_attachment_data(gr_attach, kb_number)
            dispatcher.event(
                SNOWKBAttachmentFailedEvent(**attachment_data, error=str(e))
            )
            return {}

    def handle_attachments(self, sys_id: str, kb_number: str) -> list:
        """
        Download all attachments for a given KB article sys_id. Returns a list of attachment info dicts.
        """
        attachments = []
        try:
            gr_attach = self.pysnc_client.GlideRecord("sys_attachment")
            gr_attach.add_query("table_sys_id", sys_id)
            gr_attach.add_query("table_name", self.kb_table)
            gr_attach.query()
            while gr_attach.next():
                attachment_info = self.handle_attachment(gr_attach, kb_number)
                if "markdown_text" in attachment_info:
                    attachments.append(attachment_info)
        except Exception as e:
            self.logger.error(f"Error downloading attachments: {e}")
        return attachments

    def get_File_type(self, file_name: str) -> FileType:
        """
        Determine the file type based on the file name extension.
        """
        ext = os.path.splitext(file_name)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".gif"]:
            return FileType.IMAGE
        elif ext in [".pdf"]:
            return FileType.PDF
        elif ext in [".txt"]:
            return FileType.TEXT
        elif ext in [".csv"]:
            return FileType.CSV
        elif ext in [".html"]:
            return FileType.HTML
        elif ext in [".docx"]:
            return FileType.DOCUMENT
        elif ext in [".xlsx"]:
            return FileType.SPREADSHEET
        elif ext in [".pptx"]:
            return FileType.PRESENTATION
        elif ext in [".md"]:
            return FileType.MARKDOWN
        else:
            return FileType.UNKNOWN

    def _download_attachment_content(self, sys_id: str) -> Optional[bytes]:
        """
        Download attachment content using PySNC's attachment.get_file method.
        """
        try:
            if hasattr(self.pysnc_client, "attachment_api") and hasattr(
                self.pysnc_client.attachment_api, "get_file"
            ):
                return self.pysnc_client.attachment_api.get_file(sys_id)
            else:
                self.logger.error(
                    "self.pysnc_client.attachment_api.get_file is not available. Please check your PySNC version."
                )
                return None
        except Exception as e:
            self.logger.error(f"Attachment download failed for {sys_id}: {e}")
            return None

```
  
---|---  
###  initialize_client #
```
initialize_client()

```

Initialize a new ServiceNowClient instance with fresh credentials.
Source code in `llama-index-integrations/readers/llama-index-readers-service-now/llama_index/readers/service_now/base.py`

| ```
def initialize_client(self):
    """Initialize a new ServiceNowClient instance with fresh credentials."""
    try:
        self.logger.info("Initializing ServiceNow client")
        instance = self.instance
        user = self.username
        password = self.password

        # Use OAuth flow if client_id and client_secret are provided, otherwise use basic auth
        if self.client_id and self.client_secret:
            client_id = self.client_id
            client_secret = self.client_secret
            self.pysnc_client = ServiceNowClient(
                instance,
                ServiceNowPasswordGrantFlow(
                    user, password, client_id, client_secret
                ),
            )
        else:
            # Basic authentication with username and password
            self.pysnc_client = ServiceNowClient(instance, (user, password))
    except Exception as e:
        self.logger.error(f"Error initializing ServiceNow client: {e}")
        raise ValueError(f"Error initializing ServiceNow client: {e}")

```
  
---|---  
###  load_data #
```
load_data(article_sys_id: Optional[str] = None, numbers: Optional[List[str]] = None, status='Published') -> List[Document]

```

Load a KB article by sys_id or number using PySNC. Returns a list with one Document.
Source code in `llama-index-integrations/readers/llama-index-readers-service-now/llama_index/readers/service_now/base.py`

| ```
def load_data(
    self,
    article_sys_id: Optional[str] = None,
    numbers: Optional[List[str]] = None,
    status="Published",
) -> List[Document]:
    """
    Load a KB article by sys_id or number using PySNC. Returns a list with one Document.
    """
    gr = self.pysnc_client.GlideRecord(self.kb_table)
    if article_sys_id:
        gr.add_query("sys_id", article_sys_id)
    elif numbers:
        gr.add_query("number", "IN", ",".join(numbers))
    else:
        raise ValueError("Must provide article_sys_id or number")
    gr.add_query("latest", "true")  # Only fetch latest version
    gr.add_query(
        "workflow_state", status or DEFAULT_WORKFLOW_STATE
    )  # Include only published articles
    gr.query()
    if not gr.has_next():
        self.logger.error(
            f"No KB article found for sys_id {article_sys_id} or numbers {numbers}"
        )
        raise ValueError(
            f"No KB article found for sys_id {article_sys_id} or numbers {numbers}"
        )
    docs = []

    total_pages = gr.get_row_count()
    self.logger.info(
        f"Found {total_pages} KB articles matching criteria: sys_id={article_sys_id}, numbers={numbers}, status={status}"
    )
    dispatcher.event(SNOWKBTotalPagesEvent(total_pages=total_pages))

    while gr.next():
        try:
            kb_number = gr.number.get_value()
            dispatcher.event(SNOWKBPageFetchStartEvent(page_id=kb_number))

            # Check if document should be processed using callback
            if self.process_document_callback:
                should_process = self.process_document_callback(kb_number)
                if not should_process:
                    self.logger.info(
                        f"Skipping document {kb_number} based on process_document_callback"
                    )
                    continue

            # Process article text and attachments
            txt_lm = (
                gr.article_body
                if hasattr(gr, "article_body") and gr.article_body
                else gr.text.get_value()
            )
            attachments = self.handle_attachments(
                gr.sys_id.get_value(), kb_number=gr.number.get_value()
            )

            try:
                article_markdown = (
                    self.custom_parser_manager.process_text_with_custom_parser(
                        FileType.HTML, txt_lm, "html"
                    )
                )
            except ValueError as e:
                self.logger.error(
                    f"Error processing article HTML with custom parser: {e}"
                )
                if self.fail_on_error:
                    raise
                article_markdown = txt_lm  # Fallback to original text

            complete_text = (
                article_markdown
                + "\n\n"
                + "\n".join(
                    self._format_attachment_header(attach) + attach["markdown_text"]
                    for attach in attachments
                    if "markdown_text" in attach
                )
            )

            display_number = (
                gr.get_display_value("display_number")
                if hasattr(gr, "display_number")
                else None
            )
            sys_updated_on = (
                gr.get_value("sys_updated_on")
                if hasattr(gr, "sys_updated_on")
                else None
            )
            kb_number = gr.get_value("number") if hasattr(gr, "number") else None
            kb_status = (
                gr.workflow_state.get_display_value()
                if hasattr(gr, "workflow_state")
                else "Unknown"
            )

            doc = Document(
                text=complete_text,
                extra_info={
                    "title": gr.short_description.get_display_value()
                    if hasattr(gr, "short_description")
                    else "No Title",
                    "page_id": kb_number,
                    "status": kb_status,
                    "version": display_number,
                    "sys_updated_on": sys_updated_on,
                    "kb_number": kb_number,
                },
            )
            metadata = {
                "version": display_number,
                "sys_updated_on": sys_updated_on,
                "kb_number": kb_number,
            }
            dispatcher.event(
                SNOWKBPageFetchCompletedEvent(
                    page_id=kb_number,
                    document=doc,
                    metadata=metadata,
                )
            )
            docs.append(doc)
        except Exception as e:
            self.logger.error(
                f"Error processing KB article {gr.number.get_value()}: {e}"
            )
            dispatcher.event(
                SNOWKBPageFailedEvent(
                    page_id=gr.number.get_value(),
                    error=str(e),
                )
            )
            if self.fail_on_error:
                raise
    return docs

```
  
---|---  
###  handle_attachment #
```
handle_attachment(gr_attach: GlideRecord, kb_number: str) -> dict

```

Process a single attachment GlideRecord and return its info dict.
Source code in `llama-index-integrations/readers/llama-index-readers-service-now/llama_index/readers/service_now/base.py`

| ```
def handle_attachment(self, gr_attach: GlideRecord, kb_number: str) -> dict:
    """
    Process a single attachment GlideRecord and return its info dict.
    """
    if not hasattr(gr_attach, "file_name") or not hasattr(
        gr_attach, "content_type"
    ):
        self.logger.error(
            "Invalid GlideRecord for attachment, missing required fields."
        )
        return {}

    attachment_id = f"{gr_attach.get_value('sys_id')}"
    size_bytes = int(f"{gr_attach.get_value('size_bytes')}")
    file_name = f"{gr_attach.get_value('file_name')}"
    content_type = f"{gr_attach.get_value('content_type')}"

    self.logger.info(f"Processing attachment {file_name}")
    attachment_data = self._get_attachment_data(gr_attach, kb_number)
    dispatcher.event(SNOWKBAttachmentProcessingStartEvent(**attachment_data))

    if self.process_attachment_callback:
        can_process, message = self.process_attachment_callback(
            content_type, size_bytes, file_name
        )
        if not can_process:
            attachment_data = self._get_attachment_data(gr_attach, kb_number)
            dispatcher.event(
                SNOWKBAttachmentSkippedEvent(**attachment_data, reason=message)
            )
            self.logger.info(f"Skipping attachment {file_name}: {message}")
            return {}

    try:
        res: requests.Response = self._download_attachment_content(gr_attach.sys_id)
        if not res or not getattr(res, "ok", False):
            self.logger.error(
                f"Failed to download attachment content for {file_name}"
            )
            return {}
        else:
            file_content = res.content

        file_type = self.get_File_type(file_name)

        # Check if parser is available for this file type
        if file_type not in self.custom_parsers:
            self.logger.warning(
                f"No custom parser available for file type {file_type.value} (file: {file_name}). Skipping attachment."
            )
            attachment_data = self._get_attachment_data(gr_attach, kb_number)
            dispatcher.event(
                SNOWKBAttachmentSkippedEvent(
                    **attachment_data, reason=f"No parser for {file_type.value}"
                )
            )
            return {}  # Skip this attachment if no parser available

        try:
            markdown_text = self.custom_parser_manager.process_with_custom_parser(
                file_type, file_content, file_name.split(".")[-1]
            )
        except ValueError as e:
            self.logger.error(
                f"Error processing attachment {file_name} with custom parser: {e}"
            )
            attachment_data = self._get_attachment_data(gr_attach, kb_number)
            dispatcher.event(
                SNOWKBAttachmentFailedEvent(**attachment_data, error=str(e))
            )
            if self.fail_on_error:
                raise
            return {}  # Skip this attachment if custom parser fails

        self.logger.debug(markdown_text)

        attachment_data = self._get_attachment_data(gr_attach, kb_number)
        dispatcher.event(SNOWKBAttachmentProcessedEvent(**attachment_data))
        return {
            "file_name": file_name,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "markdown_text": markdown_text,
            "sys_id": gr_attach.sys_id,
        }
    except Exception as e:
        self.logger.error(f"Error processing attachment {file_name}: {e}")
        attachment_data = self._get_attachment_data(gr_attach, kb_number)
        dispatcher.event(
            SNOWKBAttachmentFailedEvent(**attachment_data, error=str(e))
        )
        return {}

```
  
---|---  
###  handle_attachments #
```
handle_attachments(sys_id: str, kb_number: str) -> list

```

Download all attachments for a given KB article sys_id. Returns a list of attachment info dicts.
Source code in `llama-index-integrations/readers/llama-index-readers-service-now/llama_index/readers/service_now/base.py`

| ```
def handle_attachments(self, sys_id: str, kb_number: str) -> list:
    """
    Download all attachments for a given KB article sys_id. Returns a list of attachment info dicts.
    """
    attachments = []
    try:
        gr_attach = self.pysnc_client.GlideRecord("sys_attachment")
        gr_attach.add_query("table_sys_id", sys_id)
        gr_attach.add_query("table_name", self.kb_table)
        gr_attach.query()
        while gr_attach.next():
            attachment_info = self.handle_attachment(gr_attach, kb_number)
            if "markdown_text" in attachment_info:
                attachments.append(attachment_info)
    except Exception as e:
        self.logger.error(f"Error downloading attachments: {e}")
    return attachments

```
  
---|---  
###  get_File_type #
```
get_File_type(file_name: str) -> FileType

```

Determine the file type based on the file name extension.
Source code in `llama-index-integrations/readers/llama-index-readers-service-now/llama_index/readers/service_now/base.py`

| ```
def get_File_type(self, file_name: str) -> FileType:
    """
    Determine the file type based on the file name extension.
    """
    ext = os.path.splitext(file_name)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".gif"]:
        return FileType.IMAGE
    elif ext in [".pdf"]:
        return FileType.PDF
    elif ext in [".txt"]:
        return FileType.TEXT
    elif ext in [".csv"]:
        return FileType.CSV
    elif ext in [".html"]:
        return FileType.HTML
    elif ext in [".docx"]:
        return FileType.DOCUMENT
    elif ext in [".xlsx"]:
        return FileType.SPREADSHEET
    elif ext in [".pptx"]:
        return FileType.PRESENTATION
    elif ext in [".md"]:
        return FileType.MARKDOWN
    else:
        return FileType.UNKNOWN

```
  
---|---
