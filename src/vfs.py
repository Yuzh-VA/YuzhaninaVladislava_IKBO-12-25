import csv
import base64
from pathlib import Path

class VFSNode:
    # либо директория, либо файл VFS.
    def __init__(self, name, is_dir=True, content=""):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {}  # имя
        
class VirtualFileSystem:
    # Виртуальная файловая система в памяти.

    def __init__(self):
        self.root = VFSNode("", is_dir=True)

    def load_from_csv(self, path):
        # Загружает VFS из CSV-файла.

        
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"VFS file not found: {path}")
        if not file_path.is_file():
            raise ValueError(f"VFS path is not a file: {path}")

        self.root = VFSNode("", is_dir=True)

        try:
            with open(file_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or "type" not in reader.fieldnames \
                        or "path" not in reader.fieldnames:
                    raise ValueError("Invalid CSV: missing 'type' or 'path' column")
                for row in reader:
                    self._add_node(row)
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {e}")

    def _add_node(self, row):
        
        node_type = (row.get("type") or "").strip()
        raw_path = (row.get("path") or "").strip()
        content = row.get("content") or ""

        if not node_type or not raw_path:
            return  # пустая строка 

        if node_type not in ("dir", "file"):
            raise ValueError(f"Unknown node type: {node_type}")

        # раскодируем если содержимое в base64 
        if content.startswith("base64:"):
            try:
                content = base64.b64decode(content[7:]).decode("utf-8", errors="replace")
            except Exception:
                content = ""

        parts = [p for p in raw_path.split("/") if p]
        current = self.root
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            if part not in current.children:
                is_dir = (not is_last) or (node_type == "dir")
                current.children[part] = VFSNode(part, is_dir=is_dir)
            current = current.children[part]

        if node_type == "file":
            current.is_dir = False
            current.content = content