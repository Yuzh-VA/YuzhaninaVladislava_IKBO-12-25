# импорт библиотек
import tkinter as tk
from tkinter import scrolledtext
import argparse

from pathlib import Path

from vfs import VirtualFileSystem
# шаблон
class ShellEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_name = "default_vfs"
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.root.title(f"VFS: {self.vfs_name}")
        
        self.cwd = "/"
# поле вывода
        self.output = scrolledtext.ScrolledText(root, height=25, width=100)
        self.output.pack(padx=10, pady=10)
# поле ввода и метода
        self.entry = tk.Entry(root, width=100)
        self.entry.pack(padx=10, pady=(0, 10))
        self.entry.bind("<Return>", self.execute) 
        self.print_prompt()
        
        
        # создаем VFS и загружаем из файла
        self.vfs = VirtualFileSystem()
        if vfs_path:
            try:
                self.vfs.load_from_csv(vfs_path)
                self.vfs_name = Path(vfs_path).stem
                self.root.title(f"VFS: {self.vfs_name}")
            except FileNotFoundError as e:
                self.output.insert(tk.END, f"Error: {e}\n")
            except ValueError as e:
                self.output.insert(tk.END, f"Error: invalid VFS format — {e}\n")

        self.print_prompt()

    def print_prompt(self):
        
        prompt = f"{self.vfs_name}:{self.cwd}$ "
        self.output.insert(tk.END, prompt)
        self.output.see(tk.END)
# метода по кнопке Enter для чтения строки ее очищения, дублирование введенной строки
    def execute(self,event):
        cmd_line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.output.insert(tk.END, cmd_line + "\n")
# разбивание строки 
        parts = cmd_line.split()
        if not parts:
            self.print_prompt()
            return
        self.run_command(cmd_line)  
        
    def run_command(self, cmd_line):
        parts = cmd_line.split()
        if not parts:
            self.print_prompt()
            return

        cmd, args = parts[0], parts[1:]
# команды
        if cmd == "exit":
            self.root.quit()
        elif cmd == "ls":
            self.cmd_ls(args)
        elif cmd == "cd":
            self.cmd_cd(args)
        elif cmd == "wc":
            self.cmd_wc(args)
        elif cmd == "du":
            self.cmd_du(args)
        elif cmd == "conf-dump":
            self.cmd_conf_dump()
        elif cmd == "touch":
            self.cmd_touch(args)
        elif cmd == "vfs-init":
            self.cmd_vfs_init()
        else:
            self.output.insert(tk.END, f"Error: unknown command '{cmd}'\n")
        self.print_prompt()

    
    def cmd_vfs_init(self):
        # заменяет текущую VFS на VFS по умолчанию
        self.vfs = VirtualFileSystem()
        self.vfs_name = "default_vfs"
        self.root.title(f"VFS: {self.vfs_name}")
        self.cwd = "/"
        self.output.insert(tk.END, "VFS has been reset to default.\n")
    
    def cmd_conf_dump(self):
        #выводит параметры эмулятора как ключ-значение
        self.output.insert(tk.END, f"vfs_name = {self.vfs_name}\n")
        self.output.insert(tk.END, f"vfs_path = {self.vfs_path}\n")
        self.output.insert(tk.END, f"script_path = {self.script_path}\n")
        self.output.insert(tk.END, f"vfs_loaded = {self.vfs is not None}\n")
        

    def _resolve_path(self, path):
        #превращает относительный путь в абсолютный внутри VFS
        if not path:
            return self.cwd
        if path.startswith("/"):
            return path  # уже абсолютный
        
        #склеиваем текущую директорию и относительный путь
        if self.cwd == "/":
            return f"/{path}"
        return f"{self.cwd.rstrip('/')}/{path}"


    def cmd_ls(self, args):
        #выводит содержимое директории
        # Если передан аргумент смотрим в него или в текущую
        target = self._resolve_path(args[0]) if args else self.cwd

        if not self.vfs.exists(target):
            self.output.insert(tk.END, f"ls: cannot access '{target}': No such file or directory\n")
            return

        if not self.vfs.is_dir(target):
            #если это файл просто выводим его имя
            self.output.insert(tk.END, f"{target.split('/')[-1]}\n")
            return

        try:
            items = self.vfs.list_dir(target)
            if not items:
                return  #пустая папка ничего не выводим
            for item in items:
                #папка это или файл чтобы добавить /
                item_path = self._resolve_path(item) if target == "/" else f"{target.rstrip('/')}/{item}"
                is_dir = self.vfs.is_dir(item_path)
                suffix = "/" if is_dir else ""
                self.output.insert(tk.END, f"{item}{suffix}\n")
        except Exception as e:
            self.output.insert(tk.END, f"ls: error: {e}\n")


    def cmd_cd(self, args):
        if not args:
            self.cwd = "/"  # cd без аргументов в корень
            return

        target = self._resolve_path(args[0])

        if not self.vfs.exists(target):
            self.output.insert(tk.END, f"cd: no such file or directory: {args[0]}\n")
            return
        if not self.vfs.is_dir(target):
            self.output.insert(tk.END, f"cd: not a directory: {args[0]}\n")
            return

        #убираем двойные слеши и добавляем /
        self.cwd = "/" + "/".join([p for p in target.split("/") if p])


    def cmd_wc(self, args):
        #считает строки слова и символы в файле
        if not args:
            self.output.insert(tk.END, "wc: missing file operand\n")
            return

        target = self._resolve_path(args[0])
        if not self.vfs.exists(target):
            self.output.insert(tk.END, f"wc: {args[0]}: No such file or directory\n")
            return
        if self.vfs.is_dir(target):
            self.output.insert(tk.END, f"wc: {args[0]}: Is a directory\n")
            return

        try:
            content = self.vfs.read_file(target)
            lines = content.splitlines()
            line_count = len(lines)
            word_count = len(content.split())
            char_count = len(content)
            self.output.insert(
                tk.END, 
                f"{line_count:>5} {word_count:>5} {char_count:>5} {args[0]}\n"
            )
        except Exception as e:
            self.output.insert(tk.END, f"wc: error: {e}\n")


    def cmd_du(self, args):
        #размер файла
        target = self._resolve_path(args[0]) if args else self.cwd

        if not self.vfs.exists(target):
            self.output.insert(tk.END, f"du: cannot access '{args[0] if args else target}': No such file or directory\n")
            return

        try:
            size = self.vfs.get_size(target)
            display_name = args[0] if args else "."
            self.output.insert(tk.END, f"{size}\t{display_name}\n")
        except Exception as e:
            self.output.insert(tk.END, f"du: error: {e}\n")
        
    def cmd_touch(self, args):
        # создает пустой файл
        if not args:
            self.output.insert(tk.END, "touch: missing file operand\n")
            return
        target = self._resolve_path(args[0])
        try:
            self.vfs.touch(target)
        except IsADirectoryError:
            self.output.insert(tk.END, f"touch: cannot touch '{args[0]}': Is a directory\n")
        except FileNotFoundError:
            self.output.insert(tk.END, f"touch: cannot touch '{args[0]}': No such file or directory\n")
        except Exception as e:
            self.output.insert(tk.END, f"touch: error: {e}\n")
        
        
def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор командной оболочки")
    parser.add_argument("--vfs", type=str, default=None,
                        help="Путь к физическому расположению VFS")
    parser.add_argument("--script", type=str, default=None,
                        help="Путь к стартовому скрипту")
    return parser.parse_args()
    
def run_script(shell, script_path):
    
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        shell.output.insert(tk.END, f"Error: script not found: {script_path}\n")
        return

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        shell.output.insert(tk.END, f"{shell.vfs_name}$ {line}\n")
        try:
            shell.run_command(line)
        except Exception as e:
            shell.output.insert(tk.END, f"Error: {e}\n")

def main():
    args = parse_args()
    root = tk.Tk()
    shell = ShellEmulator(root, vfs_path=args.vfs, script_path=args.script)
    if args.script:
        root.after(100, lambda: run_script(shell, args.script))
    root.mainloop()
        
# работа окна
if __name__ == "__main__":
    main()