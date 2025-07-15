# Docling
##  DoclingReader #
Bases: `BasePydanticReader`
Docling Reader.
Extracts PDF, DOCX, and other document formats into LlamaIndex Documents as either Markdown or JSON-serialized Docling native format.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`export_type` |  `Literal[markdown, json]` |  The type to export to. Defaults to "markdown". |  _required_  
`doc_converter` |  `DocumentConverter` |  The Docling converter to use. Default factory: `DocumentConverter`. |  _required_  
`md_export_kwargs` |  `Dict[str, Any]` |  Kwargs to use in case of markdown export. Defaults to `{"image_placeholder": ""}`. |  _required_  
`id_func` |  |  (DocIDGenCallable, optional): Doc ID generation function to use. Default: `_uuid4_doc_id_gen` |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-docling/llama_index/readers/docling/base.py`

| ```
class DoclingReader(BasePydanticReader):
    """
    Docling Reader.

    Extracts PDF, DOCX, and other document formats into LlamaIndex Documents as either Markdown or JSON-serialized Docling native format.

    Args:
        export_type (Literal["markdown", "json"], optional): The type to export to. Defaults to "markdown".
        doc_converter (DocumentConverter, optional): The Docling converter to use. Default factory: `DocumentConverter`.
        md_export_kwargs (Dict[str, Any], optional): Kwargs to use in case of markdown export. Defaults to `{"image_placeholder": ""}`.
        id_func: (DocIDGenCallable, optional): Doc ID generation function to use. Default: `_uuid4_doc_id_gen`

    """

    class ExportType(str, Enum):
        MARKDOWN = "markdown"
        JSON = "json"

    @runtime_checkable
    class DocIDGenCallable(Protocol):
        def __call__(self, doc: DLDocument, file_path: str | Path) -> str: ...

    @staticmethod
    def _uuid4_doc_id_gen(doc: DLDocument, file_path: str | Path) -> str:
        return str(uuid.uuid4())

    export_type: ExportType = ExportType.MARKDOWN
    doc_converter: DocumentConverter = Field(default_factory=DocumentConverter)
    md_export_kwargs: Dict[str, Any] = {"image_placeholder": ""}
    id_func: DocIDGenCallable = _uuid4_doc_id_gen

    def lazy_load_data(
        self,
        file_path: str | Path | Iterable[str] | Iterable[Path],
        extra_info: dict | None = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> Iterable[LIDocument]:
        """
        Lazily load from given source.

        Args:
            file_path (str | Path | Iterable[str] | Iterable[Path]): Document file source as single str (URL or local file) or pathlib.Path — or iterable thereof
            extra_info (dict | None, optional): Any pre-existing metadata to include. Defaults to None.

        Returns:
            Iterable[LIDocument]: Iterable over the created LlamaIndex documents.

        """
        file_paths = (
            file_path
            if isinstance(file_path, Iterable) and not isinstance(file_path, str)
            else [file_path]
        )

        for source in file_paths:
            dl_doc = self.doc_converter.convert(source).document
            text: str
            if self.export_type == self.ExportType.MARKDOWN:
                text = dl_doc.export_to_markdown(**self.md_export_kwargs)
            elif self.export_type == self.ExportType.JSON:
                text = json.dumps(dl_doc.export_to_dict())
            else:
                raise ValueError(f"Unexpected export type: {self.export_type}")
            li_doc = LIDocument(
                doc_id=self.id_func(doc=dl_doc, file_path=source),
                text=text,
            )
            li_doc.metadata = extra_info or {}
            yield li_doc

```
  
---|---  
###  lazy_load_data #
```
lazy_load_data(file_path: str | Path | Iterable[str] | Iterable[Path], extra_info: dict | None = None, fs: Optional[AbstractFileSystem] = None) -> Iterable[Document]

```

Lazily load from given source.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`file_path` |  `str | Path | Iterable[str] | Iterable[Path]` |  Document file source as single str (URL or local file) or pathlib.Path — or iterable thereof |  _required_  
`extra_info` |  `dict | None` |  Any pre-existing metadata to include. Defaults to None. |  `None`  
Returns:
Type | Description  
---|---  
`Iterable[Document]` |  Iterable[LIDocument]: Iterable over the created LlamaIndex documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-docling/llama_index/readers/docling/base.py`

| ```
def lazy_load_data(
    self,
    file_path: str | Path | Iterable[str] | Iterable[Path],
    extra_info: dict | None = None,
    fs: Optional[AbstractFileSystem] = None,
) -> Iterable[LIDocument]:
    """
    Lazily load from given source.

    Args:
        file_path (str | Path | Iterable[str] | Iterable[Path]): Document file source as single str (URL or local file) or pathlib.Path — or iterable thereof
        extra_info (dict | None, optional): Any pre-existing metadata to include. Defaults to None.

    Returns:
        Iterable[LIDocument]: Iterable over the created LlamaIndex documents.

    """
    file_paths = (
        file_path
        if isinstance(file_path, Iterable) and not isinstance(file_path, str)
        else [file_path]
    )

    for source in file_paths:
        dl_doc = self.doc_converter.convert(source).document
        text: str
        if self.export_type == self.ExportType.MARKDOWN:
            text = dl_doc.export_to_markdown(**self.md_export_kwargs)
        elif self.export_type == self.ExportType.JSON:
            text = json.dumps(dl_doc.export_to_dict())
        else:
            raise ValueError(f"Unexpected export type: {self.export_type}")
        li_doc = LIDocument(
            doc_id=self.id_func(doc=dl_doc, file_path=source),
            text=text,
        )
        li_doc.metadata = extra_info or {}
        yield li_doc

```
  
---|---
