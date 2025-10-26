# Resume screener
##  ResumeScreenerPack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-resume-screener/llama_index/packs/resume_screener/base.py`

| ```
class ResumeScreenerPack(BaseLlamaPack):
    def __init__(
        self, job_description: str, criteria: List[str], llm: Optional[LLM] = None
    ) -> None:
        self.reader = PDFReader()
        llm = llm or OpenAI(model="gpt-4")
        Settings.llm = llm
        self.synthesizer = TreeSummarize(output_cls=ResumeScreenerDecision)
        criteria_str = _format_criteria_str(criteria)
        self.query = QUERY_TEMPLATE.format(
            job_description=job_description, criteria_str=criteria_str
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {"reader": self.reader, "synthesizer": self.synthesizer}

    def run(self, resume_path: str, *args: Any, **kwargs: Any) -> Any:
        """Run pack."""
        docs = self.reader.load_data(Path(resume_path))
        output = self.synthesizer.synthesize(
            query=self.query,
            nodes=[NodeWithScore(node=doc, score=1.0) for doc in docs],
        )
        return output.response

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-resume-screener/llama_index/packs/resume_screener/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {"reader": self.reader, "synthesizer": self.synthesizer}

```
  
---|---  
###  run #
```
run(resume_path: str, *args: Any, **kwargs: Any) -> Any

```

Run pack.
Source code in `llama-index-packs/llama-index-packs-resume-screener/llama_index/packs/resume_screener/base.py`

| ```
def run(self, resume_path: str, *args: Any, **kwargs: Any) -> Any:
    """Run pack."""
    docs = self.reader.load_data(Path(resume_path))
    output = self.synthesizer.synthesize(
        query=self.query,
        nodes=[NodeWithScore(node=doc, score=1.0) for doc in docs],
    )
    return output.response

```
  
---|---
