# Youtube transcript
##  YoutubeTranscriptReader #
Bases: `BasePydanticReader`
Youtube Transcript reader.
Source code in `llama-index-integrations/readers/llama-index-readers-youtube-transcript/llama_index/readers/youtube_transcript/base.py`

| ```
class YoutubeTranscriptReader(BasePydanticReader):
    """Youtube Transcript reader."""

    is_remote: bool = True

    @classmethod
    def class_name(cls) -> str:
        """Get the name identifier of the class."""
        return "YoutubeTranscriptReader"

    def load_data(
        self,
        ytlinks: List[str],
        languages: Optional[List[str]] = ["en"],
        **load_kwargs: Any,
    ) -> List[Document]:
        """
        Load data from the input directory.

        Args:
            pages (List[str]): List of youtube links \
                for which transcripts are to be read.

        """
        results = []
        for link in ytlinks:
            video_id = self._extract_video_id(link)
            if not video_id:
                raise ValueError(
                    f"Supplied url {link} is not a supported youtube URL."
                    "Supported formats include:"
                    "  youtube.com/watch?v=\\{video_id\\} "
                    "(with or without 'www.')\n"
                    "  youtube.com/embed?v=\\{video_id\\} "
                    "(with or without 'www.')\n"
                    "  youtu.be/{video_id\\} (never includes www subdomain)"
                )
            transcript_chunks = YouTubeTranscriptApi.get_transcript(
                video_id, languages=languages
            )
            chunk_text = [chunk["text"] for chunk in transcript_chunks]
            transcript = "\n".join(chunk_text)
            results.append(
                Document(
                    text=transcript, id_=video_id, extra_info={"video_id": video_id}
                )
            )
        return results

    @staticmethod
    def _extract_video_id(yt_link) -> Optional[str]:
        for pattern in YOUTUBE_URL_PATTERNS:
            match = re.search(pattern, yt_link)
            if match:
                return match.group(1)

        # return None if no match is found
        return None

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get the name identifier of the class.
Source code in `llama-index-integrations/readers/llama-index-readers-youtube-transcript/llama_index/readers/youtube_transcript/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get the name identifier of the class."""
    return "YoutubeTranscriptReader"

```
  
---|---  
###  load_data #
```
load_data(ytlinks: List[str], languages: Optional[List[str]] = ['en'], **load_kwargs: Any) -> List[Document]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`pages` |  `List[str]` |  List of youtube links for which transcripts are to be read. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-youtube-transcript/llama_index/readers/youtube_transcript/base.py`

| ```
def load_data(
    self,
    ytlinks: List[str],
    languages: Optional[List[str]] = ["en"],
    **load_kwargs: Any,
) -> List[Document]:
    """
    Load data from the input directory.

    Args:
        pages (List[str]): List of youtube links \
            for which transcripts are to be read.

    """
    results = []
    for link in ytlinks:
        video_id = self._extract_video_id(link)
        if not video_id:
            raise ValueError(
                f"Supplied url {link} is not a supported youtube URL."
                "Supported formats include:"
                "  youtube.com/watch?v=\\{video_id\\} "
                "(with or without 'www.')\n"
                "  youtube.com/embed?v=\\{video_id\\} "
                "(with or without 'www.')\n"
                "  youtu.be/{video_id\\} (never includes www subdomain)"
            )
        transcript_chunks = YouTubeTranscriptApi.get_transcript(
            video_id, languages=languages
        )
        chunk_text = [chunk["text"] for chunk in transcript_chunks]
        transcript = "\n".join(chunk_text)
        results.append(
            Document(
                text=transcript, id_=video_id, extra_info={"video_id": video_id}
            )
        )
    return results

```
  
---|---
