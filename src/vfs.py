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
    
    def _resolve(self, path):
        #  узел по пути или None
        if not path or path == "/":
            return self.root
        parts = [p for p in path.split("/") if p]
        current = self.root
        for part in parts:
            if part not in current.children:
                return None
            current = current.children[part]
        return current

    def exists(self, path):
        return self._resolve(path) is not None

    def is_dir(self, path):
        node = self._resolve(path)
        return node is not None and node.is_dir

    def list_dir(self, path):
        node = self._resolve(path)
        if node is None:
            raise FileNotFoundError(f"No such directory: {path}")
        if not node.is_dir:
            raise NotADirectoryError(f"Not a directory: {path}")
        return sorted(node.children.keys())

    def read_file(self, path):
        node = self._resolve(path)
        if node is None:
            raise FileNotFoundError(f"No such file: {path}")
        if node.is_dir:
            raise IsADirectoryError(f"Is a directory: {path}")
        return node.content

    
    
    def get_size(self, path):
        # возвращает размер файла или суммарный размер папки
        node = self._resolve(path)
        if node is None:
            raise FileNotFoundError(f"No such file or directory: {path}")

        if not node.is_dir:
            #размер файла
            return len(node.content.encode("utf-8"))

        #если это папка суммируем размеры всех детей
        total = 0
        for child in node.children.values():
            total += self._get_node_size(child)
        return total

    def _get_node_size(self, node):
        #размер узла
        if not node.is_dir:
            return len(node.content.encode("utf-8"))
        total = 0
        for child in node.children.values():
            total += self._get_node_size(child)
        return total