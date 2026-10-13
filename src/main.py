# импорт библиотек
import tkinter as tk
from tkinter import scrolledtext
import argparse
# шаблон
class ShellEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_name = "default_vfs"
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.root.title(f"VFS: {self.vfs_name}")
# поле вывода
        self.output = scrolledtext.ScrolledText(root, height=25, width=100)
        self.output.pack(padx=10, pady=10)
# поле ввода и метода
        self.entry = tk.Entry(root, width=100)
        self.entry.pack(padx=10, pady=(0, 10))
        self.entry.bind("<Return>", self.execute) 
        self.print_prompt()
        
    def print_prompt(self):
        self.output.insert(tk.END, f"{self.vfs_name}$ ")
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
            self.output.insert(tk.END, f"ls called with args: {args}\n")
        elif cmd == "cd":
            self.output.insert(tk.END, f"cd called with args: {args}\n")
        elif cmd == "conf-dump":
            self.cmd_conf_dump()
        else:
            self.output.insert(tk.END, f"Error: unknown command '{cmd}'\n")

        self.print_prompt()

    
    def cmd_conf_dump(self):
        """Выводит параметры эмулятора в формате ключ-значение."""
        self.output.insert(tk.END, f"vfs_name = {self.vfs_name}\n")
        self.output.insert(tk.END, f"vfs_path = {self.vfs_path}\n")
        self.output.insert(tk.END, f"script_path = {self.script_path}\n")
        
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
    # root = tk.Tk()
    # app = ShellEmulator(root)
    # root.mainloop()  
    main()