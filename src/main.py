# импорт библиотек
import tkinter as tk
from tkinter import scrolledtext

# шаблон
class ShellEmulator:
    def __init__(self, root):
        self.root = root
        self.vfs_name = "default_vfs"
        self.root.title(f"VFS: {self.vfs_name}")
# поле вывода
        self.output = scrolledtext.ScrolledText(root, height=25, width=100)
        self.output.pack(padx=10, pady=10)
# поле ввода и метода
        self.entry = tk.Entry(root, width=100)
        self.entry.pack(padx=10, pady=(0, 10))
        self.entry.bind("<Return>", self.execute) 
        self.print_prompt()

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

        cmd, args = parts[0], parts[1:]
# команды
        if cmd == "exit":
            self.root.quit()
        elif cmd == "ls":
            self.output.insert(tk.END, f"ls called with args: {args}\n")
        elif cmd == "cd":
            self.output.insert(tk.END, f"cd called with args: {args}\n")
        else:
            self.output.insert(tk.END, f"Error: unknown command '{cmd}'\n")

        self.print_prompt()

# работа окна
if __name__ == "__main__":
    root = tk.Tk()
    app = ShellEmulator(root)
    root.mainloop()