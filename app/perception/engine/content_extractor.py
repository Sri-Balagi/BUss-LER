import html
from html.parser import HTMLParser
import re


class HTMLTextExtractor(HTMLParser):
    """Clean plain-text extractor using standard library HTMLParser."""

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []
        self._ignore: bool = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in ("script", "style"):
            self._ignore = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in ("script", "style"):
            self._ignore = False
        elif tag.lower() in ("p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"):
            self._pieces.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignore:
            self._pieces.append(data)

    def get_text(self) -> str:
        raw = "".join(self._pieces)
        # Normalize whitespace while preserving paragraphs
        lines = [line.strip() for line in raw.splitlines()]
        clean = "\n".join(line for line in lines if line)
        return html.unescape(clean)


class ContentExtractor:
    """Extracts and cleans text from raw provider content."""

    @staticmethod
    def clean_html(html_content: str) -> str:
        """Strip HTML tags and convert to clean plain text."""
        if not html_content or not isinstance(html_content, str):
            return ""
        parser = HTMLTextExtractor()
        try:
            parser.feed(html_content)
            return parser.get_text()
        except Exception:
            # Fallback regex strip if parser encounters broken HTML
            clean = re.sub(r"<[^>]+>", " ", html_content)
            return re.sub(r"\s+", " ", clean).strip()

    @staticmethod
    def extract_text(raw_payload: dict, resource_type: str) -> str:
        """Derive readable content string based on payload & resource_type."""
        if not raw_payload:
            return ""

        # Gmail message
        if resource_type == "email" or "snippet" in raw_payload:
            snippet = raw_payload.get("snippet", "")
            body = raw_payload.get("body", "") or raw_payload.get("body_html", "")
            if body:
                cleaned_body = ContentExtractor.clean_html(body)
                return cleaned_body if len(cleaned_body) > len(snippet) else snippet
            return snippet

        # Drive file / document
        if resource_type == "file" or "name" in raw_payload:
            name = raw_payload.get("name", "")
            description = raw_payload.get("description", "")
            text_content = raw_payload.get("content", "") or raw_payload.get("text", "")
            parts = [name, description, text_content]
            return "\n\n".join(p for p in parts if p)

        # Calendar event
        if resource_type == "event" or "summary" in raw_payload:
            summary = raw_payload.get("summary", "")
            description = ContentExtractor.clean_html(raw_payload.get("description", ""))
            location = raw_payload.get("location", "")
            attendees = ", ".join(
                a.get("email", "") for a in raw_payload.get("attendees", []) if isinstance(a, dict)
            )
            parts = [f"Event: {summary}"]
            if location:
                parts.append(f"Location: {location}")
            if attendees:
                parts.append(f"Attendees: {attendees}")
            if description:
                parts.append(f"Description:\n{description}")
            return "\n".join(parts)

        # Generic fallback
        return str(raw_payload.get("content", raw_payload.get("text", "")))
