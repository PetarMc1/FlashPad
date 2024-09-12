import tkinter as tk
from tkinter import messagebox, filedialog
import win32print
import win32ui
import win32con
from io import BytesIO
import requests
from PIL import Image, ImageTk, ImageWin
import tkinter.font as tkfont

class FlashPad(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set the window title and size
        self.title("FlashPad")
        self.geometry("800x600")

        # Load and set the window icon from a URL
        icon_url = 'https://cdn.458011.xyz/flashpad/icon.ico'
        self.set_icon_from_url(icon_url)

        # Initialize font and theme variables
        self.current_font_size = 12
        self.current_font = tkfont.Font(family="Consolas", size=self.current_font_size)
        self.current_file = None  # Track the currently opened file

        # Default dark theme
        self.text_bg = '#1e1e1e'
        self.text_fg = 'white'
        self.cursor_color = 'white'
        self.line_bg = '#2d2d2d'
        self.line_fg = 'white'
        self.scrollbar_bg = '#2d2d2d'
        self.scrollbar_fg = 'white'
        self.theme = "dark"

        # Create the menu bar
        self.create_menu_bar()

        # Create the frame for the text widget and scrollbars
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create the frame for line numbers and text widget
        self.text_frame = tk.Frame(self.main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        # Create a vertical scrollbar
        self.scrollbar_y = tk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the text widget
        self.text_widget = tk.Text(self.text_frame, undo=True, wrap=tk.NONE, font=self.current_font,
                                   bg=self.text_bg, fg=self.text_fg, insertbackground=self.cursor_color,
                                   yscrollcommand=self.sync_scroll_y)
        self.text_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create the line numbers widget
        self.line_numbers = tk.Text(self.text_frame, width=4, padx=4, takefocus=0, border=0,
                                    state='disabled', font=self.current_font, bg=self.line_bg, fg=self.line_fg)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Configure the scrollbar to scroll both text widgets
        self.scrollbar_y.config(command=self.sync_scroll_y)

        # Bind events for updating line numbers
        self.text_widget.bind("<<Modified>>", self.on_text_change)
        self.text_widget.bind("<KeyRelease>", self.on_text_change)
        self.text_widget.bind("<ButtonRelease-1>", self.on_text_change)

        # Bind mouse scrolling to both widgets
        self.text_widget.bind("<MouseWheel>", self.mouse_scroll)
        self.line_numbers.bind("<MouseWheel>", self.mouse_scroll)

        # Bind keyboard shortcuts for font resizing and common actions
        self.bind_all("<Control-s>", self.save_file)  # Ctrl + S
        self.bind_all("<Control-o>", self.open_file)  # Ctrl + O
        self.bind_all("<Control-n>", self.new_file)  # Ctrl + N
        self.bind_all("<Control-equal>", self.increase_font_size)  # Ctrl + =
        self.bind_all("<Control-minus>", self.decrease_font_size)  # Ctrl + -
        self.bind_all("<Control-0>", self.reset_font_size)  # Ctrl + 0 (reset to default)
        self.bind_all("<Control-p>", self.show_print_dialog)  # Ctrl + P (Print dialog)

        # Ensure the first line is shown on start
        self.text_widget.yview_moveto(0)

        # Finalize setup
        self.finalize_setup()

    def set_icon_from_url(self, url):
        try:
            response = requests.get(url)
            image_data = BytesIO(response.content)
            icon_image = Image.open(image_data)
            self.iconphoto(True, ImageTk.PhotoImage(icon_image))
        except Exception as e:
            print(f"Error loading icon from URL: {e}")

    def create_menu_bar(self):
        # Create a menu bar and add it to the window
        self.menu_bar = tk.Menu(self, bg='white', fg='black', bd=0)  # Light theme for menu bar
        self.configure(menu=self.menu_bar)

        # Add File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg='white', fg='black', bd=0)  # Light theme for File menu
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl + N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl + O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl + S")
        self.file_menu.add_command(label="Save As...", command=self.save_as_file)
        self.file_menu.add_command(label="Print", command=self.show_print_dialog, accelerator="Ctrl + P")  # Print option
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl + Q")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Add Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg='white', fg='black', bd=0)  # Light theme for Edit menu
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl + Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl + Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl + X")
        self.edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl + C")
        self.edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl + V")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # Add View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0, bg='white', fg='black', bd=0)  # Light theme for View menu
        self.view_menu.add_command(label="Increase Font Size", command=self.increase_font_size, accelerator="Ctrl + =")
        self.view_menu.add_command(label="Decrease Font Size", command=self.decrease_font_size, accelerator="Ctrl + -")
        self.view_menu.add_command(label="Reset Font Size", command=self.reset_font_size, accelerator="Ctrl + 0")
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Switch Theme", command=self.switch_theme, accelerator="Ctrl + T")
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        # Add Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, bg='white', fg='black', bd=0)  # Light theme for Help menu
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="Version", command=self.show_version)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

    def finalize_setup(self):
        # Ensure the first line is shown on start
        self.text_widget.yview_moveto(0)

    def new_file(self, event=None):
        if self.text_widget.get("1.0", tk.END).strip():
            if messagebox.askyesno("Save Changes", "Do you want to save changes to the current file?"):
                self.save_file()
        self.text_widget.delete("1.0", tk.END)
        self.current_file = None

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, content)
            self.current_file = file_path

    def save_file(self, event=None):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_widget.get("1.0", tk.END))
        else:
            self.save_as_file()

    def save_as_file(self, event=None):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_widget.get("1.0", tk.END))
            self.current_file = file_path

    def undo(self, event=None):
        self.text_widget.edit_undo()

    def redo(self, event=None):
        self.text_widget.edit_redo()

    def cut(self, event=None):
        self.text_widget.event_generate("<<Cut>>")

    def copy(self, event=None):
        self.text_widget.event_generate("<<Copy>>")

    def paste(self, event=None):
        self.text_widget.event_generate("<<Paste>>")

    def increase_font_size(self, event=None):
        self.current_font_size += 2
        self.current_font.config(size=self.current_font_size)

    def decrease_font_size(self, event=None):
        if self.current_font_size > 2:
            self.current_font_size -= 2
            self.current_font.config(size=self.current_font_size)

    def reset_font_size(self, event=None):
        self.current_font_size = 12
        self.current_font.config(size=self.current_font_size)

    def switch_theme(self, event=None):
        if self.theme == "dark":
            self.text_bg = 'white'
            self.text_fg = 'black'
            self.cursor_color = 'black'
            self.line_bg = '#f0f0f0'
            self.line_fg = 'black'
            self.scrollbar_bg = '#f0f0f0'
            self.scrollbar_fg = 'black'
            self.theme = "light"
        else:
            self.text_bg = '#1e1e1e'
            self.text_fg = 'white'
            self.cursor_color = 'white'
            self.line_bg = '#2d2d2d'
            self.line_fg = 'white'
            self.scrollbar_bg = '#2d2d2d'
            self.scrollbar_fg = 'white'
            self.theme = "dark"
        self.text_widget.config(bg=self.text_bg, fg=self.text_fg, insertbackground=self.cursor_color)
        self.line_numbers.config(bg=self.line_bg, fg=self.line_fg)
        self.scrollbar_y.config(bg=self.scrollbar_bg, troughcolor=self.scrollbar_bg, sliderrelief='flat', sliderbackground=self.scrollbar_fg)
        self.text_widget.update_idletasks()

    def show_print_dialog(self, event=None):
        print_dialog = tk.Toplevel(self)
        print_dialog.title("Print")
        self.center_dialog(print_dialog)
        print_dialog.configure(bg='white')

        tk.Label(print_dialog, text="Printer:", bg='white').pack(pady=5)
        self.printer_var = tk.StringVar(value=win32print.GetDefaultPrinter())
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
        tk.OptionMenu(print_dialog, self.printer_var, *printers).pack(pady=5)

        tk.Label(print_dialog, text="Number of Copies:", bg='white').pack(pady=5)
        self.copies_var = tk.IntVar(value=1)
        tk.Spinbox(print_dialog, from_=1, to=100, textvariable=self.copies_var, width=5).pack(pady=5)

        tk.Label(print_dialog, text="Page Size:", bg='white').pack(pady=5)
        self.page_size_var = tk.StringVar(value="A4")
        tk.OptionMenu(print_dialog, self.page_size_var, "A4", "A3").pack(pady=5)

        tk.Label(print_dialog, text="Print Range:", bg='white').pack(pady=5)
        self.range_var = tk.StringVar(value="All")
        range_menu = tk.OptionMenu(print_dialog, self.range_var, "All", "Custom")
        range_menu.pack(pady=5)

        self.custom_range_frame = tk.Frame(print_dialog, bg='white')
        self.custom_range_frame.pack(pady=5)
        tk.Label(self.custom_range_frame, text="From Page:", bg='white').pack(side=tk.LEFT, padx=5)
        self.from_page_var = tk.IntVar(value=1)
        self.from_page_entry = tk.Spinbox(self.custom_range_frame, from_=1, to=1000, textvariable=self.from_page_var, width=5)
        self.from_page_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(self.custom_range_frame, text="To Page:", bg='white').pack(side=tk.LEFT, padx=5)
        self.to_page_var = tk.IntVar(value=1)
        self.to_page_entry = tk.Spinbox(self.custom_range_frame, from_=1, to=1000, textvariable=self.to_page_var, width=5)
        self.to_page_entry.pack(side=tk.LEFT, padx=5)
        self.custom_range_frame.pack_forget()

        # Bind the range menu to update the frame visibility
        range_menu.bind("<Configure>", self.update_range_frame)

        button_frame = tk.Frame(print_dialog, bg='white')
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Print", command=self.print_text, relief=tk.RAISED, bg='lightgrey', fg='black', padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=print_dialog.destroy, relief=tk.RAISED, bg='lightgrey', fg='black', padx=10, pady=5).pack(side=tk.LEFT, padx=5)

    def update_range_frame(self, event=None):
        if self.range_var.get() == "Custom":
            self.custom_range_frame.pack(pady=5)
        else:
            self.custom_range_frame.pack_forget()

    def center_dialog(self, dialog):
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def print_text(self):
        # Implement the actual printing functionality here
        print("Printing...")
        # Access the selected printer, copies, page size, and print range
        printer = self.printer_var.get()
        copies = self.copies_var.get()
        page_size = self.page_size_var.get()
        print_range = self.range_var.get()
        from_page = self.from_page_var.get()
        to_page = self.to_page_var.get()
        print(f"Printer: {printer}, Copies: {copies}, Page Size: {page_size}, Print Range: {print_range} (From: {from_page}, To: {to_page})")

    def sync_scroll_y(self, *args):
        self.text_widget.yview(*args)
        self.line_numbers.yview(*args)

    def on_text_change(self, *args):
        self.update_line_numbers()
        self.text_widget.edit_modified(False)

    def update_line_numbers(self):
        line_numbers = "\n".join(str(i) for i in range(1, int(self.text_widget.index('end-1c').split('.')[0]) + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert(tk.END, line_numbers)
        self.line_numbers.config(state='disabled')

    def mouse_scroll(self, event):
        if event.num == 5 or event.delta == -120:  # Scroll down
            self.text_widget.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:  # Scroll up
            self.text_widget.yview_scroll(-1, "units")

    def show_about(self):
        messagebox.showinfo("About FlashPad", "FlashPad v1.0\nA simple text editor built.")

    def show_version(self):
        messagebox.showinfo("Version", "FlashPad v1.1.0-beta.1")

if __name__ == "__main__":
    app = FlashPad()
    app.mainloop()
