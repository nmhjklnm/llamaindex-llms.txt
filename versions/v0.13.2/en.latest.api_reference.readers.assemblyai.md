# Assemblyai
##  AssemblyAIAudioTranscriptReader #
Bases: `BaseReader`
Reader for AssemblyAI audio transcripts.
It uses the AssemblyAI API to transcribe audio files and loads the transcribed text into one or more Documents, depending on the specified format.
To use, you should have the `assemblyai` python package installed, and the environment variable `ASSEMBLYAI_API_KEY` set with your API key. Alternatively, the API key can also be passed as an argument.
Audio files can be specified via an URL or a local file path.
Source code in `llama-index-integrations/readers/llama-index-readers-assemblyai/llama_index/readers/assemblyai/base.py`

| ```
class AssemblyAIAudioTranscriptReader(BaseReader):
    """
    Reader for AssemblyAI audio transcripts.

    It uses the AssemblyAI API to transcribe audio files
    and loads the transcribed text into one or more Documents,
    depending on the specified format.

    To use, you should have the ``assemblyai`` python package installed, and the
    environment variable ``ASSEMBLYAI_API_KEY`` set with your API key.
    Alternatively, the API key can also be passed as an argument.

    Audio files can be specified via an URL or a local file path.
    """

    def __init__(
        self,
        file_path: str,
        *,
        transcript_format: TranscriptFormat = TranscriptFormat.TEXT,
        config: Optional[assemblyai.TranscriptionConfig] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initializes the AssemblyAI AudioTranscriptReader.

        Args:
            file_path: An URL or a local file path.
            transcript_format: Transcript format to use.
                See class ``TranscriptFormat`` for more info.
            config: Transcription options and features. If ``None`` is given,
                the Transcriber's default configuration will be used.
            api_key: AssemblyAI API key.

        """
        if api_key is not None:
            assemblyai.settings.api_key = api_key

        self.file_path = file_path
        self.transcript_format = transcript_format

        # Instantiating the Transcriber will raise a ValueError if no API key is set.
        self.transcriber = assemblyai.Transcriber(config=config)

    def load_data(self) -> List[Document]:
        """
        Transcribes the audio file and loads the transcript into documents.

        It uses the AssemblyAI API to transcribe the audio file and blocks until
        the transcription is finished.
        """
        transcript = self.transcriber.transcribe(self.file_path)

        if transcript.error:
            raise ValueError(f"Could not transcribe file: {transcript.error}")

        if self.transcript_format == TranscriptFormat.TEXT:
            return [Document(text=transcript.text, metadata=transcript.json_response)]
        elif self.transcript_format == TranscriptFormat.SENTENCES:
            sentences = transcript.get_sentences()
            return [
                Document(text=s.text, metadata=s.dict(exclude={"text"}))
                for s in sentences
            ]
        elif self.transcript_format == TranscriptFormat.PARAGRAPHS:
            paragraphs = transcript.get_paragraphs()
            return [
                Document(text=p.text, metadata=p.dict(exclude={"text"}))
                for p in paragraphs
            ]
        elif self.transcript_format == TranscriptFormat.SUBTITLES_SRT:
            return [Document(text=transcript.export_subtitles_srt())]
        elif self.transcript_format == TranscriptFormat.SUBTITLES_VTT:
            return [Document(text=transcript.export_subtitles_vtt())]
        else:
            raise ValueError("Unknown transcript format.")

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Transcribes the audio file and loads the transcript into documents.
It uses the AssemblyAI API to transcribe the audio file and blocks until the transcription is finished.
Source code in `llama-index-integrations/readers/llama-index-readers-assemblyai/llama_index/readers/assemblyai/base.py`

| ```
def load_data(self) -> List[Document]:
    """
    Transcribes the audio file and loads the transcript into documents.

    It uses the AssemblyAI API to transcribe the audio file and blocks until
    the transcription is finished.
    """
    transcript = self.transcriber.transcribe(self.file_path)

    if transcript.error:
        raise ValueError(f"Could not transcribe file: {transcript.error}")

    if self.transcript_format == TranscriptFormat.TEXT:
        return [Document(text=transcript.text, metadata=transcript.json_response)]
    elif self.transcript_format == TranscriptFormat.SENTENCES:
        sentences = transcript.get_sentences()
        return [
            Document(text=s.text, metadata=s.dict(exclude={"text"}))
            for s in sentences
        ]
    elif self.transcript_format == TranscriptFormat.PARAGRAPHS:
        paragraphs = transcript.get_paragraphs()
        return [
            Document(text=p.text, metadata=p.dict(exclude={"text"}))
            for p in paragraphs
        ]
    elif self.transcript_format == TranscriptFormat.SUBTITLES_SRT:
        return [Document(text=transcript.export_subtitles_srt())]
    elif self.transcript_format == TranscriptFormat.SUBTITLES_VTT:
        return [Document(text=transcript.export_subtitles_vtt())]
    else:
        raise ValueError("Unknown transcript format.")

```
  
---|---
