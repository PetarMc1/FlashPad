import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as tkfont
import win32print
import win32ui
from PIL import Image, ImageTk
import requests
from io import BytesIO

class PrintDialog(tk.Toplevel):
    def __init__(self, parent, text_to_print):
        super().__init__(parent)
        self.title("Print Setup")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        self.text_to_print = text_to_print
        self.printer_name = None
        self.page_size = "A4"
        self.page_range = (1, 1)
        self.total_pages = 1  # Placeholder for total pages

        # Printer Selection (Dropdown)
        tk.Label(self, text="Select Printer:").pack(pady=5)
        self.printer_var = tk.StringVar()
        self.populate_printer_dropdown()

        self.printer_dropdown = tk.OptionMenu(self, self.printer_var, *self.printers)
        self.printer_dropdown.pack(pady=5)

        # Page Size Selection
        tk.Label(self, text="Page Size:").pack(pady=5)
        self.page_size_var = tk.StringVar(value=self.page_size)
        page_size_menu = tk.OptionMenu(self, self.page_size_var, "A4", "A3", "Letter", "Legal")
        page_size_menu.pack(pady=5)

        # Page Range Selection
        tk.Label(self, text=f"Page Range (1 to total pages or 'all'):\nTotal Pages: {self.total_pages}").pack(pady=5)
        self.page_range_entry = tk.Entry(self)
        self.page_range_entry.pack(pady=5)

        # Buttons
        tk.Button(self, text="Print", command=self.print_job).pack(pady=10)
        tk.Button(self, text="Cancel", command=self.cancel).pack(pady=5)

        # Update total pages
        self.update_page_info()

    def populate_printer_dropdown(self):
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        self.printers = [printer[2] for printer in printers]
        if self.printers:
            self.printer_var.set(self.printers[0])  # Set the first printer as default

    def update_page_info(self):
        # Simple estimation: assuming 1000 characters per page
        char_per_page = 1000
        total_chars = len(self.text_to_print)
        self.total_pages = (total_chars // char_per_page) + 1
        # Update label to show total pages
        self.children["!label"].config(text=f"Page Range (1 to {self.total_pages} or 'all'):\nTotal Pages: {self.total_pages}")

    def print_job(self):
        try:
            if self.printer_var.get():
                self.printer_name = self.printer_var.get()
                self.page_size = self.page_size_var.get()
                page_range_text = self.page_range_entry.get().strip().lower()
                if page_range_text == 'all':
                    self.page_range = (1, self.total_pages)
                else:
                    start, end = map(int, page_range_text.split('-'))
                    if 1 <= start <= end <= self.total_pages:
                        self.page_range = (start, end)
                    else:
                        raise ValueError("Page range is out of bounds")
                self.perform_print()
            else:
                messagebox.showerror("Print", "No printer selected.")
        except Exception as e:
            messagebox.showerror("Print", f"An error occurred: {e}")
        finally:
            self.destroy()

    def perform_print(self):
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            try:
                doc_name = "FlashPad Document"
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(self.printer_name)
                hdc.StartDoc(doc_name)
                hdc.StartPage()
                text = self.text_to_print
                # Handle printing based on page size and range
                for page_num in range(self.page_range[0], self.page_range[1] + 1):
                    start_index = (page_num - 1) * 1000
                    end_index = min(start_index + 1000, len(text))
                    page_text = text[start_index:end_index]
                    hdc.TextOut(100, 100, page_text)  # Print text at coordinates
                    if page_num < self.page_range[1]:
                        hdc.EndPage()
                        hdc.StartPage()
                hdc.EndPage()
                hdc.EndDoc()
                hdc.DeleteDC()
                messagebox.showinfo("Print", "Print job sent successfully.")
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            messagebox.showerror("Print", f"An error occurred while printing: {e}")

    def cancel(self):
        self.destroy()

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
        self.bind_all("<Control-p>", self.show_print_dialog)  # Ctrl + P
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
        self.file_menu.add_command(label="Save As...", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Print", command=self.show_print_dialog, accelerator="Ctrl + P")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl + Q")
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

        # Add View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)  # Light theme for View menu
        self.view_menu.add_command(label="Increase Font Size", command=self.increase_font_size, accelerator="Ctrl + =")
        self.view_menu.add_command(label="Decrease Font Size", command=self.decrease_font_size, accelerator="Ctrl + -")
        self.view_menu.add_command(label="Reset Font Size", command=self.reset_font_size, accelerator="Ctrl + 0")
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Switch Theme", command=self.switch_theme, accelerator="Ctrl + T")
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        # Add Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, bg='#f0f0f0', fg='black', bd=0)  # Light theme for Help menu
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="Version", command=self.show_version)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

    def finalize_setup(self):
        # Ensure the first line is shown on start
        self.text_widget.yview_moveto(0)

    def show_print_dialog(self, event=None):
        PrintDialog(self, self.text_widget.get(1.0, tk.END))

    def sync_scroll_y(self, *args):
        self.text_widget.yview(*args)
        self.line_numbers.yview(*args)

    def save_file(self, event=None):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_widget.get(1.0, tk.END))
        else:
            self.save_as_file()

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, content)
                self.current_file = file_path

    def save_as_file(self, event=None):
        file_path = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_widget.get(1.0, tk.END))
                self.current_file = file_path

    def new_file(self, event=None):
        response = messagebox.askyesno("New File", "Do you want to save changes to the current file?")
        if response:
            self.save_file()
        self.text_widget.delete(1.0, tk.END)
        self.current_file = None

    def switch_theme(self, event=None):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    def increase_font_size(self, event=None):
        self.current_font_size += 2
        self.current_font.config(size=self.current_font_size)
        self.text_widget.config(font=self.current_font)
        self.line_numbers.config(font=self.current_font)

    def decrease_font_size(self, event=None):
        if self.current_font_size > 6:
            self.current_font_size -= 2
            self.current_font.config(size=self.current_font_size)
            self.text_widget.config(font=self.current_font)
            self.line_numbers.config(font=self.current_font)

    def reset_font_size(self, event=None):
        self.current_font_size = 12
        self.current_font.config(size=self.current_font_size)
        self.text_widget.config(font=self.current_font)
        self.line_numbers.config(font=self.current_font)

    def on_text_change(self, event=None):
        self.update_line_numbers()

    def update_line_numbers(self):
        line_numbers = self.text_widget.index("end-1c").split(".")[0]
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        for i in range(1, int(line_numbers) + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state='disabled')

    def mouse_scroll(self, event):
        self.text_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

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

    def show_about(self):
        messagebox.showinfo("About FlashPad", "FlashPad - A simple text editor.")

    def show_version(self):
        messagebox.showinfo("Version", "FlashPad v1.1.0-alpha.2")

if __name__ == "__main__":
    app = FlashPad()
    app.mainloop()
