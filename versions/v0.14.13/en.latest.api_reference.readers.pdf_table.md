# Pdf table
##  PDFTableReader #
Bases: `BaseReader`
PDF Table Reader. Reads table from PDF.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`row_separator` |  `str` |  Row separator used to join rows of a DataFrame. |  `'\n'`  
`col_separator` |  `str` |  Col separator used to join columns of a DataFrame. |  `', '`  
Source code in `llama-index-integrations/readers/llama-index-readers-pdf-table/llama_index/readers/pdf_table/base.py`

| ```
class PDFTableReader(BaseReader):
    """
    PDF Table Reader. Reads table from PDF.

    Args:
        row_separator (str): Row separator used to join rows of a DataFrame.
        col_separator (str): Col separator used to join columns of a DataFrame.

    """

    def __init__(
        self,
        *args: Any,
        row_separator: str = "\n",
        col_separator: str = ", ",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._row_separator = row_separator
        self._col_separator = col_separator

    def load_data(
        self, file: Path, pages: str = "1", extra_info: Optional[Dict] = None
    ) -> List[Document]:
        """
        Load data and extract table from PDF file.

        Args:
            file (Path): Path for the PDF file.
            pages (str): Pages to read tables from.
            extra_info (Optional[Dict]): Extra information.

        Returns:
            List[Document]: List of documents.

        """
        import camelot

        results = []
        tables = camelot.read_pdf(filepath=str(file), pages=pages)

        for table in tables:
            document = self._dataframe_to_document(df=table.df, extra_info=extra_info)
            results.append(document)

        return results

    def _dataframe_to_document(
        self, df: pd.DataFrame, extra_info: Optional[Dict] = None
    ) -> Document:
        df_list = df.apply(
            lambda row: (self._col_separator).join(row.astype(str).tolist()), axis=1
        ).tolist()

        return Document(
            text=self._row_separator.join(df_list), extra_info=extra_info or {}
        )

```
  
---|---  
###  load_data #
```
load_data(file: Path, pages: str = '1', extra_info: Optional[Dict] = None) -> List[Document]

```

Load data and extract table from PDF file.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`file` |  `Path` |  Path for the PDF file. |  _required_  
`pages` |  `str` |  Pages to read tables from. |  `'1'`  
`extra_info` |  `Optional[Dict]` |  Extra information. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-pdf-table/llama_index/readers/pdf_table/base.py`

| ```
def load_data(
    self, file: Path, pages: str = "1", extra_info: Optional[Dict] = None
) -> List[Document]:
    """
    Load data and extract table from PDF file.

    Args:
        file (Path): Path for the PDF file.
        pages (str): Pages to read tables from.
        extra_info (Optional[Dict]): Extra information.

    Returns:
        List[Document]: List of documents.

    """
    import camelot

    results = []
    tables = camelot.read_pdf(filepath=str(file), pages=pages)

    for table in tables:
        document = self._dataframe_to_document(df=table.df, extra_info=extra_info)
        results.append(document)

    return results

```
  
---|---
