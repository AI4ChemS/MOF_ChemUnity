import xml.etree.ElementTree as ET

class XMLToMD:
    def __init__(self):
        self.namespace = {"tei": "http://www.tei-c.org/ns/1.0"}

    @staticmethod
    def clean_text(text):
        """Cleans up text by stripping whitespace and replacing newlines."""
        return text.replace("\n", " ").replace("\r", " ").strip()

    def parse_cell(self, cell):
        """Parses a <cell> element, including nested tags like <hi>."""
        cell_content = ''.join(cell.itertext())  # Get all nested text
        return self.clean_text(cell_content)

    def format_table(self, table):
        """Formats a TEI table into Markdown table syntax."""
        table_lines = []

        # Process table headers
        headers = table.findall("tei:head", self.namespace)
        if headers:
            for header in headers:
                table_lines.append(f"**{self.clean_text(''.join(header.itertext()))}**\n")

        rows = [row for row in table.findall("tei:row", self.namespace) if row.tag.endswith("row")]
        if not rows:
            return ""

        # Process header row if it exists
        header_cells = rows[0].findall("tei:cell", self.namespace)
        if header_cells:
            header_texts = [self.parse_cell(cell) for cell in header_cells]
            table_lines.append("| " + " | ".join(header_texts) + " |")
            table_lines.append("|" + "|".join("---" for _ in header_texts) + "|")

        # Process data rows
        for row in rows[1:]:
            cells = row.findall("tei:cell", self.namespace)
            row_texts = [self.parse_cell(cell) for cell in cells]
            table_lines.append("| " + " | ".join(row_texts) + " |")

        return "\n".join(table_lines) + "\n\n"

    def process_text(self, elem):
        """Process any text, including <hi> tags, to extract plain text."""
        if elem.tag.endswith('hi'):  # If it's a <hi> tag, return its plain text
            text = self.clean_text(elem.text) if elem.text else ''
            return text
        elif elem.text:  # For regular text nodes
            return self.clean_text(elem.text)
        return ''

    def process_paragraph(self, paragraph):
        """Process a paragraph, extracting plain text, ignoring formatting."""
        content = []
        skip_table = False

        for elem in paragraph.iter():
            if elem.tag.endswith('table'):
                skip_table = True
                continue
            elif skip_table and elem.tag.endswith('/table'):
                skip_table = False
                continue

            if skip_table:
                continue

            # Process the text normally
            content.append(self.process_text(elem))
            if elem.tail:
                content.append(self.clean_text(elem.tail))

        return ''.join(content)

    def process_head(self, head):
        """Process <head> element, extracting plain text without formatting."""
        content = []
        for elem in head.iter():
            content.append(self.process_text(elem))
            if elem.tail:
                content.append(self.clean_text(elem.tail))

        return ''.join(content)

    def tei_to_markdown(self, tei_file, markdown_file):
        """Converts a TEI XML file to Markdown format."""
        tree = ET.parse(tei_file)
        root = tree.getroot()

        markdown_lines = []

        # Extract title
        title = root.find(".//tei:title[@type='main']", self.namespace)
        if title is not None:
            markdown_lines.append(f"# {self.clean_text(title.text)}\n\n")

        # Process body content
        body = root.find(".//tei:body", self.namespace)
        if body:
            for div in body.findall(".//tei:div", self.namespace):
                section_title = div.find("tei:head", self.namespace)
                if section_title is not None:
                    markdown_lines.append(f"## {self.process_head(section_title)}\n\n")

                for paragraph in div.findall("tei:p", self.namespace):
                    processed_text = self.process_paragraph(paragraph)
                    if processed_text:
                        markdown_lines.append(f"{processed_text}\n\n")

                for table in div.findall(".//tei:table", self.namespace):
                    markdown_lines.append("\n")
                    markdown_lines.append(self.format_table(table))
                    markdown_lines.append("\n")

        with open(markdown_file, "w", encoding="utf-8") as md_file:
            md_file.writelines(markdown_lines)
