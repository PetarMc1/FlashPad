import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox

class Flashpad(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Flashpad")
        self.geometry("800x600")
        self.iconbitmap('./icon.ico')

        self.current_font_size = 12
        self.current_font = tkfont.Font(family="Consolas", size=self.current_font_size)
        self.current_file = None

        self.text_bg = '#1e1e1e'
        self.text_fg = 'white'
        self.cursor_color = 'white'
        self.line_bg = '#2d2d2d'
        self.line_fg = 'white'
        self.scrollbar_bg = '#2d2d2d'
        self.scrollbar_fg = 'white'
        self.theme = "dark"

        self.create_menu_bar()

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.text_frame = tk.Frame(self.main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(self.text_frame, width=4, padx=4, takefocus=0, border=0,
                                    state='disabled', font=self.current_font, bg=self.line_bg, fg=self.line_fg)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.text_widget = tk.Text(self.text_frame, undo=True, wrap=tk.NONE, font=self.current_font,
                                   bg=self.text_bg, fg=self.text_fg, insertbackground=self.cursor_color)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_y = tk.Scrollbar(self.text_frame, command=self.on_y_scroll)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x = tk.Scrollbar(self.main_frame, command=self.text_widget.xview, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_widget.config(xscrollcommand=self.scrollbar_x.set)

        self.text_frame.pack_propagate(False)
        self.main_frame.pack_propagate(False)

        self.text_widget.bind("<<Modified>>", self.on_text_change)
        self.text_widget.bind("<KeyRelease>", self.on_text_change)
        self.text_widget.bind("<ButtonRelease-1>", self.on_text_change)

        self.bind_all("<Control-s>", self.save_file)
        self.bind_all("<Control-o>", self.open_file)
        self.bind_all("<Control-n>", self.new_file)
        self.bind_all("<Control-p>", self.print_file)
        self.bind_all("<Control-equal>", self.increase_font_size)
        self.bind_all("<Control-minus>", self.decrease_font_size)
        self.bind_all("<Control-0>", self.reset_font_size)

        self.finalize_setup()

    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self, bg='#f0f0f0', fg='black', bd=0)
        self.configure(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl + N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl + O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl + S")
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Print", command=self.print_file, accelerator="Ctrl + P")
        self.file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl + Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl + Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl + X")
        self.edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl + C")
        self.edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl + V")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.view_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)
        self.view_menu.add_command(label="Zoom In", command=self.increase_font_size, accelerator="Ctrl + =")
        self.view_menu.add_command(label="Zoom Out", command=self.decrease_font_size, accelerator="Ctrl + -")
        self.view_menu.add_command(label="Reset Zoom", command=self.reset_font_size, accelerator="Ctrl + 0")
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Switch to Light Theme", command=lambda: self.switch_theme("light"))
        self.view_menu.add_command(label="Switch to Dark Theme", command=lambda: self.switch_theme("dark"))
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

    def finalize_setup(self):
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "dark":
            self.text_bg = '#1e1e1e'
            self.text_fg = 'white'
            self.cursor_color = 'white'
            self.line_bg = '#2d2d2d'
            self.line_fg = 'white'
            self.scrollbar_bg = '#2d2d2d'
            self.scrollbar_fg = 'white'
        else:
            self.text_bg = 'white'
            self.text_fg = 'black'
            self.cursor_color = 'black'
            self.line_bg = '#f0f0f0'
            self.line_fg = 'black'
            self.scrollbar_bg = '#f0f0f0'
            self.scrollbar_fg = 'black'

        self.text_widget.config(bg=self.text_bg, fg=self.text_fg, insertbackground=self.cursor_color)
        self.line_numbers.config(bg=self.line_bg, fg=self.line_fg)
        self.scrollbar_y.config(bg=self.scrollbar_bg, troughcolor=self.scrollbar_bg)
        self.scrollbar_x.config(bg=self.scrollbar_bg, troughcolor=self.scrollbar_bg)

    def save_file(self, event=None):
        if hasattr(self, 'current_file') and self.current_file:
            response = messagebox.askyesno("Save", f"Do you want to save changes to {self.current_file}?")
            if response:
                with open(self.current_file, "w") as file:
                    file.write(self.text_widget.get(1.0, tk.END))
                    messagebox.showinfo("Save", f"File saved successfully: {self.current_file}")
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("All Files", "*.*")])
            if file_path:
                with open(file_path, "w") as file:
                    file.write(self.text_widget.get(1.0, tk.END))
                    self.current_file = file_path
                    self.title(f"Flashpad - {file_path}")
                    messagebox.showinfo("Save", f"File saved successfully: {file_path}")

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, content)
                self.current_file = file_path
                self.title(f"Flashpad - {file_path}")

    def new_file(self, event=None):
        if hasattr(self, 'current_file') and self.current_file:
            response = messagebox.askyesno("New File", "Do you want to save changes to the current file?")
            if response:
                self.save_file()
        self.text_widget.delete(1.0, tk.END)
        self.current_file = None
        self.title("Flashpad")

    def save_as_file(self, event=None):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_widget.get(1.0, tk.END))
                self.current_file = file_path
                self.title(f"Flashpad - {file_path}")
                messagebox.showinfo("Save As", f"File saved successfully: {file_path}")

    def print_file(self, event=None):
        messagebox.showinfo("Print", "Print functionality is not yet implemented.")

    def increase_font_size(self, event=None):
        self.current_font_size += 2
        self.current_font.configure(size=self.current_font_size)

    def decrease_font_size(self, event=None):
        self.current_font_size -= 2
        self.current_font.configure(size=self.current_font_size)

    def reset_font_size(self, event=None):
        self.current_font_size = 12
        self.current_font.configure(size=self.current_font_size)

    def switch_theme(self, theme):
        self.theme = theme
        self.apply_theme()

    def show_about(self, event=None):
        messagebox.showinfo("About", "Flashpad - A simple text editor")

    def on_text_change(self, event=None):
        line_count = self.text_widget.index("end-1c").split(".")[0]
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        for i in range(1, int(line_count) + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state='disabled')

    def on_y_scroll(self, *args):
        self.text_widget.yview(*args)
        self.line_numbers.yview(*args)

    def undo(self, event=None):
        self.text_widget.event_generate("<<Undo>>")

    def redo(self, event=None):
        self.text_widget.event_generate("<<Redo>>")

    def cut(self, event=None):
        self.text_widget.event_generate("<<Cut>>")

    def copy(self, event=None):
        self.text_widget.event_generate("<<Copy>>")

    def paste(self, event=None):
        self.text_widget.event_generate("<<Paste>>")

if __name__ == "__main__":
    app = Flashpad()
    app.mainloop()
