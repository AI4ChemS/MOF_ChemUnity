import xml.etree.ElementTree as ET
from pathlib import Path

class TEI_Parser:
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

    def xml_to_markdown(self, tei_file, markdown_file):
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


class Elsevier_Parser:
    def __init__(self):
        self.namespaces = {
            "default": "http://www.elsevier.com/xml/svapi/article/dtd",
            "ce": "http://www.elsevier.com/xml/common/dtd",
            "ns1": "http://www.elsevier.com/xml/common/cals/dtd",  # Added for ns1 prefix
            "mml": "http://www.w3.org/1998/Math/MathML"
        }

    @staticmethod
    def extract_text(element):
        """Recursively extracts and cleans text, including inline elements."""
        if element is None:
            return ""
        # Start with the text of the current element
        text = (element.text or "")
        # Recursively process children
        for child in element:
            text += "" + Elsevier_Parser.extract_text(child)
            # Include tail text after the child element
            if child.tail:
                text += "" + child.tail
        # Normalize spaces
        return " ".join(text.split())

    def parse_table(self, table):
        """Parses a table element, including <tgroup>, and formats it into Markdown."""
        rows = []
        headers = []

        # Parse the table caption
        caption_element = table.find(".//ce:caption/ce:simple-para", self.namespaces)
        caption = self.extract_text(caption_element).strip() if caption_element is not None else "Table"

        # Locate <tgroup>
        tgroup = table.find(".//ns1:tgroup", self.namespaces)
        if tgroup is None:
            return f"### {caption}\n\n*No table data found*\n\n"

        # Extract headers
        thead = tgroup.find(".//ns1:thead", self.namespaces)
        if thead is not None:
            for row in thead.findall(".//ns1:row", self.namespaces):
                header_cells = [self.extract_text(cell).strip() for cell in row.findall(".//ce:entry", self.namespaces)]
                headers.append(header_cells)

        # Extract rows
        tbody = tgroup.find(".//ns1:tbody", self.namespaces)
        if tbody is not None:
            for row in tbody.findall(".//ns1:row", self.namespaces):
                row_cells = [self.extract_text(cell).strip() for cell in row.findall(".//ce:entry", self.namespaces)]
                rows.append(row_cells)

        # Build Markdown table
        markdown_table = f"### {caption}\n\n"
        if headers:
            for header_row in headers:
                markdown_table += "| " + " | ".join(header_row) + " |\n"
                markdown_table += "|" + "|".join(["---"] * len(header_row)) + "|\n"
        for row in rows:
            markdown_table += "| " + " | ".join(row) + " |\n"

        return markdown_table + "\n\n"

    def xml_to_markdown(self, xml_file, md_file):
        """Converts the XML file to Markdown and writes to the md_file."""
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Extract title with inline formatting
        title_element = root.find(".//ce:title", self.namespaces)
        title = self.extract_text(title_element).strip() if title_element is not None else "Untitled"

        md_content = f"# {title}\n\n"

        # Extract abstract
        abstract_paragraphs = []
        for para in root.findall(".//ce:abstract//ce:simple-para", self.namespaces):
            abstract_paragraphs.append(self.extract_text(para).strip())
        if abstract_paragraphs:
            md_content += f"## Abstract\n{' '.join(abstract_paragraphs)}\n\n"

        # Extract sections and their content
        for section in root.findall(".//ce:section", self.namespaces):
            sec_title = section.find("ce:section-title", self.namespaces)
            if sec_title is not None:
                md_content += f"## {self.extract_text(sec_title).strip()}\n\n"

            for para in section.findall("ce:para", self.namespaces):
                md_content += f"{self.extract_text(para).strip()}\n\n"

            # Extract tables
            for table in section.findall(".//ce:table", self.namespaces):
                md_content += self.parse_table(table)

        # Extract floating tables
        for table in root.findall(".//ce:table", self.namespaces):
            if table not in root.findall(".//ce:section//ce:table", self.namespaces):
                md_content += self.parse_table(table)

        Path(md_file).write_text(md_content, encoding="utf-8")
