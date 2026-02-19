# Markdown
Node parsers.
##  MarkdownNodeParser #
Bases: `NodeParser`
Markdown node parser.
Splits a document into Nodes using Markdown header-based splitting logic. Each node contains its text content and the path of headers leading to it.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`include_metadata` |  `bool` |  whether to include metadata in nodes |  _required_  
`include_prev_next_rel` |  `bool` |  whether to include prev/next relationships |  _required_  
`header_path_separator` |  `str` |  separator char used for section header path metadata |  `'/'`  
Source code in `llama-index-core/llama_index/core/node_parser/file/markdown.py`

| ```
class MarkdownNodeParser(NodeParser):
    """
    Markdown node parser.

    Splits a document into Nodes using Markdown header-based splitting logic.
    Each node contains its text content and the path of headers leading to it.

    Args:
        include_metadata (bool): whether to include metadata in nodes
        include_prev_next_rel (bool): whether to include prev/next relationships
        header_path_separator (str): separator char used for section header path metadata

    """

    header_path_separator: str = Field(
        default="/", description="Separator char used for section header path metadata."
    )

    @classmethod
    def from_defaults(
        cls,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
        header_path_separator: str = "/",
        callback_manager: Optional[CallbackManager] = None,
    ) -> "MarkdownNodeParser":
        callback_manager = callback_manager or CallbackManager([])
        return cls(
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel,
            header_path_separator=header_path_separator,
            callback_manager=callback_manager,
        )

    def get_nodes_from_node(self, node: BaseNode) -> List[TextNode]:
        """Get nodes from document by splitting on headers."""
        text = node.get_content(metadata_mode=MetadataMode.NONE)
        markdown_nodes = []
        lines = text.split("\n")
        current_section = ""
        # Keep track of (markdown level, text) for headers
        header_stack: List[tuple[int, str]] = []
        code_block = False

        for line in lines:
            # Track if we're inside a code block to avoid parsing headers in code
            if line.lstrip().startswith("```"):
                code_block = not code_block
                current_section += line + "\n"
                continue

            # Only parse headers if we're not in a code block
            if not code_block:
                header_match = re.match(r"^(#+)\s(.*)", line)
                if header_match:
                    # Save the previous section before starting a new one
                    if current_section.strip():
                        markdown_nodes.append(
                            self._build_node_from_split(
                                current_section.strip(),
                                node,
                                self.header_path_separator.join(
                                    h[1] for h in header_stack[:-1]
                                ),
                            )
                        )

                    header_level = len(header_match.group(1))
                    header_text = header_match.group(2)

                    # Compare against top-of-stack item’s markdown level.
                    # Pop headers of equal or higher markdown level; not necessarily current stack size / depth.
                    # Hierarchy depth gets deeper one level at a time, but markdown headers can jump from H1 to H3, for example.
                    while header_stack and header_stack[-1][0] >= header_level:
                        header_stack.pop()

                    # Add the new header
                    header_stack.append((header_level, header_text))
                    current_section = "#" * header_level + f" {header_text}\n"
                    continue

            current_section += line + "\n"

        # Add the final section
        if current_section.strip():
            markdown_nodes.append(
                self._build_node_from_split(
                    current_section.strip(),
                    node,
                    self.header_path_separator.join(h[1] for h in header_stack[:-1]),
                )
            )

        return markdown_nodes

    def _build_node_from_split(
        self,
        text_split: str,
        node: BaseNode,
        header_path: str,
    ) -> TextNode:
        """Build node from single text split."""
        node = build_nodes_from_splits([text_split], node, id_func=self.id_func)[0]

        if self.include_metadata:
            separator = self.header_path_separator
            node.metadata["header_path"] = (
                # ex: "/header1/header2/" || "/"
                separator + header_path + separator if header_path else separator
            )

        return node

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[BaseNode]:
        """Parse nodes."""
        all_nodes: List[BaseNode] = []
        nodes_with_progress = get_tqdm_iterable(nodes, show_progress, "Parsing nodes")

        for node in nodes_with_progress:
            nodes = self.get_nodes_from_node(node)
            all_nodes.extend(nodes)

        return all_nodes

```
  
---|---  
###  get_nodes_from_node #
```
get_nodes_from_node(node: BaseNode) -> List[TextNode]

```

Get nodes from document by splitting on headers.
Source code in `llama-index-core/llama_index/core/node_parser/file/markdown.py`
```
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
102
103
104
105
106
107
```
| ```
def get_nodes_from_node(self, node: BaseNode) -> List[TextNode]:
    """Get nodes from document by splitting on headers."""
    text = node.get_content(metadata_mode=MetadataMode.NONE)
    markdown_nodes = []
    lines = text.split("\n")
    current_section = ""
    # Keep track of (markdown level, text) for headers
    header_stack: List[tuple[int, str]] = []
    code_block = False

    for line in lines:
        # Track if we're inside a code block to avoid parsing headers in code
        if line.lstrip().startswith("```"):
            code_block = not code_block
            current_section += line + "\n"
            continue

        # Only parse headers if we're not in a code block
        if not code_block:
            header_match = re.match(r"^(#+)\s(.*)", line)
            if header_match:
                # Save the previous section before starting a new one
                if current_section.strip():
                    markdown_nodes.append(
                        self._build_node_from_split(
                            current_section.strip(),
                            node,
                            self.header_path_separator.join(
                                h[1] for h in header_stack[:-1]
                            ),
                        )
                    )

                header_level = len(header_match.group(1))
                header_text = header_match.group(2)

                # Compare against top-of-stack item’s markdown level.
                # Pop headers of equal or higher markdown level; not necessarily current stack size / depth.
                # Hierarchy depth gets deeper one level at a time, but markdown headers can jump from H1 to H3, for example.
                while header_stack and header_stack[-1][0] >= header_level:
                    header_stack.pop()

                # Add the new header
                header_stack.append((header_level, header_text))
                current_section = "#" * header_level + f" {header_text}\n"
                continue

        current_section += line + "\n"

    # Add the final section
    if current_section.strip():
        markdown_nodes.append(
            self._build_node_from_split(
                current_section.strip(),
                node,
                self.header_path_separator.join(h[1] for h in header_stack[:-1]),
            )
        )

    return markdown_nodes

```
  
---|---
