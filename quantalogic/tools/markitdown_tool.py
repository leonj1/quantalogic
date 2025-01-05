"""Tool for converting various file formats to Markdown using the MarkItDown library."""

import os
import tempfile
from typing import Optional

from quantalogic.tools.tool import Tool, ToolArgument
from quantalogic.utils.download_http_file import download_http_file

MAX_LINES = 2000  # Maximum number of lines to return when no output file is specified

class MarkitdownTool(Tool):
    """Tool for converting various file formats to Markdown using the MarkItDown library."""

    name: str = "markitdown_tool"
    description: str = (
        "Converts various file formats to Markdown using the MarkItDown library. "
        "Supports both local file paths and URLs (http://, https://). "
        "Supported formats include: PDF, PowerPoint, Word, Excel, HTML"
    )
    arguments: list = [
        ToolArgument(
            name="file_path",
            arg_type="string",
            description="The path to the file to convert. Can be a local path or URL (http://, https://).",
            required=True,
            example="/path/to/file.txt or https://example.com/file.pdf",
        ),
        ToolArgument(
            name="output_file_path",
            arg_type="string",
            description="Path to write the Markdown output to. You can use a temp file.",
            required=False,
            example="/path/to/output.md",
        ),
    ]

    def execute(self, file_path: str, output_file_path: Optional[str] = None) -> str:
        """Converts a file to Markdown and returns or writes the content.

        Args:
            file_path (str): The path to the file to convert. Can be a local path or URL.
            output_file_path (str, optional): Optional path to write the Markdown output to.

        Returns:
            str: The Markdown content or a success message.
        """
        # Handle tilde expansion for local paths
        if file_path.startswith("~"):
            file_path = os.path.expanduser(file_path)

        # Handle URL paths
        if file_path.startswith(("http://", "https://")):
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name
                    # Download the file from URL
                    download_http_file(file_path, temp_path)
                    # Use the temporary file path for conversion
                    file_path = temp_path
                    is_temp_file = True
            except Exception as e:
                return f"Error downloading file from URL: {str(e)}"
        else:
            is_temp_file = False

        try:
            from markitdown import MarkItDown

            md = MarkItDown()
            result = md.convert(file_path)

            if output_file_path:
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(result.text_content)
                output_message = f"Markdown content successfully written to {output_file_path}"
            else:
                # Truncate content if it exceeds MAX_LINES
                lines = result.text_content.splitlines()
                if len(lines) > MAX_LINES:
                    truncated_content = "\n".join(lines[:MAX_LINES])
                    output_message = f"Markdown content truncated to {MAX_LINES} lines:\n{truncated_content}"
                else:
                    output_message = result.text_content

            return output_message
        except Exception as e:
            return f"Error converting file to Markdown: {str(e)}"
        finally:
            # Clean up temporary file if it was created
            if is_temp_file and os.path.exists(file_path):
                os.remove(file_path)


if __name__ == "__main__":
    tool = MarkitdownTool()
    print(tool.to_markdown())

    # Example usage:
    print(tool.execute(file_path="./examples/2412.18601v1.pdf"))

    print(tool.execute(file_path="https://arxiv.org/pdf/2412.18601"))
