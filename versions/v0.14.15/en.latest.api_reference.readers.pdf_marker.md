# Pdf marker
##  PDFMarkerReader #
Bases: `BaseReader`
PDF Marker Reader. Reads a pdf to markdown format and tables with layout.
Source code in `llama-index-integrations/readers/llama-index-readers-pdf-marker/llama_index/readers/pdf_marker/base.py`

| ```
class PDFMarkerReader(BaseReader):
    """
    PDF Marker Reader. Reads a pdf to markdown format and tables with layout.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def load_data(
        self,
        file: Path,
        max_pages: int = None,
        langs: List[str] = None,
        batch_multiplier: int = 2,
        start_page: int = None,
        extra_info: Optional[Dict] = None,
    ) -> List[Document]:
        """
        Load data from PDF
        Args:
            file (Path): Path for the PDF file.
            max_pages (int): is the maximum number of pages to process. Omit this to convert the entire document.
            langs (List[str]): List of languages to use for OCR. See supported languages : https://github.com/VikParuchuri/surya/blob/master/surya/languages.py
            batch_multiplier (int): is how much to multiply default batch sizes by if you have extra VRAM. Higher numbers will take more VRAM, but process faster. Set to 2 by default. The default batch sizes will take ~3GB of VRAM.
            start_page (int): Start page for conversion.

        Returns:
            List[Document]: List of documents.

        """
        from marker.convert import convert_single_pdf
        from marker.models import load_all_models

        model_lst = load_all_models()
        full_text, images, out_meta = convert_single_pdf(
            str(file),
            model_lst,
            max_pages=max_pages,
            langs=langs,
            batch_multiplier=batch_multiplier,
            start_page=start_page,
        )

        doc = Document(text=full_text, extra_info=extra_info or {})

        return [doc]

```
  
---|---  
###  load_data #
```
load_data(file: Path, max_pages: int = None, langs: List[str] = None, batch_multiplier: int = 2, start_page: int = None, extra_info: Optional[Dict] = None) -> List[Document]

```

Load data from PDF Args: file (Path): Path for the PDF file. max_pages (int): is the maximum number of pages to process. Omit this to convert the entire document. langs (List[str]): List of languages to use for OCR. See supported languages : https://github.com/VikParuchuri/surya/blob/master/surya/languages.py batch_multiplier (int): is how much to multiply default batch sizes by if you have extra VRAM. Higher numbers will take more VRAM, but process faster. Set to 2 by default. The default batch sizes will take ~3GB of VRAM. start_page (int): Start page for conversion.
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-pdf-marker/llama_index/readers/pdf_marker/base.py`

| ```
def load_data(
    self,
    file: Path,
    max_pages: int = None,
    langs: List[str] = None,
    batch_multiplier: int = 2,
    start_page: int = None,
    extra_info: Optional[Dict] = None,
) -> List[Document]:
    """
    Load data from PDF
    Args:
        file (Path): Path for the PDF file.
        max_pages (int): is the maximum number of pages to process. Omit this to convert the entire document.
        langs (List[str]): List of languages to use for OCR. See supported languages : https://github.com/VikParuchuri/surya/blob/master/surya/languages.py
        batch_multiplier (int): is how much to multiply default batch sizes by if you have extra VRAM. Higher numbers will take more VRAM, but process faster. Set to 2 by default. The default batch sizes will take ~3GB of VRAM.
        start_page (int): Start page for conversion.

    Returns:
        List[Document]: List of documents.

    """
    from marker.convert import convert_single_pdf
    from marker.models import load_all_models

    model_lst = load_all_models()
    full_text, images, out_meta = convert_single_pdf(
        str(file),
        model_lst,
        max_pages=max_pages,
        langs=langs,
        batch_multiplier=batch_multiplier,
        start_page=start_page,
    )

    doc = Document(text=full_text, extra_info=extra_info or {})

    return [doc]

```
  
---|---
