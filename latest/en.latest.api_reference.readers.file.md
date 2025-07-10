# File
##  CSVReader #
Bases: `BaseReader`
CSV parser.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`concat_rows` |  `bool` |  whether to concatenate all rows into one document. If set to False, a Document will be created for each row. True by default. |  `True`  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/tabular/base.py`

| ```
class CSVReader(BaseReader):
    """
    CSV parser.

    Args:
        concat_rows (bool): whether to concatenate all rows into one document.
            If set to False, a Document will be created for each row.
            True by default.

    """

    def __init__(self, *args: Any, concat_rows: bool = True, **kwargs: Any) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._concat_rows = concat_rows

    def load_data(
        self, file: Path, extra_info: Optional[Dict] = None
    ) -> List[Document]:
        """
        Parse file.

        Returns:
            Union[str, List[str]]: a string or a List of strings.

        """
        try:
            import csv
        except ImportError:
            raise ImportError("csv module is required to read CSV files.")
        text_list = []
        with open(file) as fp:
            csv_reader = csv.reader(fp)
            for row in csv_reader:
                text_list.append(", ".join(row))

        metadata = {"filename": file.name, "extension": file.suffix}
        if extra_info:
            metadata = {**metadata, **extra_info}

        if self._concat_rows:
            return [Document(text="\n".join(text_list), metadata=metadata)]
        else:
            return [Document(text=text, metadata=metadata) for text in text_list]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None) -> List[Document]

```

Parse file.
Returns:
Type | Description  
---|---  
`List[Document]` |  Union[str, List[str]]: a string or a List of strings.  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/tabular/base.py`

| ```
def load_data(
    self, file: Path, extra_info: Optional[Dict] = None
) -> List[Document]:
    """
    Parse file.

    Returns:
        Union[str, List[str]]: a string or a List of strings.

    """
    try:
        import csv
    except ImportError:
        raise ImportError("csv module is required to read CSV files.")
    text_list = []
    with open(file) as fp:
        csv_reader = csv.reader(fp)
        for row in csv_reader:
            text_list.append(", ".join(row))

    metadata = {"filename": file.name, "extension": file.suffix}
    if extra_info:
        metadata = {**metadata, **extra_info}

    if self._concat_rows:
        return [Document(text="\n".join(text_list), metadata=metadata)]
    else:
        return [Document(text=text, metadata=metadata) for text in text_list]

```
  
---|---  
##  DocxReader #
Bases: `BaseReader`
Docx parser.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/docs/base.py`

| ```
class DocxReader(BaseReader):
    """Docx parser."""

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file."""
        if not isinstance(file, Path):
            file = Path(file)

        try:
            import docx2txt
        except ImportError:
            raise ImportError(
                "docx2txt is required to read Microsoft Word files: "
                "`pip install docx2txt`"
            )

        if fs:
            with fs.open(str(file)) as f:
                text = docx2txt.process(f)
        else:
            text = docx2txt.process(file)
        metadata = {"file_name": file.name}
        if extra_info is not None:
            metadata.update(extra_info)

        return [Document(text=text, metadata=metadata or {})]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/docs/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file."""
    if not isinstance(file, Path):
        file = Path(file)

    try:
        import docx2txt
    except ImportError:
        raise ImportError(
            "docx2txt is required to read Microsoft Word files: "
            "`pip install docx2txt`"
        )

    if fs:
        with fs.open(str(file)) as f:
            text = docx2txt.process(f)
    else:
        text = docx2txt.process(file)
    metadata = {"file_name": file.name}
    if extra_info is not None:
        metadata.update(extra_info)

    return [Document(text=text, metadata=metadata or {})]

```
  
---|---  
##  EpubReader #
Bases: `BaseReader`
Epub Parser.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/epub/base.py`

| ```
class EpubReader(BaseReader):
    """Epub Parser."""

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file."""
        try:
            import ebooklib
            import html2text
            from ebooklib import epub
        except ImportError:
            raise ImportError(
                "Please install extra dependencies that are required for "
                "the EpubReader: "
                "`pip install EbookLib html2text`"
            )
        if fs:
            logger.warning(
                "fs was specified but EpubReader doesn't support loading "
                "from fsspec filesystems. Will load from local filesystem instead."
            )

        text_list = []
        book = epub.read_epub(file, options={"ignore_ncx": True})

        # Iterate through all chapters.
        for item in book.get_items():
            # Chapters are typically located in epub documents items.
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                text_list.append(
                    html2text.html2text(item.get_content().decode("utf-8"))
                )

        text = "\n".join(text_list)
        return [Document(text=text, metadata=extra_info or {})]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/epub/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file."""
    try:
        import ebooklib
        import html2text
        from ebooklib import epub
    except ImportError:
        raise ImportError(
            "Please install extra dependencies that are required for "
            "the EpubReader: "
            "`pip install EbookLib html2text`"
        )
    if fs:
        logger.warning(
            "fs was specified but EpubReader doesn't support loading "
            "from fsspec filesystems. Will load from local filesystem instead."
        )

    text_list = []
    book = epub.read_epub(file, options={"ignore_ncx": True})

    # Iterate through all chapters.
    for item in book.get_items():
        # Chapters are typically located in epub documents items.
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            text_list.append(
                html2text.html2text(item.get_content().decode("utf-8"))
            )

    text = "\n".join(text_list)
    return [Document(text=text, metadata=extra_info or {})]

```
  
---|---  
##  FlatReader #
Bases: `BaseReader`
Flat reader.
Extract raw text from a file and save the file type in the metadata
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/flat/base.py`

| ```
class FlatReader(BaseReader):
    """
    Flat reader.

    Extract raw text from a file and save the file type in the metadata
    """

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)

    def _get_fs(
        self, file: Path, fs: Optional[AbstractFileSystem] = None
    ) -> AbstractFileSystem:
        if fs is None:
            fs = LocalFileSystem()
        return fs

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file into string."""
        fs = self._get_fs(file, fs)
        with fs.open(file, encoding="utf-8") as f:
            content = f.read()
        metadata = {"filename": file.name, "extension": file.suffix}
        if extra_info:
            metadata = {**metadata, **extra_info}

        return [Document(text=content, metadata=metadata)]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file into string.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/flat/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file into string."""
    fs = self._get_fs(file, fs)
    with fs.open(file, encoding="utf-8") as f:
        content = f.read()
    metadata = {"filename": file.name, "extension": file.suffix}
    if extra_info:
        metadata = {**metadata, **extra_info}

    return [Document(text=content, metadata=metadata)]

```
  
---|---  
##  HTMLTagReader #
Bases: `BaseReader`
Read HTML files and extract text from a specific tag with BeautifulSoup.
By default, reads the text from the `<section>` tag.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/html/base.py`

| ```
class HTMLTagReader(BaseReader):
    """
    Read HTML files and extract text from a specific tag with BeautifulSoup.

    By default, reads the text from the ``<section>`` tag.
    """

    def __init__(
        self,
        tag: str = "section",
        ignore_no_id: bool = False,
    ) -> None:
        self._tag = tag
        self._ignore_no_id = ignore_no_id

        super().__init__()

    def load_data(
        self, file: Path, extra_info: Optional[Dict] = None
    ) -> List[Document]:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("bs4 is required to read HTML files.")

        with open(file, encoding="utf-8") as html_file:
            soup = BeautifulSoup(html_file, "html.parser")

        tags = soup.find_all(self._tag)
        docs = []
        for tag in tags:
            tag_id = tag.get("id")
            tag_text = self._extract_text_from_tag(tag)

            if self._ignore_no_id and not tag_id:
                continue

            metadata = {
                "tag": self._tag,
                "tag_id": tag_id,
                "file_path": str(file),
            }
            metadata.update(extra_info or {})

            doc = Document(
                text=tag_text,
                metadata=metadata,
            )
            docs.append(doc)
        return docs

    def _extract_text_from_tag(self, tag: "Tag") -> str:
        try:
            from bs4 import NavigableString
        except ImportError:
            raise ImportError("bs4 is required to read HTML files.")

        texts = []
        for elem in tag.children:
            if isinstance(elem, NavigableString):
                if elem.strip():
                    texts.append(elem.strip())
            elif elem.name == self._tag:
                continue
            else:
                texts.append(elem.get_text().strip())
        return "\n".join(texts)

```
  
---|---  
##  HWPReader #
Bases: `BaseReader`
Hwp Parser.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/docs/base.py`

| ```
class HWPReader(BaseReader):
    """Hwp Parser."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.FILE_HEADER_SECTION = "FileHeader"
        self.HWP_SUMMARY_SECTION = "\x05HwpSummaryInformation"
        self.SECTION_NAME_LENGTH = len("Section")
        self.BODYTEXT_SECTION = "BodyText"
        self.HWP_TEXT_TAGS = [67]
        self.text = ""

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """
        Load data and extract table from Hwp file.

        Args:
            file (Path): Path for the Hwp file.

        Returns:
            List[Document]

        """
        import olefile

        if fs:
            logger.warning(
                "fs was specified but HWPReader doesn't support loading "
                "from fsspec filesystems. Will load from local filesystem instead."
            )

        if not isinstance(file, Path):
            file = Path(file)
        load_file = olefile.OleFileIO(file)
        file_dir = load_file.listdir()
        if self.is_valid(file_dir) is False:
            raise Exception("Not Valid HwpFile")

        result_text = self._get_text(load_file, file_dir)
        result = self._text_to_document(text=result_text, extra_info=extra_info)
        return [result]

    def is_valid(self, dirs: List[str]) -> bool:
        if [self.FILE_HEADER_SECTION] not in dirs:
            return False

        return [self.HWP_SUMMARY_SECTION] in dirs

    def get_body_sections(self, dirs: List[str]) -> List[str]:
        m = []
        for d in dirs:
            if d[0] == self.BODYTEXT_SECTION:
                m.append(int(d[1][self.SECTION_NAME_LENGTH :]))

        return ["BodyText/Section" + str(x) for x in sorted(m)]

    def _text_to_document(
        self, text: str, extra_info: Optional[Dict] = None
    ) -> Document:
        return Document(text=text, extra_info=extra_info or {})

    def get_text(self) -> str:
        return self.text

        # 전체 text 추출

    def _get_text(self, load_file: Any, file_dirs: List[str]) -> str:
        sections = self.get_body_sections(file_dirs)
        text = ""
        for section in sections:
            text += self.get_text_from_section(load_file, section)
            text += "\n"

        self.text = text
        return self.text

    def is_compressed(self, load_file: Any) -> bool:
        header = load_file.openstream("FileHeader")
        header_data = header.read()
        return (header_data[36] & 1) == 1

    def get_text_from_section(self, load_file: Any, section: str) -> str:
        bodytext = load_file.openstream(section)
        data = bodytext.read()

        unpacked_data = (
            zlib.decompress(data, -15) if self.is_compressed(load_file) else data
        )
        size = len(unpacked_data)

        i = 0

        text = ""
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3FF
            (header >> 10) & 0x3FF
            rec_len = (header >> 20) & 0xFFF

            if rec_type in self.HWP_TEXT_TAGS:
                rec_data = unpacked_data[i + 4 : i + 4 + rec_len]
                text += rec_data.decode("utf-16")
                text += "\n"

            i += 4 + rec_len

        return text

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Load data and extract table from Hwp file.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`file` |  `Path` |  Path for the Hwp file. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/docs/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """
    Load data and extract table from Hwp file.

    Args:
        file (Path): Path for the Hwp file.

    Returns:
        List[Document]

    """
    import olefile

    if fs:
        logger.warning(
            "fs was specified but HWPReader doesn't support loading "
            "from fsspec filesystems. Will load from local filesystem instead."
        )

    if not isinstance(file, Path):
        file = Path(file)
    load_file = olefile.OleFileIO(file)
    file_dir = load_file.listdir()
    if self.is_valid(file_dir) is False:
        raise Exception("Not Valid HwpFile")

    result_text = self._get_text(load_file, file_dir)
    result = self._text_to_document(text=result_text, extra_info=extra_info)
    return [result]

```
  
---|---  
##  IPYNBReader #
Bases: `BaseReader`
Image parser.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/ipynb/base.py`

| ```
class IPYNBReader(BaseReader):
    """Image parser."""

    def __init__(
        self,
        parser_config: Optional[Dict] = None,
        concatenate: bool = False,
    ):
        """Init params."""
        self._parser_config = parser_config
        self._concatenate = concatenate

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file."""
        if file.name.endswith(".ipynb"):
            try:
                import nbconvert
            except ImportError:
                raise ImportError("Please install nbconvert 'pip install nbconvert' ")
        if fs:
            with fs.open(file, encoding="utf-8") as f:
                string = nbconvert.exporters.ScriptExporter().from_file(f)[0]
        else:
            string = nbconvert.exporters.ScriptExporter().from_file(file)[0]
        # split each In[] cell into a separate string
        splits = re.split(r"In\[\d+\]:", string)
        # remove the first element, which is empty
        splits.pop(0)

        if self._concatenate:
            docs = [Document(text="\n\n".join(splits), metadata=extra_info or {})]
        else:
            docs = [Document(text=s, metadata=extra_info or {}) for s in splits]
        return docs

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/ipynb/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file."""
    if file.name.endswith(".ipynb"):
        try:
            import nbconvert
        except ImportError:
            raise ImportError("Please install nbconvert 'pip install nbconvert' ")
    if fs:
        with fs.open(file, encoding="utf-8") as f:
            string = nbconvert.exporters.ScriptExporter().from_file(f)[0]
    else:
        string = nbconvert.exporters.ScriptExporter().from_file(file)[0]
    # split each In[] cell into a separate string
    splits = re.split(r"In\[\d+\]:", string)
    # remove the first element, which is empty
    splits.pop(0)

    if self._concatenate:
        docs = [Document(text="\n\n".join(splits), metadata=extra_info or {})]
    else:
        docs = [Document(text=s, metadata=extra_info or {}) for s in splits]
    return docs

```
  
---|---  
##  ImageCaptionReader #
Bases: `BaseReader`
Image parser.
Caption image using Blip.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/image_caption/base.py`

| ```
class ImageCaptionReader(BaseReader):
    """
    Image parser.

    Caption image using Blip.

    """

    def __init__(
        self,
        parser_config: Optional[Dict] = None,
        keep_image: bool = False,
        prompt: Optional[str] = None,
    ):
        """Init params."""
        if parser_config is None:
            """Init parser."""
            try:
                import sentencepiece  # noqa
                import torch
                from PIL import Image  # noqa
                from transformers import BlipForConditionalGeneration, BlipProcessor
            except ImportError:
                raise ImportError(
                    "Please install extra dependencies that are required for "
                    "the ImageCaptionReader: "
                    "`pip install torch transformers sentencepiece Pillow`"
                )

            device = infer_torch_device()
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            processor = BlipProcessor.from_pretrained(
                "Salesforce/blip-image-captioning-large"
            )
            model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-large", torch_dtype=dtype
            )

            parser_config = {
                "processor": processor,
                "model": model,
                "device": device,
                "dtype": dtype,
            }

        self._parser_config = parser_config
        self._keep_image = keep_image
        self._prompt = prompt

    def load_data(
        self, file: Path, extra_info: Optional[Dict] = None
    ) -> List[Document]:
        """Parse file."""
        from llama_index.core.img_utils import img_2_b64
        from PIL import Image

        # load document image
        image = Image.open(file)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Encode image into base64 string and keep in document
        image_str: Optional[str] = None
        if self._keep_image:
            image_str = img_2_b64(image)

        # Parse image into text
        model = self._parser_config["model"]
        processor = self._parser_config["processor"]

        device = self._parser_config["device"]
        dtype = self._parser_config["dtype"]
        model.to(device)

        # unconditional image captioning

        inputs = processor(image, self._prompt, return_tensors="pt").to(device, dtype)

        out = model.generate(**inputs)
        text_str = processor.decode(out[0], skip_special_tokens=True)

        return [
            ImageDocument(
                text=text_str,
                image=image_str,
                image_path=str(file),
                metadata=extra_info or {},
            )
        ]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/image_caption/base.py`

| ```
def load_data(
    self, file: Path, extra_info: Optional[Dict] = None
) -> List[Document]:
    """Parse file."""
    from llama_index.core.img_utils import img_2_b64
    from PIL import Image

    # load document image
    image = Image.open(file)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Encode image into base64 string and keep in document
    image_str: Optional[str] = None
    if self._keep_image:
        image_str = img_2_b64(image)

    # Parse image into text
    model = self._parser_config["model"]
    processor = self._parser_config["processor"]

    device = self._parser_config["device"]
    dtype = self._parser_config["dtype"]
    model.to(device)

    # unconditional image captioning

    inputs = processor(image, self._prompt, return_tensors="pt").to(device, dtype)

    out = model.generate(**inputs)
    text_str = processor.decode(out[0], skip_special_tokens=True)

    return [
        ImageDocument(
            text=text_str,
            image=image_str,
            image_path=str(file),
            metadata=extra_info or {},
        )
    ]

```
  
---|---  
##  ImageReader #
Bases: `BaseReader`
Image parser.
Extract text from images using DONUT or pytesseract.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/image/base.py`

| ```
class ImageReader(BaseReader):
    """
    Image parser.

    Extract text from images using DONUT or pytesseract.

    """

    def __init__(
        self,
        parser_config: Optional[Dict] = None,
        keep_image: bool = False,
        parse_text: bool = False,
        text_type: str = "text",
        pytesseract_model_kwargs: Dict[str, Any] = {},
    ):
        """Init parser."""
        self._text_type = text_type
        if parser_config is None and parse_text:
            if text_type == "plain_text":
                try:
                    import pytesseract
                except ImportError:
                    raise ImportError(
                        "Please install extra dependencies that are required for "
                        "the ImageReader when text_type is 'plain_text': "
                        "`pip install pytesseract`"
                    )
                processor = None
                model = pytesseract
            else:
                try:
                    import sentencepiece  # noqa
                    import torch  # noqa
                    from PIL import Image  # noqa
                    from transformers import DonutProcessor, VisionEncoderDecoderModel
                except ImportError:
                    raise ImportError(
                        "Please install extra dependencies that are required for "
                        "the ImageCaptionReader: "
                        "`pip install torch transformers sentencepiece Pillow`"
                    )

                processor = DonutProcessor.from_pretrained(
                    "naver-clova-ix/donut-base-finetuned-cord-v2"
                )
                model = VisionEncoderDecoderModel.from_pretrained(
                    "naver-clova-ix/donut-base-finetuned-cord-v2"
                )
            parser_config = {"processor": processor, "model": model}

        self._parser_config = parser_config
        self._keep_image = keep_image
        self._parse_text = parse_text
        self._pytesseract_model_kwargs = pytesseract_model_kwargs

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file."""
        from llama_index.core.img_utils import img_2_b64
        from PIL import Image

        # load document image
        if fs:
            with fs.open(path=file) as f:
                image = Image.open(BytesIO(f.read()))
        else:
            image = Image.open(file)

        if image.mode != "RGB":
            image = image.convert("RGB")

        # Encode image into base64 string and keep in document
        image_str: Optional[str] = None
        if self._keep_image:
            image_str = img_2_b64(image)

        # Parse image into text
        text_str: str = ""
        if self._parse_text:
            assert self._parser_config is not None
            model = self._parser_config["model"]
            processor = self._parser_config["processor"]

            if processor:
                device = infer_torch_device()
                model.to(device)

                # prepare decoder inputs
                task_prompt = "<s_cord-v2>"
                decoder_input_ids = processor.tokenizer(
                    task_prompt, add_special_tokens=False, return_tensors="pt"
                ).input_ids

                pixel_values = processor(image, return_tensors="pt").pixel_values

                outputs = model.generate(
                    pixel_values.to(device),
                    decoder_input_ids=decoder_input_ids.to(device),
                    max_length=model.decoder.config.max_position_embeddings,
                    early_stopping=True,
                    pad_token_id=processor.tokenizer.pad_token_id,
                    eos_token_id=processor.tokenizer.eos_token_id,
                    use_cache=True,
                    num_beams=3,
                    bad_words_ids=[[processor.tokenizer.unk_token_id]],
                    return_dict_in_generate=True,
                )

                sequence = processor.batch_decode(outputs.sequences)[0]
                sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(
                    processor.tokenizer.pad_token, ""
                )
                # remove first task start token
                text_str = re.sub(r"<.*?>", "", sequence, count=1).strip()
            else:
                import pytesseract

                model = cast(pytesseract, self._parser_config["model"])
                text_str = model.image_to_string(
                    image, **self._pytesseract_model_kwargs
                )

        return [
            ImageDocument(
                text=text_str,
                image=image_str,
                image_path=str(file),
                metadata=extra_info or {},
            )
        ]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/image/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file."""
    from llama_index.core.img_utils import img_2_b64
    from PIL import Image

    # load document image
    if fs:
        with fs.open(path=file) as f:
            image = Image.open(BytesIO(f.read()))
    else:
        image = Image.open(file)

    if image.mode != "RGB":
        image = image.convert("RGB")

    # Encode image into base64 string and keep in document
    image_str: Optional[str] = None
    if self._keep_image:
        image_str = img_2_b64(image)

    # Parse image into text
    text_str: str = ""
    if self._parse_text:
        assert self._parser_config is not None
        model = self._parser_config["model"]
        processor = self._parser_config["processor"]

        if processor:
            device = infer_torch_device()
            model.to(device)

            # prepare decoder inputs
            task_prompt = "<s_cord-v2>"
            decoder_input_ids = processor.tokenizer(
                task_prompt, add_special_tokens=False, return_tensors="pt"
            ).input_ids

            pixel_values = processor(image, return_tensors="pt").pixel_values

            outputs = model.generate(
                pixel_values.to(device),
                decoder_input_ids=decoder_input_ids.to(device),
                max_length=model.decoder.config.max_position_embeddings,
                early_stopping=True,
                pad_token_id=processor.tokenizer.pad_token_id,
                eos_token_id=processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=3,
                bad_words_ids=[[processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )

            sequence = processor.batch_decode(outputs.sequences)[0]
            sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(
                processor.tokenizer.pad_token, ""
            )
            # remove first task start token
            text_str = re.sub(r"<.*?>", "", sequence, count=1).strip()
        else:
            import pytesseract

            model = cast(pytesseract, self._parser_config["model"])
            text_str = model.image_to_string(
                image, **self._pytesseract_model_kwargs
            )

    return [
        ImageDocument(
            text=text_str,
            image=image_str,
            image_path=str(file),
            metadata=extra_info or {},
        )
    ]

```
  
---|---  
##  ImageTabularChartReader #
Bases: `BaseReader`
Image parser.
Extract tabular data from a chart or figure.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/image_deplot/base.py`

| ```
class ImageTabularChartReader(BaseReader):
    """
    Image parser.

    Extract tabular data from a chart or figure.

    """

    def __init__(
        self,
        parser_config: Optional[Dict] = None,
        keep_image: bool = False,
        max_output_tokens=512,
        prompt: str = "Generate underlying data table of the figure below:",
    ):
        """Init params."""
        if parser_config is None:
            try:
                import torch
                from PIL import Image  # noqa: F401
                from transformers import (
                    Pix2StructForConditionalGeneration,
                    Pix2StructProcessor,
                )
            except ImportError:
                raise ImportError(
                    "Please install extra dependencies that are required for "
                    "the ImageCaptionReader: "
                    "`pip install torch transformers Pillow`"
                )

            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            processor = Pix2StructProcessor.from_pretrained("google/deplot")
            model = Pix2StructForConditionalGeneration.from_pretrained(
                "google/deplot", torch_dtype=dtype
            )
            parser_config = {
                "processor": processor,
                "model": model,
                "device": device,
                "dtype": dtype,
            }

        self._parser_config = parser_config
        self._keep_image = keep_image
        self._max_output_tokens = max_output_tokens
        self._prompt = prompt

    def load_data(
        self, file: Path, extra_info: Optional[Dict] = None
    ) -> List[Document]:
        """Parse file."""
        from llama_index.core.img_utils import img_2_b64
        from PIL import Image

        # load document image
        image = Image.open(file)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Encode image into base64 string and keep in document
        image_str: Optional[str] = None
        if self._keep_image:
            image_str = img_2_b64(image)

        # Parse image into text
        model = self._parser_config["model"]
        processor = self._parser_config["processor"]

        device = self._parser_config["device"]
        dtype = self._parser_config["dtype"]
        model.to(device)

        # unconditional image captioning

        inputs = processor(image, self._prompt, return_tensors="pt").to(device, dtype)

        out = model.generate(**inputs, max_new_tokens=self._max_output_tokens)
        text_str = "Figure or chart with tabular data: " + processor.decode(
            out[0], skip_special_tokens=True
        )

        return [
            ImageDocument(
                text=text_str,
                image=image_str,
                extra_info=extra_info or {},
            )
        ]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/image_deplot/base.py`

| ```
def load_data(
    self, file: Path, extra_info: Optional[Dict] = None
) -> List[Document]:
    """Parse file."""
    from llama_index.core.img_utils import img_2_b64
    from PIL import Image

    # load document image
    image = Image.open(file)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Encode image into base64 string and keep in document
    image_str: Optional[str] = None
    if self._keep_image:
        image_str = img_2_b64(image)

    # Parse image into text
    model = self._parser_config["model"]
    processor = self._parser_config["processor"]

    device = self._parser_config["device"]
    dtype = self._parser_config["dtype"]
    model.to(device)

    # unconditional image captioning

    inputs = processor(image, self._prompt, return_tensors="pt").to(device, dtype)

    out = model.generate(**inputs, max_new_tokens=self._max_output_tokens)
    text_str = "Figure or chart with tabular data: " + processor.decode(
        out[0], skip_special_tokens=True
    )

    return [
        ImageDocument(
            text=text_str,
            image=image_str,
            extra_info=extra_info or {},
        )
    ]

```
  
---|---  
##  ImageVisionLLMReader #
Bases: `BaseReader`
Image parser.
Caption image using Blip2 (a multimodal VisionLLM similar to GPT4).
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/image_vision_llm/base.py`

| ```
class ImageVisionLLMReader(BaseReader):
    """
    Image parser.

    Caption image using Blip2 (a multimodal VisionLLM similar to GPT4).

    """

    def __init__(
        self,
        parser_config: Optional[Dict] = None,
        keep_image: bool = False,
        prompt: str = "Question: describe what you see in this image. Answer:",
    ):
        """Init params."""
        if parser_config is None:
            try:
                import sentencepiece  # noqa
                import torch
                from PIL import Image  # noqa
                from transformers import Blip2ForConditionalGeneration, Blip2Processor
            except ImportError:
                raise ImportError(
                    "Please install extra dependencies that are required for "
                    "the ImageCaptionReader: "
                    "`pip install torch transformers sentencepiece Pillow`"
                )

            self._torch = torch
            self._torch_imported = True

            device = infer_torch_device()
            dtype = (
                self._torch.float16
                if self._torch.cuda.is_available()
                else self._torch.float32
            )
            processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
            model = Blip2ForConditionalGeneration.from_pretrained(
                "Salesforce/blip2-opt-2.7b", torch_dtype=dtype
            )
            parser_config = {
                "processor": processor,
                "model": model,
                "device": device,
                "dtype": dtype,
            }

        # Try to import PyTorch in order to run inference efficiently.
        self._import_torch()

        self._parser_config = parser_config
        self._keep_image = keep_image
        self._prompt = prompt

    def load_data(
        self, file: Path, extra_info: Optional[Dict] = None
    ) -> List[Document]:
        """Parse file."""
        from llama_index.core.img_utils import img_2_b64
        from PIL import Image

        # load document image
        image = Image.open(file)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Encode image into base64 string and keep in document
        image_str: Optional[str] = None
        if self._keep_image:
            image_str = img_2_b64(image)

        # Parse image into text
        model = self._parser_config["model"]
        processor = self._parser_config["processor"]

        device = self._parser_config["device"]
        dtype = self._parser_config["dtype"]
        model.to(device)

        # unconditional image captioning

        inputs = processor(image, self._prompt, return_tensors="pt").to(device, dtype)

        if self._torch_imported:
            # Gradients are not needed during inference. If PyTorch is
            # installed, we can instruct it to not track the gradients.
            # This reduces GPU memory usage and improves inference efficiency.
            with self._torch.no_grad():
                out = model.generate(**inputs)
        else:
            # Fallback to less efficient behavior if PyTorch is not installed.
            out = model.generate(**inputs)

        text_str = processor.decode(out[0], skip_special_tokens=True)

        return [
            ImageDocument(
                text=text_str,
                image=image_str,
                image_path=str(file),
                metadata=extra_info or {},
            )
        ]

    def _import_torch(self) -> None:
        self._torch = None

        try:
            import torch

            self._torch = torch
            self._torch_imported = True
        except ImportError:
            self._torch_imported = False

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/image_vision_llm/base.py`

| ```
def load_data(
    self, file: Path, extra_info: Optional[Dict] = None
) -> List[Document]:
    """Parse file."""
    from llama_index.core.img_utils import img_2_b64
    from PIL import Image

    # load document image
    image = Image.open(file)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Encode image into base64 string and keep in document
    image_str: Optional[str] = None
    if self._keep_image:
        image_str = img_2_b64(image)

    # Parse image into text
    model = self._parser_config["model"]
    processor = self._parser_config["processor"]

    device = self._parser_config["device"]
    dtype = self._parser_config["dtype"]
    model.to(device)

    # unconditional image captioning

    inputs = processor(image, self._prompt, return_tensors="pt").to(device, dtype)

    if self._torch_imported:
        # Gradients are not needed during inference. If PyTorch is
        # installed, we can instruct it to not track the gradients.
        # This reduces GPU memory usage and improves inference efficiency.
        with self._torch.no_grad():
            out = model.generate(**inputs)
    else:
        # Fallback to less efficient behavior if PyTorch is not installed.
        out = model.generate(**inputs)

    text_str = processor.decode(out[0], skip_special_tokens=True)

    return [
        ImageDocument(
            text=text_str,
            image=image_str,
            image_path=str(file),
            metadata=extra_info or {},
        )
    ]

```
  
---|---  
##  MarkdownReader #
Bases: `BaseReader`
Markdown parser.
Extract text from markdown files. Returns dictionary with keys as headers and values as the text between headers.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/markdown/base.py`

| ```
class MarkdownReader(BaseReader):
    """
    Markdown parser.

    Extract text from markdown files.
    Returns dictionary with keys as headers and values as the text between headers.

    """

    def __init__(
        self,
        *args: Any,
        remove_hyperlinks: bool = True,
        remove_images: bool = True,
        separator: str = " ",
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images
        self._separator = separator

    def markdown_to_tups(self, markdown_text: str) -> List[Tuple[Optional[str], str]]:
        """Convert a markdown file to a list of tuples containing header and text."""
        markdown_tups: List[Tuple[Optional[str], str]] = []
        lines = markdown_text.split("\n")

        current_lines = []
        in_code_block = False
        headers = {}
        for line in lines:
            # Toggle code block state
            if line.startswith("```"):
                in_code_block = not in_code_block

            if in_code_block:
                current_lines.append(line)
                continue
            # Process headers only when not in a code block
            else:
                line = line.strip()
                if not line:
                    continue

                header_match = re.match(r"^(#+)\s+(.*)", line)
                if header_match:
                    if current_lines and not headers:
                        # Add content before first header
                        markdown_tups.append((None, "\n".join(current_lines)))
                        current_lines.clear()
                    # Extract header level and text
                    header_level = len(
                        header_match.group(1)
                    )  # number of '#' indicates level
                    current_header = header_match.group(2)  # the header text
                    if headers.get(header_level):
                        # Add previous section to the list before switching header
                        markdown_tups.append(
                            (
                                self._separator.join(headers.values()),
                                "\n".join(current_lines),
                            )
                        )
                        # remove all headers with level greater than current header
                        headers = {k: v for k, v in headers.items() if k < header_level}
                        current_lines.clear()

                    headers[header_level] = current_header
                else:
                    current_lines.append(line)

        # Append the last section
        if current_lines or headers:
            markdown_tups.append(
                (self._separator.join(headers.values()), "\n".join(current_lines))
            )

        # Postprocess the tuples before returning
        return [
            (
                key.strip() if key else None,  # Clean up header (strip whitespace)
                re.sub(r"<.*?>", "", value),  # Remove HTML tags
            )
            for key, value in markdown_tups
        ]

    def remove_images(self, content: str) -> str:
        """Remove images in markdown content but keep the description."""
        pattern = r"![(.?)](.?)"
        return re.sub(pattern, r"\1", content)

    def remove_hyperlinks(self, content: str) -> str:
        """Remove hyperlinks in markdown content."""
        pattern = r"\[(.*?)\]\((.*?)\)"
        return re.sub(pattern, r"\1", content)

    def _init_parser(self) -> Dict:
        """Initialize the parser with the config."""
        return {}

    def parse_tups(
        self,
        filepath: str,
        errors: str = "ignore",
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Tuple[Optional[str], str]]:
        """Parse file into tuples."""
        fs = fs or LocalFileSystem()
        with fs.open(filepath, encoding="utf-8") as f:
            content = f.read().decode(encoding="utf-8")
        if self._remove_hyperlinks:
            content = self.remove_hyperlinks(content)
        if self._remove_images:
            content = self.remove_images(content)
        return self.markdown_to_tups(content)

    def load_data(
        self,
        file: str,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file into string."""
        tups = self.parse_tups(file, fs=fs)
        results = []

        for header, text in tups:
            if header is None:
                results.append(Document(text=text, metadata=extra_info or {}))
            else:
                results.append(
                    Document(text=f"\n\n{header}\n{text}", metadata=extra_info or {})
                )
        return results

```
  
---|---  
###  markdown_to_tups #
```
markdown_to_tups(markdown_text: str) -> List[Tuple[Optional[str], str]]

```

Convert a markdown file to a list of tuples containing header and text.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/markdown/base.py`
```
 39
 40
 41
 42
 43
 44
 45
 46
 47
 48
 49
 50
 51
 52
 53
 54
 55
 56
 57
 58
 59
 60
 61
 62
 63
 64
 65
 66
 67
 68
 69
 70
 71
 72
 73
 74
 75
 76
 77
 78
 79
 80
 81
 82
 83
 84
 85
 86
 87
 88
 89
 90
 91
 92
 93
 94
 95
 96
 97
 98
 99
100
101
```
| ```
def markdown_to_tups(self, markdown_text: str) -> List[Tuple[Optional[str], str]]:
    """Convert a markdown file to a list of tuples containing header and text."""
    markdown_tups: List[Tuple[Optional[str], str]] = []
    lines = markdown_text.split("\n")

    current_lines = []
    in_code_block = False
    headers = {}
    for line in lines:
        # Toggle code block state
        if line.startswith("```"):
            in_code_block = not in_code_block

        if in_code_block:
            current_lines.append(line)
            continue
        # Process headers only when not in a code block
        else:
            line = line.strip()
            if not line:
                continue

            header_match = re.match(r"^(#+)\s+(.*)", line)
            if header_match:
                if current_lines and not headers:
                    # Add content before first header
                    markdown_tups.append((None, "\n".join(current_lines)))
                    current_lines.clear()
                # Extract header level and text
                header_level = len(
                    header_match.group(1)
                )  # number of '#' indicates level
                current_header = header_match.group(2)  # the header text
                if headers.get(header_level):
                    # Add previous section to the list before switching header
                    markdown_tups.append(
                        (
                            self._separator.join(headers.values()),
                            "\n".join(current_lines),
                        )
                    )
                    # remove all headers with level greater than current header
                    headers = {k: v for k, v in headers.items() if k < header_level}
                    current_lines.clear()

                headers[header_level] = current_header
            else:
                current_lines.append(line)

    # Append the last section
    if current_lines or headers:
        markdown_tups.append(
            (self._separator.join(headers.values()), "\n".join(current_lines))
        )

    # Postprocess the tuples before returning
    return [
        (
            key.strip() if key else None,  # Clean up header (strip whitespace)
            re.sub(r"<.*?>", "", value),  # Remove HTML tags
        )
        for key, value in markdown_tups
    ]

```
  
---|---  
###  remove_images #
```
remove_images(content: str) -> str

```

Remove images in markdown content but keep the description.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/markdown/base.py`

| ```
def remove_images(self, content: str) -> str:
    """Remove images in markdown content but keep the description."""
    pattern = r"![(.?)](.?)"
    return re.sub(pattern, r"\1", content)

```
  
---|---  
###  remove_hyperlinks #
```
remove_hyperlinks(content: str) -> str

```

Remove hyperlinks in markdown content.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/markdown/base.py`

| ```
def remove_hyperlinks(self, content: str) -> str:
    """Remove hyperlinks in markdown content."""
    pattern = r"\[(.*?)\]\((.*?)\)"
    return re.sub(pattern, r"\1", content)

```
  
---|---  
###  parse_tups #
```
parse_tups(filepath: str, errors: str = 'ignore', fs: Optional[AbstractFileSystem] = None) -> List[Tuple[Optional[str], str]]

```

Parse file into tuples.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/markdown/base.py`

| ```
def parse_tups(
    self,
    filepath: str,
    errors: str = "ignore",
    fs: Optional[AbstractFileSystem] = None,
) -> List[Tuple[Optional[str], str]]:
    """Parse file into tuples."""
    fs = fs or LocalFileSystem()
    with fs.open(filepath, encoding="utf-8") as f:
        content = f.read().decode(encoding="utf-8")
    if self._remove_hyperlinks:
        content = self.remove_hyperlinks(content)
    if self._remove_images:
        content = self.remove_images(content)
    return self.markdown_to_tups(content)

```
  
---|---  
###  load_data #
```
load_data(file: str, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file into string.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/markdown/base.py`

| ```
def load_data(
    self,
    file: str,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file into string."""
    tups = self.parse_tups(file, fs=fs)
    results = []

    for header, text in tups:
        if header is None:
            results.append(Document(text=text, metadata=extra_info or {}))
        else:
            results.append(
                Document(text=f"\n\n{header}\n{text}", metadata=extra_info or {})
            )
    return results

```
  
---|---  
##  MboxReader #
Bases: `BaseReader`
Mbox parser.
Extract messages from mailbox files. Returns string including date, subject, sender, receiver and content for each message.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/mbox/base.py`

| ```
class MboxReader(BaseReader):
    """
    Mbox parser.

    Extract messages from mailbox files.
    Returns string including date, subject, sender, receiver and
    content for each message.

    """

    DEFAULT_MESSAGE_FORMAT: str = (
        "Date: {_date}\n"
        "From: {_from}\n"
        "To: {_to}\n"
        "Subject: {_subject}\n"
        "Content: {_content}"
    )

    def __init__(
        self,
        *args: Any,
        max_count: int = 0,
        message_format: str = DEFAULT_MESSAGE_FORMAT,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        try:
            from bs4 import BeautifulSoup  # noqa
        except ImportError:
            raise ImportError(
                "`beautifulsoup4` package not found: `pip install beautifulsoup4`"
            )

        super().__init__(*args, **kwargs)
        self.max_count = max_count
        self.message_format = message_format

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file into string."""
        # Import required libraries
        import mailbox
        from email.parser import BytesParser
        from email.policy import default

        from bs4 import BeautifulSoup

        if fs:
            logger.warning(
                "fs was specified but MboxReader doesn't support loading "
                "from fsspec filesystems. Will load from local filesystem instead."
            )

        i = 0
        results: List[str] = []
        # Load file using mailbox
        bytes_parser = BytesParser(policy=default).parse
        mbox = mailbox.mbox(file, factory=bytes_parser)  # type: ignore

        # Iterate through all messages
        for _, _msg in enumerate(mbox):
            try:
                msg: mailbox.mboxMessage = _msg
                # Parse multipart messages
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get("Content-Disposition"))
                        if ctype == "text/plain" and "attachment" not in cdispo:
                            content = part.get_payload(decode=True)  # decode
                            break
                # Get plain message payload for non-multipart messages
                else:
                    content = msg.get_payload(decode=True)

                # Parse message HTML content and remove unneeded whitespace
                soup = BeautifulSoup(content)
                stripped_content = " ".join(soup.get_text().split())
                # Format message to include date, sender, receiver and subject
                msg_string = self.message_format.format(
                    _date=msg["date"],
                    _from=msg["from"],
                    _to=msg["to"],
                    _subject=msg["subject"],
                    _content=stripped_content,
                )
                # Add message string to results
                results.append(msg_string)
            except Exception as e:
                logger.warning(f"Failed to parse message:\n{_msg}\n with exception {e}")

            # Increment counter and return if max count is met
            i += 1
            if self.max_count > 0 and i >= self.max_count:
                break

        return [Document(text=result, metadata=extra_info or {}) for result in results]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file into string.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/mbox/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file into string."""
    # Import required libraries
    import mailbox
    from email.parser import BytesParser
    from email.policy import default

    from bs4 import BeautifulSoup

    if fs:
        logger.warning(
            "fs was specified but MboxReader doesn't support loading "
            "from fsspec filesystems. Will load from local filesystem instead."
        )

    i = 0
    results: List[str] = []
    # Load file using mailbox
    bytes_parser = BytesParser(policy=default).parse
    mbox = mailbox.mbox(file, factory=bytes_parser)  # type: ignore

    # Iterate through all messages
    for _, _msg in enumerate(mbox):
        try:
            msg: mailbox.mboxMessage = _msg
            # Parse multipart messages
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in cdispo:
                        content = part.get_payload(decode=True)  # decode
                        break
            # Get plain message payload for non-multipart messages
            else:
                content = msg.get_payload(decode=True)

            # Parse message HTML content and remove unneeded whitespace
            soup = BeautifulSoup(content)
            stripped_content = " ".join(soup.get_text().split())
            # Format message to include date, sender, receiver and subject
            msg_string = self.message_format.format(
                _date=msg["date"],
                _from=msg["from"],
                _to=msg["to"],
                _subject=msg["subject"],
                _content=stripped_content,
            )
            # Add message string to results
            results.append(msg_string)
        except Exception as e:
            logger.warning(f"Failed to parse message:\n{_msg}\n with exception {e}")

        # Increment counter and return if max count is met
        i += 1
        if self.max_count > 0 and i >= self.max_count:
            break

    return [Document(text=result, metadata=extra_info or {}) for result in results]

```
  
---|---  
##  PDFReader #
Bases: `BaseReader`
PDF parser.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/docs/base.py`

| ```
class PDFReader(BaseReader):
    """PDF parser."""

    def __init__(self, return_full_document: Optional[bool] = False) -> None:
        """
        Initialize PDFReader.
        """
        self.return_full_document = return_full_document

    @retry(
        stop=stop_after_attempt(RETRY_TIMES),
    )
    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file."""
        if not isinstance(file, Path):
            file = Path(file)

        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "pypdf is required to read PDF files: `pip install pypdf`"
            )
        fs = fs or get_default_fs()
        with fs.open(str(file), "rb") as fp:
            # Load the file in memory if the filesystem is not the default one to avoid
            # issues with pypdf
            stream = fp if is_default_fs(fs) else io.BytesIO(fp.read())

            # Create a PDF object
            pdf = pypdf.PdfReader(stream)

            # Get the number of pages in the PDF document
            num_pages = len(pdf.pages)

            docs = []

            # This block returns a whole PDF as a single Document
            if self.return_full_document:
                metadata = {"file_name": file.name}
                if extra_info is not None:
                    metadata.update(extra_info)

                # Join text extracted from each page
                text = "\n".join(
                    pdf.pages[page].extract_text() for page in range(num_pages)
                )

                docs.append(Document(text=text, metadata=metadata))

            # This block returns each page of a PDF as its own Document
            else:
                # Iterate over every page

                for page in range(num_pages):
                    # Extract the text from the page
                    page_text = pdf.pages[page].extract_text()
                    page_label = pdf.page_labels[page]

                    metadata = {"page_label": page_label, "file_name": file.name}
                    if extra_info is not None:
                        metadata.update(extra_info)

                    docs.append(Document(text=page_text, metadata=metadata))

            return docs

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/docs/base.py`

| ```
@retry(
    stop=stop_after_attempt(RETRY_TIMES),
)
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file."""
    if not isinstance(file, Path):
        file = Path(file)

    try:
        import pypdf
    except ImportError:
        raise ImportError(
            "pypdf is required to read PDF files: `pip install pypdf`"
        )
    fs = fs or get_default_fs()
    with fs.open(str(file), "rb") as fp:
        # Load the file in memory if the filesystem is not the default one to avoid
        # issues with pypdf
        stream = fp if is_default_fs(fs) else io.BytesIO(fp.read())

        # Create a PDF object
        pdf = pypdf.PdfReader(stream)

        # Get the number of pages in the PDF document
        num_pages = len(pdf.pages)

        docs = []

        # This block returns a whole PDF as a single Document
        if self.return_full_document:
            metadata = {"file_name": file.name}
            if extra_info is not None:
                metadata.update(extra_info)

            # Join text extracted from each page
            text = "\n".join(
                pdf.pages[page].extract_text() for page in range(num_pages)
            )

            docs.append(Document(text=text, metadata=metadata))

        # This block returns each page of a PDF as its own Document
        else:
            # Iterate over every page

            for page in range(num_pages):
                # Extract the text from the page
                page_text = pdf.pages[page].extract_text()
                page_label = pdf.page_labels[page]

                metadata = {"page_label": page_label, "file_name": file.name}
                if extra_info is not None:
                    metadata.update(extra_info)

                docs.append(Document(text=page_text, metadata=metadata))

        return docs

```
  
---|---  
##  PagedCSVReader #
Bases: `BaseReader`
Paged CSV parser.
Displayed each row in an LLM-friendly format on a separate document.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`encoding` |  `str` |  Encoding used to open the file. utf-8 by default. |  `'utf-8'`  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/paged_csv/base.py`

| ```
class PagedCSVReader(BaseReader):
    """
    Paged CSV parser.

    Displayed each row in an LLM-friendly format on a separate document.

    Args:
        encoding (str): Encoding used to open the file.
            utf-8 by default.

    """

    def __init__(self, *args: Any, encoding: str = "utf-8", **kwargs: Any) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._encoding = encoding

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        delimiter: str = ",",
        quotechar: str = '"',
    ) -> List[Document]:
        """Parse file."""
        import csv

        docs = []
        with open(file, encoding=self._encoding) as fp:
            csv_reader = csv.DictReader(f=fp, delimiter=delimiter, quotechar=quotechar)  # type: ignore
            for row in csv_reader:
                docs.append(
                    Document(
                        text="\n".join(
                            f"{k.strip()}: {v.strip()}" for k, v in row.items()
                        ),
                        extra_info=extra_info or {},
                    )
                )
        return docs

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, delimiter: str = ',', quotechar: str = '"') -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/paged_csv/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    delimiter: str = ",",
    quotechar: str = '"',
) -> List[Document]:
    """Parse file."""
    import csv

    docs = []
    with open(file, encoding=self._encoding) as fp:
        csv_reader = csv.DictReader(f=fp, delimiter=delimiter, quotechar=quotechar)  # type: ignore
        for row in csv_reader:
            docs.append(
                Document(
                    text="\n".join(
                        f"{k.strip()}: {v.strip()}" for k, v in row.items()
                    ),
                    extra_info=extra_info or {},
                )
            )
    return docs

```
  
---|---  
##  PandasCSVReader #
Bases: `BaseReader`
Pandas-based CSV parser.
Parses CSVs using the separator detection from Pandas `read_csv`function. If special parameters are required, use the `pandas_config` dict.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`concat_rows` |  `bool` |  whether to concatenate all rows into one document. If set to False, a Document will be created for each row. True by default. |  `True`  
`col_joiner` |  `str` |  Separator to use for joining cols per row. Set to ", " by default. |  `', '`  
`row_joiner` |  `str` |  Separator to use for joining each row. Only used when `concat_rows=True`. Set to "\n" by default. |  `'\n'`  
`pandas_config` |  `dict` |  Options for the `pandas.read_csv` function call. Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html for more information. Set to empty dict by default, this means pandas will try to figure out the separators, table head, etc. on its own. |  `{}`  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/tabular/base.py`

| ```
class PandasCSVReader(BaseReader):
    r"""
    Pandas-based CSV parser.

    Parses CSVs using the separator detection from Pandas `read_csv`function.
    If special parameters are required, use the `pandas_config` dict.

    Args:
        concat_rows (bool): whether to concatenate all rows into one document.
            If set to False, a Document will be created for each row.
            True by default.

        col_joiner (str): Separator to use for joining cols per row.
            Set to ", " by default.

        row_joiner (str): Separator to use for joining each row.
            Only used when `concat_rows=True`.
            Set to "\n" by default.

        pandas_config (dict): Options for the `pandas.read_csv` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            for more information.
            Set to empty dict by default, this means pandas will try to figure
            out the separators, table head, etc. on its own.

    """

    def __init__(
        self,
        *args: Any,
        concat_rows: bool = True,
        col_joiner: str = ", ",
        row_joiner: str = "\n",
        pandas_config: dict = {},
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._concat_rows = concat_rows
        self._col_joiner = col_joiner
        self._row_joiner = row_joiner
        self._pandas_config = pandas_config

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file."""
        if fs:
            with fs.open(file) as f:
                df = pd.read_csv(f, **self._pandas_config)
        else:
            df = pd.read_csv(file, **self._pandas_config)

        text_list = df.apply(
            lambda row: (self._col_joiner).join(row.astype(str).tolist()), axis=1
        ).tolist()

        if self._concat_rows:
            return [
                Document(
                    text=(self._row_joiner).join(text_list), metadata=extra_info or {}
                )
            ]
        else:
            return [
                Document(text=text, metadata=extra_info or {}) for text in text_list
            ]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/tabular/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file."""
    if fs:
        with fs.open(file) as f:
            df = pd.read_csv(f, **self._pandas_config)
    else:
        df = pd.read_csv(file, **self._pandas_config)

    text_list = df.apply(
        lambda row: (self._col_joiner).join(row.astype(str).tolist()), axis=1
    ).tolist()

    if self._concat_rows:
        return [
            Document(
                text=(self._row_joiner).join(text_list), metadata=extra_info or {}
            )
        ]
    else:
        return [
            Document(text=text, metadata=extra_info or {}) for text in text_list
        ]

```
  
---|---  
##  PandasExcelReader #
Bases: `BaseReader`
Custom Excel parser that includes header names in each row.
Parses Excel files using Pandas' `read_excel` function, but formats each row to include the header name, for example: "name: joao, position: analyst". The first row (header) is not included in the generated documents.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`concat_rows` |  `bool` |  Determines whether to concatenate all rows into one document. If set to False, one Document is created for each row. Defaults to True. |  `True`  
`sheet_name` |  `str | int | None` |  Defaults to None, meaning all sheets. Alternatively, pass a string or an integer to specify the sheet to be read. |  `None`  
`field_separator` |  `str` |  Character or string to separate each field. Default: ", ". |  `', '`  
`key_value_separator` |  `str` |  Character or string to separate the key from the value. Default: ": ". |  `': '`  
`pandas_config` |  `dict` |  Options for the `pandas.read_excel` function call. Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html for more details. Defaults to an empty dictionary. |  `{}`  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/tabular/base.py`

| ```
class PandasExcelReader(BaseReader):
    """
    Custom Excel parser that includes header names in each row.

    Parses Excel files using Pandas' `read_excel` function, but formats
    each row to include the header name, for example: "name: joao, position: analyst".
    The first row (header) is not included in the generated documents.

    Args:
        concat_rows (bool): Determines whether to concatenate all rows into one document.
            If set to False, one Document is created for each row.
            Defaults to True.
        sheet_name (str | int | None): Defaults to None, meaning all sheets.
            Alternatively, pass a string or an integer to specify the sheet to be read.
        field_separator (str): Character or string to separate each field. Default: ", ".
        key_value_separator (str): Character or string to separate the key from the value. Default: ": ".
        pandas_config (dict): Options for the `pandas.read_excel` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
            for more details.
            Defaults to an empty dictionary.

    """

    def __init__(
        self,
        *args: Any,
        concat_rows: bool = True,
        sheet_name=None,
        field_separator: str = ", ",
        key_value_separator: str = ": ",
        pandas_config: dict = {},
        **kwargs: Any,
    ) -> None:
        """Initializes the parameters."""
        super().__init__(*args, **kwargs)
        self._concat_rows = concat_rows
        self._sheet_name = sheet_name
        self._field_separator = field_separator
        self._key_value_separator = key_value_separator
        self._pandas_config = pandas_config

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parses the file."""
        openpyxl_spec = importlib.util.find_spec("openpyxl")
        if openpyxl_spec is not None:
            pass
        else:
            raise ImportError(
                "Please install openpyxl to read Excel files. You can install it with 'pip install openpyxl'"
            )

        # A sheet_name of None means all sheets; otherwise, indexing starts at 0
        if fs:
            with fs.open(file) as f:
                dfs = pd.read_excel(f, self._sheet_name, **self._pandas_config)
        else:
            dfs = pd.read_excel(file, self._sheet_name, **self._pandas_config)

        documents = []

        # Handle the case where only a single DataFrame is returned
        if isinstance(dfs, pd.DataFrame):
            df = dfs.fillna("")
            # Get the headers/column names
            headers = df.columns.tolist()

            # Convert the DataFrame into a list of rows formatted with header names
            text_list = []

            # Start from index 0 to include all data rows
            # The header is already in 'headers', not in the data rows
            for _, row in df.iterrows():
                # Format each row as "header1: value1, header2: value2, ..."
                formatted_row = self._field_separator.join(
                    [
                        f"{header}{self._key_value_separator}{row[header]!s}"
                        for header in headers
                    ]
                )
                text_list.append(formatted_row)

            if self._concat_rows:
                documents.append(
                    Document(text="\n".join(text_list), metadata=extra_info or {})
                )
            else:
                documents.extend(
                    [
                        Document(text=text, metadata=extra_info or {})
                        for text in text_list
                    ]
                )
        else:
            # Handle multiple sheets
            for df in dfs.values():
                df = df.fillna("")
                headers = df.columns.tolist()

                text_list = []
                for _, row in df.iterrows():
                    formatted_row = self._field_separator.join(
                        [
                            f"{header}{self._key_value_separator}{row[header]!s}"
                            for header in headers
                        ]
                    )
                    text_list.append(formatted_row)

                if self._concat_rows:
                    documents.append(
                        Document(text="\n".join(text_list), metadata=extra_info or {})
                    )
                else:
                    documents.extend(
                        [
                            Document(text=text, metadata=extra_info or {})
                            for text in text_list
                        ]
                    )

        return documents

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parses the file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/tabular/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parses the file."""
    openpyxl_spec = importlib.util.find_spec("openpyxl")
    if openpyxl_spec is not None:
        pass
    else:
        raise ImportError(
            "Please install openpyxl to read Excel files. You can install it with 'pip install openpyxl'"
        )

    # A sheet_name of None means all sheets; otherwise, indexing starts at 0
    if fs:
        with fs.open(file) as f:
            dfs = pd.read_excel(f, self._sheet_name, **self._pandas_config)
    else:
        dfs = pd.read_excel(file, self._sheet_name, **self._pandas_config)

    documents = []

    # Handle the case where only a single DataFrame is returned
    if isinstance(dfs, pd.DataFrame):
        df = dfs.fillna("")
        # Get the headers/column names
        headers = df.columns.tolist()

        # Convert the DataFrame into a list of rows formatted with header names
        text_list = []

        # Start from index 0 to include all data rows
        # The header is already in 'headers', not in the data rows
        for _, row in df.iterrows():
            # Format each row as "header1: value1, header2: value2, ..."
            formatted_row = self._field_separator.join(
                [
                    f"{header}{self._key_value_separator}{row[header]!s}"
                    for header in headers
                ]
            )
            text_list.append(formatted_row)

        if self._concat_rows:
            documents.append(
                Document(text="\n".join(text_list), metadata=extra_info or {})
            )
        else:
            documents.extend(
                [
                    Document(text=text, metadata=extra_info or {})
                    for text in text_list
                ]
            )
    else:
        # Handle multiple sheets
        for df in dfs.values():
            df = df.fillna("")
            headers = df.columns.tolist()

            text_list = []
            for _, row in df.iterrows():
                formatted_row = self._field_separator.join(
                    [
                        f"{header}{self._key_value_separator}{row[header]!s}"
                        for header in headers
                    ]
                )
                text_list.append(formatted_row)

            if self._concat_rows:
                documents.append(
                    Document(text="\n".join(text_list), metadata=extra_info or {})
                )
            else:
                documents.extend(
                    [
                        Document(text=text, metadata=extra_info or {})
                        for text in text_list
                    ]
                )

    return documents

```
  
---|---  
##  PptxReader #
Bases: `BaseReader`
Powerpoint parser.
Extract text, caption images, and specify slides.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/slides/base.py`

| ```
class PptxReader(BaseReader):
    """
    Powerpoint parser.

    Extract text, caption images, and specify slides.

    """

    def __init__(self) -> None:
        """Init parser."""
        try:
            import torch  # noqa
            from PIL import Image  # noqa
            from pptx import Presentation  # noqa
            from transformers import (
                AutoTokenizer,
                VisionEncoderDecoderModel,
                ViTFeatureExtractor,
            )
        except ImportError:
            raise ImportError(
                "Please install extra dependencies that are required for "
                "the PptxReader: "
                "`pip install torch 'transformers<4.50' python-pptx Pillow`"
            )

        model = VisionEncoderDecoderModel.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        )
        feature_extractor = ViTFeatureExtractor.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        )

        self.parser_config = {
            "feature_extractor": feature_extractor,
            "model": model,
            "tokenizer": tokenizer,
        }

    def caption_image(self, tmp_image_file: str) -> str:
        """Generate text caption of image."""
        from PIL import Image

        model = self.parser_config["model"]
        feature_extractor = self.parser_config["feature_extractor"]
        tokenizer = self.parser_config["tokenizer"]

        device = infer_torch_device()
        model.to(device)

        max_length = 16
        num_beams = 4
        gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

        i_image = Image.open(tmp_image_file)
        if i_image.mode != "RGB":
            i_image = i_image.convert(mode="RGB")

        pixel_values = feature_extractor(
            images=[i_image], return_tensors="pt"
        ).pixel_values
        pixel_values = pixel_values.to(device)

        output_ids = model.generate(pixel_values, **gen_kwargs)

        preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        return preds[0].strip()

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file."""
        from pptx import Presentation

        if fs:
            with fs.open(str(file)) as f:
                presentation = Presentation(io.BytesIO(f.read()))
        else:
            presentation = Presentation(file)
        result = ""
        for i, slide in enumerate(presentation.slides):
            result += f"\n\nSlide #{i}: \n"
            for shape in slide.shapes:
                if hasattr(shape, "image"):
                    image = shape.image
                    # get image "file" contents
                    image_bytes = image.blob
                    # temporarily save the image to feed into model
                    f = tempfile.NamedTemporaryFile("wb", delete=False)
                    try:
                        f.write(image_bytes)
                        f.close()
                        result += f"\n Image: {self.caption_image(f.name)}\n\n"
                    finally:
                        os.unlink(f.name)

                if hasattr(shape, "text"):
                    result += f"{shape.text}\n"

        return [Document(text=result, metadata=extra_info or {})]

```
  
---|---  
###  caption_image #
```
caption_image(tmp_image_file: str) -> str

```

Generate text caption of image.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/slides/base.py`

| ```
def caption_image(self, tmp_image_file: str) -> str:
    """Generate text caption of image."""
    from PIL import Image

    model = self.parser_config["model"]
    feature_extractor = self.parser_config["feature_extractor"]
    tokenizer = self.parser_config["tokenizer"]

    device = infer_torch_device()
    model.to(device)

    max_length = 16
    num_beams = 4
    gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

    i_image = Image.open(tmp_image_file)
    if i_image.mode != "RGB":
        i_image = i_image.convert(mode="RGB")

    pixel_values = feature_extractor(
        images=[i_image], return_tensors="pt"
    ).pixel_values
    pixel_values = pixel_values.to(device)

    output_ids = model.generate(pixel_values, **gen_kwargs)

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return preds[0].strip()

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/slides/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file."""
    from pptx import Presentation

    if fs:
        with fs.open(str(file)) as f:
            presentation = Presentation(io.BytesIO(f.read()))
    else:
        presentation = Presentation(file)
    result = ""
    for i, slide in enumerate(presentation.slides):
        result += f"\n\nSlide #{i}: \n"
        for shape in slide.shapes:
            if hasattr(shape, "image"):
                image = shape.image
                # get image "file" contents
                image_bytes = image.blob
                # temporarily save the image to feed into model
                f = tempfile.NamedTemporaryFile("wb", delete=False)
                try:
                    f.write(image_bytes)
                    f.close()
                    result += f"\n Image: {self.caption_image(f.name)}\n\n"
                finally:
                    os.unlink(f.name)

            if hasattr(shape, "text"):
                result += f"{shape.text}\n"

    return [Document(text=result, metadata=extra_info or {})]

```
  
---|---  
##  PyMuPDFReader #
Bases: `BaseReader`
Read PDF files using PyMuPDF library.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/pymu_pdf/base.py`

| ```
class PyMuPDFReader(BaseReader):
    """Read PDF files using PyMuPDF library."""

    def load_data(
        self,
        file_path: Union[Path, str],
        metadata: bool = True,
        extra_info: Optional[Dict] = None,
    ) -> List[Document]:
        """Loads list of documents from PDF file and also accepts extra information in dict format."""
        return self.load(file_path, metadata=metadata, extra_info=extra_info)

    def load(
        self,
        file_path: Union[Path, str],
        metadata: bool = True,
        extra_info: Optional[Dict] = None,
    ) -> List[Document]:
        """
        Loads list of documents from PDF file and also accepts extra information in dict format.

        Args:
            file_path (Union[Path, str]): file path of PDF file (accepts string or Path).
            metadata (bool, optional): if metadata to be included or not. Defaults to True.
            extra_info (Optional[Dict], optional): extra information related to each document in dict format. Defaults to None.

        Raises:
            TypeError: if extra_info is not a dictionary.
            TypeError: if file_path is not a string or Path.

        Returns:
            List[Document]: list of documents.

        """
        import fitz

        # check if file_path is a string or Path
        if not isinstance(file_path, str) and not isinstance(file_path, Path):
            raise TypeError("file_path must be a string or Path.")

        # open PDF file
        doc = fitz.open(file_path)

        # if extra_info is not None, check if it is a dictionary
        if extra_info:
            if not isinstance(extra_info, dict):
                raise TypeError("extra_info must be a dictionary.")

        # if metadata is True, add metadata to each document
        if metadata:
            if not extra_info:
                extra_info = {}
            extra_info["total_pages"] = len(doc)
            extra_info["file_path"] = str(file_path)

            # return list of documents
            return [
                Document(
                    text=page.get_text().encode("utf-8"),
                    extra_info=dict(
                        extra_info,
                        **{
                            "source": f"{page.number + 1}",
                        },
                    ),
                )
                for page in doc
            ]

        else:
            return [
                Document(
                    text=page.get_text().encode("utf-8"), extra_info=extra_info or {}
                )
                for page in doc
            ]

```
  
---|---  
###  load_data #
```
load_data(file_path: Union[Path, str], metadata: bool = True, extra_info: Optional[Dict] = None) -> List[Document]

```

Loads list of documents from PDF file and also accepts extra information in dict format.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/pymu_pdf/base.py`

| ```
def load_data(
    self,
    file_path: Union[Path, str],
    metadata: bool = True,
    extra_info: Optional[Dict] = None,
) -> List[Document]:
    """Loads list of documents from PDF file and also accepts extra information in dict format."""
    return self.load(file_path, metadata=metadata, extra_info=extra_info)

```
  
---|---  
###  load #
```
load(file_path: Union[Path, str], metadata: bool = True, extra_info: Optional[Dict] = None) -> List[Document]

```

Loads list of documents from PDF file and also accepts extra information in dict format.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`file_path` |  `Union[Path, str]` |  file path of PDF file (accepts string or Path). |  _required_  
`metadata` |  `bool` |  if metadata to be included or not. Defaults to True. |  `True`  
`extra_info` |  `Optional[Dict]` |  extra information related to each document in dict format. Defaults to None. |  `None`  
Raises:
Type | Description  
---|---  
`TypeError` |  if extra_info is not a dictionary.  
`TypeError` |  if file_path is not a string or Path.  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/pymu_pdf/base.py`

| ```
def load(
    self,
    file_path: Union[Path, str],
    metadata: bool = True,
    extra_info: Optional[Dict] = None,
) -> List[Document]:
    """
    Loads list of documents from PDF file and also accepts extra information in dict format.

    Args:
        file_path (Union[Path, str]): file path of PDF file (accepts string or Path).
        metadata (bool, optional): if metadata to be included or not. Defaults to True.
        extra_info (Optional[Dict], optional): extra information related to each document in dict format. Defaults to None.

    Raises:
        TypeError: if extra_info is not a dictionary.
        TypeError: if file_path is not a string or Path.

    Returns:
        List[Document]: list of documents.

    """
    import fitz

    # check if file_path is a string or Path
    if not isinstance(file_path, str) and not isinstance(file_path, Path):
        raise TypeError("file_path must be a string or Path.")

    # open PDF file
    doc = fitz.open(file_path)

    # if extra_info is not None, check if it is a dictionary
    if extra_info:
        if not isinstance(extra_info, dict):
            raise TypeError("extra_info must be a dictionary.")

    # if metadata is True, add metadata to each document
    if metadata:
        if not extra_info:
            extra_info = {}
        extra_info["total_pages"] = len(doc)
        extra_info["file_path"] = str(file_path)

        # return list of documents
        return [
            Document(
                text=page.get_text().encode("utf-8"),
                extra_info=dict(
                    extra_info,
                    **{
                        "source": f"{page.number + 1}",
                    },
                ),
            )
            for page in doc
        ]

    else:
        return [
            Document(
                text=page.get_text().encode("utf-8"), extra_info=extra_info or {}
            )
            for page in doc
        ]

```
  
---|---  
##  RTFReader #
Bases: `BaseReader`
RTF (Rich Text Format) Reader. Reads rtf file and convert to Document.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/rtf/base.py`

| ```
class RTFReader(BaseReader):
    """RTF (Rich Text Format) Reader. Reads rtf file and convert to Document."""

    def load_data(
        self,
        input_file: Union[Path, str],
        extra_info: Optional[Dict[str, Any]] = None,
        **load_kwargs: Any,
    ) -> List[Document]:
        """
        Load data from RTF file.

        Args:
            input_file (Path | str): Path for the RTF file.
            extra_info (Dict[str, Any]): Path for the RTF file.

        Returns:
            List[Document]: List of documents.

        """
        try:
            from striprtf.striprtf import rtf_to_text
        except ImportError:
            raise ImportError("striprtf is required to read RTF files.")

        with open(str(input_file)) as f:
            text = rtf_to_text(f.read())
            return [Document(text=text.strip(), metadata=extra_info or {})]

```
  
---|---  
###  load_data #
```
load_data(input_file: Union[Path, str], extra_info: Optional[Dict[str, Any]] = None, **load_kwargs: Any) -> List[Document]

```

Load data from RTF file.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`input_file` |  `Path | str` |  Path for the RTF file. |  _required_  
`extra_info` |  `Dict[str, Any]` |  Path for the RTF file. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/rtf/base.py`

| ```
def load_data(
    self,
    input_file: Union[Path, str],
    extra_info: Optional[Dict[str, Any]] = None,
    **load_kwargs: Any,
) -> List[Document]:
    """
    Load data from RTF file.

    Args:
        input_file (Path | str): Path for the RTF file.
        extra_info (Dict[str, Any]): Path for the RTF file.

    Returns:
        List[Document]: List of documents.

    """
    try:
        from striprtf.striprtf import rtf_to_text
    except ImportError:
        raise ImportError("striprtf is required to read RTF files.")

    with open(str(input_file)) as f:
        text = rtf_to_text(f.read())
        return [Document(text=text.strip(), metadata=extra_info or {})]

```
  
---|---  
##  UnstructuredReader #
Bases: `BaseReader`
General unstructured text reader for a variety of files.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/unstructured/base.py`

| ```
class UnstructuredReader(BaseReader):
    """General unstructured text reader for a variety of files."""

    def __init__(
        self,
        *args: Any,
        api_key: str = None,
        url: str = None,
        allowed_metadata_types: Optional[Tuple] = None,
        excluded_metadata_keys: Optional[Set] = None,
    ) -> None:
        """
        Initialize UnstructuredReader.

        Args:
            *args (Any): Additional arguments passed to the BaseReader.
            api_key (str, optional): API key for accessing the Unstructured.io API. If provided, the reader will use the API for parsing files. Defaults to None.
            url (str, optional): URL for the Unstructured.io API. If not provided and an api_key is given, defaults to "http://localhost:8000". Ignored if api_key is not provided. Defaults to None.
            allowed_metadata_types (Optional[Tuple], optional): Tuple of types that are allowed in the metadata. Defaults to (str, int, float, type(None)).
            excluded_metadata_keys (Optional[Set], optional): Set of metadata keys to exclude from the final document. Defaults to {"orig_elements"}.

        Attributes:
            api_key (str or None): Stores the API key.
            use_api (bool): Indicates whether to use the API for parsing files, based on the presence of the api_key.
            url (str or None): URL for the Unstructured.io API if using the API.
            allowed_metadata_types (Tuple): Tuple of types that are allowed in the metadata.
            excluded_metadata_keys (Set): Set of metadata keys to exclude from the final document.

        """
        super().__init__(*args)  # not passing kwargs to parent bc it cannot accept it

        if Element is None:
            raise ImportError(
                "Unstructured is not installed. Please install it using 'pip install -U unstructured'."
            )

        self.api_key = api_key
        self.use_api = bool(api_key)
        self.url = url or "http://localhost:8000" if self.use_api else None
        self.allowed_metadata_types = allowed_metadata_types or (
            str,
            int,
            float,
            type(None),
        )
        self.excluded_metadata_keys = excluded_metadata_keys or {"orig_elements"}

    @classmethod
    def from_api(cls, api_key: str, url: str = None):
        """Set the server url and api key."""
        return cls(api_key, url)

    def load_data(
        self,
        file: Optional[Path] = None,
        unstructured_kwargs: Optional[Dict] = None,
        document_kwargs: Optional[Dict] = None,
        extra_info: Optional[Dict] = None,
        split_documents: Optional[bool] = False,
        excluded_metadata_keys: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        Load data using Unstructured.io.

        Depending on the configuration, if url is set or use_api is True,
        it'll parse the file using an API call, otherwise it parses it locally.
        extra_info is extended by the returned metadata if split_documents is True.

        Args:
            file (Optional[Path]): Path to the file to be loaded.
            unstructured_kwargs (Optional[Dict]): Additional arguments for unstructured partitioning.
            document_kwargs (Optional[Dict]): Additional arguments for document creation.
            extra_info (Optional[Dict]): Extra information to add to the document metadata.
            split_documents (Optional[bool]): Whether to split the documents.
            excluded_metadata_keys (Optional[List[str]]): Keys to exclude from the metadata.

        Returns:
            List[Document]: List of parsed documents.

        """
        unstructured_kwargs = unstructured_kwargs.copy() if unstructured_kwargs else {}

        if (
            unstructured_kwargs.get("file") is not None
            and unstructured_kwargs.get("metadata_filename") is None
        ):
            raise ValueError(
                "Please provide a 'metadata_filename' as part of the 'unstructured_kwargs' when loading a file stream."
            )

        elements: List[Element] = self._partition_elements(unstructured_kwargs, file)

        return self._create_documents(
            elements,
            document_kwargs,
            extra_info,
            split_documents,
            excluded_metadata_keys,
        )

    def _partition_elements(
        self, unstructured_kwargs: Dict, file: Optional[Path] = None
    ) -> List[Element]:
        """
        Partition the elements from the file or via API.

        Args:
            file (Optional[Path]): Path to the file to be loaded.
            unstructured_kwargs (Dict): Additional arguments for unstructured partitioning.

        Returns:
            List[Element]: List of partitioned elements.

        """
        if file:
            unstructured_kwargs["filename"] = str(file)

        if self.use_api:
            from unstructured.partition.api import partition_via_api

            return partition_via_api(
                api_key=self.api_key,
                api_url=self.url + "/general/v0/general",
                **unstructured_kwargs,
            )
        else:
            from unstructured.partition.auto import partition

            return partition(**unstructured_kwargs)

    def _create_documents(
        self,
        elements: List[Element],
        document_kwargs: Optional[Dict],
        extra_info: Optional[Dict],
        split_documents: Optional[bool],
        excluded_metadata_keys: Optional[List[str]],
    ) -> List[Document]:
        """
        Create documents from partitioned elements.

        Args:
            elements (List): List of partitioned elements.
            document_kwargs (Optional[Dict]): Additional arguments for document creation.
            extra_info (Optional[Dict]): Extra information to add to the document metadata.
            split_documents (Optional[bool]): Whether to split the documents.
            excluded_metadata_keys (Optional[List[str]]): Keys to exclude from the metadata.

        Returns:
            List[Document]: List of parsed documents.

        """
        doc_kwargs = document_kwargs or {}
        doc_extras = extra_info or {}
        excluded_keys = set(excluded_metadata_keys or self.excluded_metadata_keys)
        docs: List[Document] = []

        def _merge_metadata(
            element: Element, sequence_number: Optional[int] = None
        ) -> Dict[str, Any]:
            candidate_metadata = {**element.metadata.to_dict(), **doc_extras}
            metadata = {
                key: (
                    value
                    if isinstance(value, self.allowed_metadata_types)
                    else json.dumps(value)
                )
                for key, value in candidate_metadata.items()
                if key not in excluded_keys
            }
            if sequence_number is not None:
                metadata["sequence_number"] = sequence_number
            return metadata

        if len(elements) == 0:
            return []

        text_chunks = [" ".join(str(el).split()) for el in elements]
        metadata = _merge_metadata(elements[0])
        filename = metadata.get("file_path", None) or metadata["filename"]
        source = Document(
            text="\n\n".join(text_chunks),
            extra_info=metadata,
            doc_id=filename,
            id_=filename,
            **doc_kwargs,
        )

        if split_documents:
            docs = []
            for sequence_number, element in enumerate(elements):
                hash_id = element.id_to_hash(sequence_number)
                node = TextNode(
                    text=element.text,
                    metadata=_merge_metadata(element, sequence_number),
                    doc_id=hash_id,
                    id_=hash_id,
                    **doc_kwargs,
                )
                node.relationships[NodeRelationship.SOURCE] = (
                    source.as_related_node_info()
                )
                docs.append(node)
        else:
            docs = [source]

        return docs

```
  
---|---  
###  from_api `classmethod` #
```
from_api(api_key: str, url: str = None)

```

Set the server url and api key.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/unstructured/base.py`

| ```
@classmethod
def from_api(cls, api_key: str, url: str = None):
    """Set the server url and api key."""
    return cls(api_key, url)

```
  
---|---  
###  load_data #
```
load_data(file: Optional[Path] = None, unstructured_kwargs: Optional[Dict] = None, document_kwargs: Optional[Dict] = None, extra_info: Optional[Dict] = None, split_documents: Optional[bool] = False, excluded_metadata_keys: Optional[List[str]] = None) -> List[Document]

```

Load data using Unstructured.io.
Depending on the configuration, if url is set or use_api is True, it'll parse the file using an API call, otherwise it parses it locally. extra_info is extended by the returned metadata if split_documents is True.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`file` |  `Optional[Path]` |  Path to the file to be loaded. |  `None`  
`unstructured_kwargs` |  `Optional[Dict]` |  Additional arguments for unstructured partitioning. |  `None`  
`document_kwargs` |  `Optional[Dict]` |  Additional arguments for document creation. |  `None`  
`extra_info` |  `Optional[Dict]` |  Extra information to add to the document metadata. |  `None`  
`split_documents` |  `Optional[bool]` |  Whether to split the documents. |  `False`  
`excluded_metadata_keys` |  `Optional[List[str]]` |  Keys to exclude from the metadata. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of parsed documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/unstructured/base.py`

| ```
def load_data(
    self,
    file: Optional[Path] = None,
    unstructured_kwargs: Optional[Dict] = None,
    document_kwargs: Optional[Dict] = None,
    extra_info: Optional[Dict] = None,
    split_documents: Optional[bool] = False,
    excluded_metadata_keys: Optional[List[str]] = None,
) -> List[Document]:
    """
    Load data using Unstructured.io.

    Depending on the configuration, if url is set or use_api is True,
    it'll parse the file using an API call, otherwise it parses it locally.
    extra_info is extended by the returned metadata if split_documents is True.

    Args:
        file (Optional[Path]): Path to the file to be loaded.
        unstructured_kwargs (Optional[Dict]): Additional arguments for unstructured partitioning.
        document_kwargs (Optional[Dict]): Additional arguments for document creation.
        extra_info (Optional[Dict]): Extra information to add to the document metadata.
        split_documents (Optional[bool]): Whether to split the documents.
        excluded_metadata_keys (Optional[List[str]]): Keys to exclude from the metadata.

    Returns:
        List[Document]: List of parsed documents.

    """
    unstructured_kwargs = unstructured_kwargs.copy() if unstructured_kwargs else {}

    if (
        unstructured_kwargs.get("file") is not None
        and unstructured_kwargs.get("metadata_filename") is None
    ):
        raise ValueError(
            "Please provide a 'metadata_filename' as part of the 'unstructured_kwargs' when loading a file stream."
        )

    elements: List[Element] = self._partition_elements(unstructured_kwargs, file)

    return self._create_documents(
        elements,
        document_kwargs,
        extra_info,
        split_documents,
        excluded_metadata_keys,
    )

```
  
---|---  
##  VideoAudioReader #
Bases: `BaseReader`
Video audio parser.
Extract text from transcript of video/audio files.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/video_audio/base.py`

| ```
class VideoAudioReader(BaseReader):
    """
    Video audio parser.

    Extract text from transcript of video/audio files.

    """

    def __init__(self, *args: Any, model_version: str = "base", **kwargs: Any) -> None:
        """Init parser."""
        super().__init__(*args, **kwargs)
        self._model_version = model_version

        try:
            import whisper
        except ImportError:
            raise ImportError(
                "Please install OpenAI whisper model "
                "'pip install git+https://github.com/openai/whisper.git' "
                "to use the model"
            )

        model = whisper.load_model(self._model_version)

        self.parser_config = {"model": model}

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """Parse file."""
        import whisper

        if file.name.endswith("mp4"):
            try:
                from pydub import AudioSegment
            except ImportError:
                raise ImportError("Please install pydub 'pip install pydub' ")
            if fs:
                with fs.open(file, "rb") as f:
                    video = AudioSegment.from_file(f, format="mp4")
            else:
                # open file
                video = AudioSegment.from_file(file, format="mp4")

            # Extract audio from video
            audio = video.split_to_mono()[0]

            file_str = str(file)[:-4] + ".mp3"
            # export file
            audio.export(file_str, format="mp3")

        model = cast(whisper.Whisper, self.parser_config["model"])
        result = model.transcribe(str(file))

        transcript = result["text"]

        return [Document(text=transcript, metadata=extra_info or {})]

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None, fs: Optional[AbstractFileSystem] = None) -> List[Document]

```

Parse file.
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/video_audio/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
    fs: Optional[AbstractFileSystem] = None,
) -> List[Document]:
    """Parse file."""
    import whisper

    if file.name.endswith("mp4"):
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("Please install pydub 'pip install pydub' ")
        if fs:
            with fs.open(file, "rb") as f:
                video = AudioSegment.from_file(f, format="mp4")
        else:
            # open file
            video = AudioSegment.from_file(file, format="mp4")

        # Extract audio from video
        audio = video.split_to_mono()[0]

        file_str = str(file)[:-4] + ".mp3"
        # export file
        audio.export(file_str, format="mp3")

    model = cast(whisper.Whisper, self.parser_config["model"])
    result = model.transcribe(str(file))

    transcript = result["text"]

    return [Document(text=transcript, metadata=extra_info or {})]

```
  
---|---  
##  XMLReader #
Bases: `BaseReader`
XML reader.
Reads XML documents with options to help suss out relationships between nodes.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`tree_level_split` |  `int` |  From which level in the xml tree we split documents, |  `0`  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/xml/base.py`

| ```
class XMLReader(BaseReader):
    """
    XML reader.

    Reads XML documents with options to help suss out relationships between nodes.

    Args:
        tree_level_split (int): From which level in the xml tree we split documents,
        the default level is the root which is level 0

    """

    def __init__(self, tree_level_split: Optional[int] = 0) -> None:
        """Initialize with arguments."""
        super().__init__()
        self.tree_level_split = tree_level_split

    def _parse_xmlelt_to_document(
        self, root: _XmlET.Element, extra_info: Optional[Dict] = None
    ) -> List[Document]:
        """
        Parse the xml object into a list of Documents.

        Args:
            root: The XML Element to be converted.
            extra_info (Optional[Dict]): Additional information. Default is None.

        Returns:
            Document: The documents.

        """
        nodes = _get_leaf_nodes_up_to_level(root, self.tree_level_split)
        documents = []
        for node in nodes:
            content = ET.tostring(node, encoding="utf8").decode("utf-8")
            content = re.sub(r"^<\?xml.*", "", content)
            content = content.strip()
            documents.append(Document(text=content, extra_info=extra_info or {}))

        return documents

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict] = None,
    ) -> List[Document]:
        """
        Load data from the input file.

        Args:
            file (Path): Path to the input file.
            extra_info (Optional[Dict]): Additional information. Default is None.

        Returns:
            List[Document]: List of documents.

        """
        if not isinstance(file, Path):
            file = Path(file)

        tree = ET.parse(file)
        return self._parse_xmlelt_to_document(tree.getroot(), extra_info)

```
  
---|---  
###  load_data #
```
load_data(file: Path, extra_info: Optional[Dict] = None) -> List[Document]

```

Load data from the input file.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`file` |  `Path` |  Path to the input file. |  _required_  
`extra_info` |  `Optional[Dict]` |  Additional information. Default is None. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-file/llama_index/readers/file/xml/base.py`

| ```
def load_data(
    self,
    file: Path,
    extra_info: Optional[Dict] = None,
) -> List[Document]:
    """
    Load data from the input file.

    Args:
        file (Path): Path to the input file.
        extra_info (Optional[Dict]): Additional information. Default is None.

    Returns:
        List[Document]: List of documents.

    """
    if not isinstance(file, Path):
        file = Path(file)

    tree = ET.parse(file)
    return self._parse_xmlelt_to_document(tree.getroot(), extra_info)

```
  
---|---
