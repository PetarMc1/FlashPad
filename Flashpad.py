import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, simpledialog
import requests
from io import BytesIO
from PIL import Image, ImageTk
import win32print
import win32ui

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
                                   yscrollcommand=self.sync_scroll)
        self.text_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create the line numbers widget
        self.line_numbers = tk.Text(self.text_frame, width=4, padx=4, takefocus=0, border=0,
                                    state='disabled', font=self.current_font, bg=self.line_bg, fg=self.line_fg)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Configure the scrollbar to scroll both text widgets
        self.scrollbar_y.config(command=self.sync_scroll)

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
        self.bind_all("<Control-p>", self.print_file)  # Ctrl + P
        self.bind_all("<Control-equal>", self.increase_font_size)  # Ctrl + =
        self.bind_all("<Control-minus>", self.decrease_font_size)  # Ctrl + -
        self.bind_all("<Control-0>", self.reset_font_size)  # Ctrl + 0 (reset to default)

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
        self.menu_bar = tk.Menu(self, bg='#f0f0f0', fg='black', bd=0)  # Light theme for menu bar
        self.configure(menu=self.menu_bar)

        # Add File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)  # Light theme for File menu
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl + N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl + O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl + S")
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Print", command=self.print_file, accelerator="Ctrl + P")
        self.file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Add Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)  # Light theme for Edit menu
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl + Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl + Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl + X")
        self.edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl + C")
        self.edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl + V")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # Add View menu for zoom controls and theme switching
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)  # Light theme for View menu
        self.view_menu.add_command(label="Zoom In", command=self.increase_font_size, accelerator="Ctrl + =")
        self.view_menu.add_command(label="Zoom Out", command=self.decrease_font_size, accelerator="Ctrl + -")
        self.view_menu.add_command(label="Reset Zoom", command=self.reset_font_size, accelerator="Ctrl + 0")
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Switch to Light Theme", command=lambda: self.switch_theme("light"))
        self.view_menu.add_command(label="Switch to Dark Theme", command=lambda: self.switch_theme("dark"))
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        # Add Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)  # Light theme for Help menu
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="Version", command=self.show_version)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

    def finalize_setup(self):
        # Initialize theme after all widgets are created
        self.apply_theme()

    def apply_theme(self):
        # Apply the current theme colors
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

        # Update widget colors
        self.text_widget.config(bg=self.text_bg, fg=self.text_fg, insertbackground=self.cursor_color)
        self.line_numbers.config(bg=self.line_bg, fg=self.line_fg)
        self.scrollbar_y.config(bg=self.scrollbar_bg, troughcolor=self.scrollbar_bg)

    def sync_scroll(self, *args):
        # Sync scrolling between text widget and line numbers
        self.text_widget.yview(*args)
        self.line_numbers.yview(*args)

    def save_file(self, event=None):
        if hasattr(self, 'current_file') and self.current_file:
            response = messagebox.askyesno("Save", f"Do you want to save changes to {self.current_file}?")
            if response:
                with open(self.current_file, "w") as file:
                    file.write(self.text_widget.get(1.0, tk.END))
                    messagebox.showinfo("Save", f"File saved as {self.current_file}")
        else:
            self.save_as_file()

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, file.read())
                self.current_file = file_path
                self.title(f"FlashPad - {file_path}")

    def new_file(self, event=None):
        response = messagebox.askyesno("New File", "Do you want to save changes to the current file?")
        if response:
            self.save_file()
        self.text_widget.delete(1.0, tk.END)
        self.current_file = None
        self.title("FlashPad")

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_widget.get(1.0, tk.END))
                self.current_file = file_path
                self.title(f"FlashPad - {file_path}")

    def print_file(self, event=None):
        print_settings = tk.Toplevel(self)
        print_settings.title("Print Settings")
        print_settings.geometry("300x200")

        def print_action():
            printer_name = printer_var.get()
            print("Selected Printer:", printer_name)

            # Get the text to be printed
            text_to_print = self.text_widget.get(1.0, tk.END)

            try:
                printer_info = win32print.GetPrinter(win32print.OpenPrinter(printer_name), 2)
                hPrinter = win32ui.CreateDC()
                hPrinter.CreatePrinterDC(printer_name)
                hPrinter.StartDoc("FlashPad Print Job")
                hPrinter.StartPage()
                hPrinter.DrawText(text_to_print, (0, 0, 1000, 1000), win32ui.DT_LEFT)
                hPrinter.EndPage()
                hPrinter.EndDoc()
                hPrinter.DeleteDC()
                messagebox.showinfo("Print", "Document sent to printer.")
            except Exception as e:
                messagebox.showerror("Print Error", f"Failed to print document: {e}")

            print_settings.destroy()

        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        printer_names = [printer[2] for printer in printers]

        tk.Label(print_settings, text="Select Printer:").pack(pady=10)
        printer_var = tk.StringVar(value=printer_names[0])
        tk.OptionMenu(print_settings, printer_var, *printer_names).pack(pady=10)
        tk.Button(print_settings, text="Print", command=print_action).pack(pady=20)

    def switch_theme(self, theme):
        self.theme = theme
        self.apply_theme()

    def increase_font_size(self, event=None):
        self.current_font_size += 2
        self.current_font.config(size=self.current_font_size)

    def decrease_font_size(self, event=None):
        if self.current_font_size > 8:  # Minimum font size to avoid too small text
            self.current_font_size -= 2
            self.current_font.config(size=self.current_font_size)

    def reset_font_size(self, event=None):
        self.current_font_size = 12
        self.current_font.config(size=self.current_font_size)

    def on_text_change(self, event=None):
        self.update_line_numbers()

    def update_line_numbers(self):
        line_numbers = ""
        for i in range(1, int(self.text_widget.index('end').split('.')[0]) + 1):
            line_numbers += f"{i}\n"
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(tk.END, line_numbers)
        self.line_numbers.config(state='disabled')

    def mouse_scroll(self, event):
        self.text_widget.yview_scroll(-1 * int((event.delta / 120)), "units")
        self.line_numbers.yview_scroll(-1 * int((event.delta / 120)), "units")
        return "break"

    def show_about(self):
        messagebox.showinfo("About", "FlashPad - A simple text editor.")

    def show_version(self):
        messagebox.showinfo("Version", "v1.1.0-alpha.1")

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

if __name__ == "__main__":
    app = FlashPad()
    app.mainloop()
