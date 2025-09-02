# Gradio react agent chatbot
##  GradioReActAgentPack #
Bases: `BaseLlamaPack`
Gradio chatbot to chat with a ReActAgent pack.
Source code in `llama-index-packs/llama-index-packs-gradio-react-agent-chatbot/llama_index/packs/gradio_react_agent_chatbot/base.py`

| ```
class GradioReActAgentPack(BaseLlamaPack):
    """Gradio chatbot to chat with a ReActAgent pack."""

    def __init__(
        self,
        tools_list: Optional[List[str]] = list(SUPPORTED_TOOLS.keys()),
        **kwargs: Any,
    ) -> None:
        """Init params."""
        try:
            from ansi2html import Ansi2HTMLConverter
        except ImportError:
            raise ImportError("Please install ansi2html via `pip install ansi2html`")

        tools = []
        for t in tools_list:
            try:
                tools.append(SUPPORTED_TOOLS[t]())
            except KeyError:
                raise KeyError(f"Tool {t} is not supported.")
        self.tools = tools

        self.llm = OpenAI(model="gpt-4-1106-preview", max_tokens=2000)
        self.agent = ReActAgent.from_tools(
            tools=functools.reduce(
                lambda x, y: x.to_tool_list() + y.to_tool_list(), self.tools
            ),
            llm=self.llm,
            verbose=True,
        )

        self.thoughts = ""
        self.conv = Ansi2HTMLConverter()

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {"agent": self.agent, "llm": self.llm, "tools": self.tools}

    def _handle_user_message(self, user_message, history):
        """
        Handle the user submitted message. Clear message box, and append
        to the history.
        """
        return "", [*history, (user_message, "")]

    def _generate_response(
        self, chat_history: List[Tuple[str, str]]
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Generate the response from agent, and capture the stdout of the
        ReActAgent's thoughts.
        """
        with Capturing() as output:
            response = self.agent.stream_chat(chat_history[-1][0])
        ansi = "\n========\n".join(output)
        html_output = self.conv.convert(ansi)
        for token in response.response_gen:
            chat_history[-1][1] += token
            yield chat_history, str(html_output)

    def _reset_chat(self) -> Tuple[str, str]:
        """Reset the agent's chat history. And clear all dialogue boxes."""
        # clear agent history
        self.agent.reset()
        return "", "", ""  # clear textboxes

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        import gradio as gr

        demo = gr.Blocks(
            theme="gstaff/xkcd",
            css="#box { height: 420px; overflow-y: scroll !important}",
        )
        with demo:
            gr.Markdown(
                "# Gradio ReActAgent Powered by LlamaIndex and LlamaHub 🦙\n"
                "This Gradio app is powered by LlamaIndex's `ReActAgent` with\n"
                "OpenAI's GPT-4-Turbo as the LLM. The tools are listed below.\n"
                "## Tools\n"
                "- [ArxivToolSpec](https://llamahub.ai/l/tools-arxiv)\n"
                "- [WikipediaToolSpec](https://llamahub.ai/l/tools-wikipedia)"
            )
            with gr.Row():
                chat_window = gr.Chatbot(
                    label="Message History",
                    scale=3,
                )
                console = gr.HTML(elem_id="box")
            with gr.Row():
                message = gr.Textbox(label="Write A Message", scale=4)
                clear = gr.ClearButton()

            message.submit(
                self._handle_user_message,
                [message, chat_window],
                [message, chat_window],
                queue=False,
            ).then(
                self._generate_response,
                chat_window,
                [chat_window, console],
            )
            clear.click(self._reset_chat, None, [message, chat_window, console])

        demo.launch(server_name="0.0.0.0", server_port=8080)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-gradio-react-agent-chatbot/llama_index/packs/gradio_react_agent_chatbot/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {"agent": self.agent, "llm": self.llm, "tools": self.tools}

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-gradio-react-agent-chatbot/llama_index/packs/gradio_react_agent_chatbot/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    import gradio as gr

    demo = gr.Blocks(
        theme="gstaff/xkcd",
        css="#box { height: 420px; overflow-y: scroll !important}",
    )
    with demo:
        gr.Markdown(
            "# Gradio ReActAgent Powered by LlamaIndex and LlamaHub 🦙\n"
            "This Gradio app is powered by LlamaIndex's `ReActAgent` with\n"
            "OpenAI's GPT-4-Turbo as the LLM. The tools are listed below.\n"
            "## Tools\n"
            "- [ArxivToolSpec](https://llamahub.ai/l/tools-arxiv)\n"
            "- [WikipediaToolSpec](https://llamahub.ai/l/tools-wikipedia)"
        )
        with gr.Row():
            chat_window = gr.Chatbot(
                label="Message History",
                scale=3,
            )
            console = gr.HTML(elem_id="box")
        with gr.Row():
            message = gr.Textbox(label="Write A Message", scale=4)
            clear = gr.ClearButton()

        message.submit(
            self._handle_user_message,
            [message, chat_window],
            [message, chat_window],
            queue=False,
        ).then(
            self._generate_response,
            chat_window,
            [chat_window, console],
        )
        clear.click(self._reset_chat, None, [message, chat_window, console])

    demo.launch(server_name="0.0.0.0", server_port=8080)

```
  
---|---
