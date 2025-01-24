import os
import json
from notion_client import Client
from datetime import datetime
from scrap import load_config

class NotionJSONUploader:
    def __init__(self, token, database_id=None):
        self.notion = Client(auth=token)
        self.database_id = database_id
        self.debug = True
        self.valid_block_types = {
            "paragraph", "heading_1", "heading_2", "heading_3",
            "bulleted_list_item", "numbered_list_item"
        }
        self.MAX_BLOCKS_PER_REQUEST = 100
        
        if database_id:
            self._debug_print(f"Using existing database with ID: {database_id}")
        else:
            self._debug_print("No database ID provided, will create a new database")

    def _chunk_blocks(self, blocks, max_size=100):
        """Split blocks into chunks that respect Notion's block limit."""
        chunks = []
        current_chunk = []
        current_size = 0

        for block in blocks:
            # If adding this block would exceed the limit, start a new chunk
            if current_size + 1 > max_size:
                chunks.append(current_chunk)
                current_chunk = []
                current_size = 0
            
            current_chunk.append(block)
            current_size += 1

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)

        return chunks
    
    
    def create_new_database(self, parent_page_id, database_title):
        """Creates a new database with the updated schema"""
        new_database = self.notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": database_title}}],
            properties={
                "Title": {"title": {}},
                "Journal": {"select": {}},
                "Publication Date": {"date": {}},
                "Keywords": {"multi_select": {}},
                "URL": {"url": {}},
                "Research Gap": {"rich_text": {}},
                "Objective": {"rich_text": {}},
                "Research Design": {"rich_text": {}},
                "Comparative Analysis": {"rich_text": {}},
                "Implications": {"rich_text": {}},
            }
        )
        self.database_id = new_database["id"]
        self._debug_print(f"Created new database with ID: {self.database_id}")

    def _debug_print(self, message):
        if self.debug:
            print(f"DEBUG: {message}")

    def _convert_date(self, date_str):
        if not date_str:
            return None
        try:
            dt = datetime.strptime(date_str, "%B %d, %Y")
            return {"start": dt.isoformat()}
        except ValueError:
            return None

    def _create_header(self, text, level=2):
        if not text:
            return None
        adjusted_level = min(max(1, level), 3)
        return {
            "type": f"heading_{adjusted_level}",
            f"heading_{adjusted_level}": {
                "rich_text": [{"type": "text", "text": {"content": str(text)}}]
            }
        }

    def _create_bullets(self, items):
        if not items or not isinstance(items, list):
            return []
        return [{
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": str(item).strip()}}]
            }
        } for item in items if item and str(item).strip()]

    def _create_paragraph(self, text):
        if not text or not str(text).strip():
            return None
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": str(text).strip()}}]
            }
        }

    def _validate_block(self, block):
        if not isinstance(block, dict) or 'type' not in block:
            return False
        if block['type'] not in self.valid_block_types:
            return False
        return block['type'] in block

    def _process_nested(self, data, level=2):
        blocks = []
        if isinstance(data, dict):
            for key, value in data.items():
                if header := self._create_header(key, level):
                    blocks.append(header)
                    blocks.extend(self._process_nested(value, level+1))
        elif isinstance(data, list):
            blocks.extend(self._create_bullets(data))
        else:
            if paragraph := self._create_paragraph(data):
                blocks.append(paragraph)
        return [b for b in blocks if self._validate_block(b)]

    def create_page(self, json_data):
        if not json_data.get("Title"):
            raise ValueError("Title is required")

        properties = {
            "Title": {
                "title": [
                    {"type": "text", "text": {"content": str(json_data["Title"]).strip()}}
                ]
            }
        }

        # Handle Journal
        if json_data.get("Journal"):
            # Remove or replace commas
            journal_clean = json_data["Journal"].replace(",", " ")
            properties["Journal"] = {
                "select": {"name": journal_clean.strip()}
            }

        # Handle Publication Date
        if json_data.get("Publication Date"):
            if date := self._convert_date(json_data["Publication Date"]):
                properties["Publication Date"] = {"date": date}

        # Handle Keywords
        if json_data.get("Keywords"):
            valid_keywords = []
            for kw in json_data["Keywords"]:
                # Split each keyword on commas and strip whitespace
                for sub_kw in kw.split(","):
                    sub_kw_clean = sub_kw.strip()
                    if sub_kw_clean:
                        valid_keywords.append(sub_kw_clean)
            if valid_keywords:
                properties["Keywords"] = {
                    "multi_select": [{"name": kw} for kw in valid_keywords]
                }

        # Handle DOI/URL
        if json_data.get("DOI or URL"):
            properties["URL"] = {"url": str(json_data["DOI or URL"]).strip()}

        # Handle Research Gap
        if rg := json_data.get("Research Gap Or Problem Statement").get("Research Gap"):
            if isinstance(rg, str):
                content = rg
            else:  # Assume a list of strings
                content = "\n".join(f"- {item}" for item in rg)
            properties["Research Gap"] = {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            }
            

        # Handle Objective
        if rg := json_data.get("Objective"):
            if isinstance(rg, str):
                content = rg
            else:  # Assume a list of strings
                content = "\n".join(f"- {item}" for item in rg)
            properties["Objective"] = {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            }
            
        # Handle Research Design
        if rg := json_data.get("Methodology").get("Research Design"):
            if isinstance(rg, str):
                content = rg
            else:  # Assume a list of strings
                content = "\n".join(f"- {item}" for item in rg)
            properties["Research Design"] = {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            }
            
        # Handle Comparative Analysis
        if rg := json_data.get("Experiment").get("Comparative Analysis"):
            if isinstance(rg, str):
                content = rg
            else:  # Assume a list of strings
                content = "\n".join(f"- {item}" for item in rg)
            properties["Comparative Analysis"] = {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            }
            
        # Handle Implications
        if rg := json_data.get("Results And Discussions").get("Implications"):
            if isinstance(rg, str):
                content = rg
            else:  # Assume a list of strings
                content = "\n".join(f"- {item}" for item in rg)
            properties["Implications"] = {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            }

        # Process content sections
        all_blocks = []
        sections = [
            ("Abstract", json_data.get("Abstract")),
            ("1. Research Gap and Problem Statement", json_data.get("Research Gap Or Problem Statement")),
            ("2. Methodology", json_data.get("Methodology")),
            ("3. Experiment", json_data.get("Experiment")),
            ("4. Results and Discussions", json_data.get("Results And Discussions")),
            ("5. Contribution", json_data.get("Contribution"))
        ]
        
        for section_title, section_data in sections:
            if section_data:
                if header := self._create_header(section_title, 2):
                    all_blocks.append(header)
                    processed_blocks = self._process_nested(section_data, 3)
                    all_blocks.extend(b for b in processed_blocks if self._validate_block(b))

        if not all_blocks:
            self._debug_print("No content blocks created")
            return None

        # Create the initial page with the first chunk of blocks
        block_chunks = self._chunk_blocks(all_blocks, self.MAX_BLOCKS_PER_REQUEST)
        
        # Create initial page with first chunk
        page = self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=properties,
            children=block_chunks[0] if block_chunks else []
        )
        page_id = page["id"]

        # Append remaining chunks using the append_block_children endpoint
        for chunk in block_chunks[1:]:
            self.notion.blocks.children.append(
                block_id=page_id,
                children=chunk
            )

        return page_id

def main():
    config = load_config("config.yaml")
    token = config["notion_api_token"]
    database_id = config.get("database_id")
    
    uploader = NotionJSONUploader(token, database_id)
    
    if not database_id:
        parent_page_id = config["parent_page_id"]
        db_title = config["new_database_title"]
        uploader.create_new_database(parent_page_id, db_title)
    
    gemini_output_folder = config["gemini_output_folder"]
    for file in os.listdir(gemini_output_folder):
        if not file.endswith(".json"):
            continue
        try:
            with open(os.path.join(gemini_output_folder, file), 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                page_id = uploader.create_page(json_data)
                print(f"Successfully created page: {page_id}" if page_id else "Failed to create page")
        except:
            print(f"Error processing file: {file}")

if __name__ == "__main__":
    main()
