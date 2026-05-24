# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import ImageTk
import os

from engine import TOOL_CONFIGS, render_chars_to_pages

class RegisterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Acrobat Writer Multi-Page Workspace")
        self.root.geometry("1300x800")
        
        self.paper_paths = {
            "Register Page": "assets/register_bg.png",
            "Blank A4 Paper": "assets/blank_a4_bg.png"
        }
        
        # Documents memory states tracking array
        self.generated_pages_stream = [] 
        self.thumbnail_images_cache = [] # Prevents Garbage Collection cleanup deletion bugs
        self.selected_viewing_page_idx = 0
        
        self.setup_ui()
        self.apply_to_register() # Build page 1 view placeholder on initialize load

    def setup_ui(self):
        # 3-Panel system: Left (Editor), Middle (Big Preview), Right (Thumbnails Stream)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- LEFT PANEL: TEXT EDITOR ---
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=3)
        
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        marker_btn = ttk.Button(toolbar, text="🖍️ Set Selection to Marker (Bold)", command=self.apply_marker_format)
        marker_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(toolbar, text="🖊️ Reset Selection to Pen (Plain)", command=self.clear_marker_format)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.text_editor = tk.Text(left_frame, wrap=tk.WORD, font=("Courier", 14), spacing3=6, insertbackground='black')
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        self.text_editor.tag_configure("bold_marker", font=("Courier", 14, "bold"), foreground="#060E37")
        self.text_editor.focus_set()
        
        button_bar = ttk.Frame(left_frame)
        button_bar.pack(fill=tk.X, pady=(5, 0))
        
        apply_btn = ttk.Button(button_bar, text="⚡ Apply to Canvas", command=self.apply_to_register)
        apply_btn.pack(side=tk.RIGHT, padx=5)
        
        save_btn = ttk.Button(button_bar, text="💾 Save as Multi-Page PDF", command=self.save_as_pdf)
        save_btn.pack(side=tk.RIGHT, padx=5)

        # --- MIDDLE PANEL: BIG CANVAS VIEW ---
        middle_frame = ttk.LabelFrame(main_paned, text=" Active Page View ")
        main_paned.add(middle_frame, weight=4)
        
        # Dropdown paper profile switcher inside active views header
        paper_selection_bar = ttk.Frame(middle_frame)
        paper_selection_bar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(paper_selection_bar, text="Paper:").pack(side=tk.LEFT, padx=2)
        self.paper_selector = ttk.Combobox(paper_selection_bar, values=list(self.paper_paths.keys()), state="readonly", width=15)
        self.paper_selector.set("Register Page")
        self.paper_selector.pack(side=tk.LEFT, padx=5)
        self.paper_selector.bind("<<ComboboxSelected>>", lambda event: self.apply_to_register())
        
        # View status tracking banner
        self.status_lbl = ttk.Label(paper_selection_bar, text="Page 1 of 1", font=("Arial", 10, "bold"))
        self.status_lbl.pack(side=tk.RIGHT, padx=10)

        self.big_preview_label = ttk.Label(middle_frame, anchor=tk.CENTER)
        self.big_preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- RIGHT PANEL: VERTICAL THUMBNAILS BAR ---
        right_frame = ttk.LabelFrame(main_paned, text=" Pages ")
        main_paned.add(right_frame, weight=1)
        
        # Scrollable container canvas layout setup
        self.thumb_canvas = tk.Canvas(right_frame, width=130, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        
        self.thumb_scroll_content = ttk.Frame(self.thumb_canvas)
        self.thumb_scroll_content.bind(
            "<Configure>", 
            lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))
        )
        
        self.thumb_canvas.create_window((0, 0), window=self.thumb_scroll_content, anchor="nw")
        self.thumb_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def apply_marker_format(self):
        try: self.text_editor.tag_add("bold_marker", "sel.first", "sel.last")
        except tk.TclError: pass

    def clear_marker_format(self):
        try: self.text_editor.tag_remove("bold_marker", "sel.first", "sel.last")
        except tk.TclError: pass

    def apply_to_register(self, reset_to_last_page=False):
        """Compiles standard streams and populates the view system dynamically."""
        end_index = self.text_editor.index("end - 1 chars")
        current_index = "1.0"
        
        structured_chars = []
        while self.text_editor.compare(current_index, "<", end_index):
            char = self.text_editor.get(current_index)
            tags = self.text_editor.tag_names(current_index)
            is_bold = "bold_marker" in tags
            structured_chars.append((char, is_bold))
            current_index = self.text_editor.index(f"{current_index} + 1 chars")

        selected_paper_name = self.paper_selector.get()
        chosen_bg_path = self.paper_paths[selected_paper_name]

        try:
            # Query backend engine data mapping
            self.generated_pages_stream = render_chars_to_pages(chosen_bg_path, structured_chars)
            
            # If the user just added text that created a new page, automatically jump to show that page
            if reset_to_last_page or self.selected_viewing_page_idx >= len(self.generated_pages_stream):
                self.selected_viewing_page_idx = len(self.generated_pages_stream) - 1
                
            self.refresh_thumbnails_sidebar()
            self.switch_active_preview_page(self.selected_viewing_page_idx)
            
        except Exception as e:
            messagebox.showerror("Execution Fault", f"An unexpected rendering error occurred:\n{str(e)}")

    def switch_active_preview_page(self, page_index):
        """Swaps the main container image viewer frame focus."""
        if 0 <= page_index < len(self.generated_pages_stream):
            self.selected_viewing_page_idx = page_index
            target_img = self.generated_pages_stream[page_index]
            
            # Update center preview panel resolution looks
            display_img = target_img.copy()
            display_img.thumbnail((550, 680))
            
            self.main_preview_photo = ImageTk.PhotoImage(display_img)
            self.big_preview_label.configure(image=self.main_preview_photo)
            
            # Update counter banner string metric indices display values
            self.status_lbl.configure(text=f"Page {page_index + 1} of {len(self.generated_pages_stream)}")

    def refresh_thumbnails_sidebar(self):
        """Clears and redraws the small preview button widgets in the right sidebar panel."""
        for widget in self.thumb_scroll_content.winfo_children():
            widget.destroy()
            
        self.thumbnail_images_cache.clear()
        
        for idx, page_img in enumerate(self.generated_pages_stream):
            thumb_img = page_img.copy()
            thumb_img.thumbnail((90, 120)) # Small mini compact snapshot size footprints
            
            photo_tk = ImageTk.PhotoImage(thumb_img)
            self.thumbnail_images_cache.append(photo_tk) # Lock pointer in memory safe registers
            
            # Interactive container row allocation block framework layout structures
            row_frame = ttk.Frame(self.thumb_scroll_content, padding=4)
            row_frame.pack(fill=tk.X, pady=4)
            
            # Clickable thumbnail image button
            btn = tk.Button(
                row_frame, 
                image=photo_tk, 
                command=lambda p_idx=idx: self.switch_active_preview_page(p_idx),
                relief=tk.FLAT,
                bd=1,
                highlightbackground="#cccccc"
            )
            btn.pack()
            
            lbl = ttk.Label(row_frame, text=f"Page {idx + 1}", font=("Arial", 8))
            lbl.pack(pady=2)

    def save_as_pdf(self):
        if not self.generated_pages_stream:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Save Multi-Page Document"
        )
        
        if file_path:
            try:
                # Convert all PIL pages to RGB format
                rgb_pages = [img.convert('RGB') for img in self.generated_pages_stream]
                
                # Use PIL's built-in multi-page PDF compilation feature
                primary_sheet = rgb_pages[0]
                append_sheets = rgb_pages[1:] if len(rgb_pages) > 1 else []
                
                primary_sheet.save(
                    file_path, 
                    "PDF", 
                    resolution=100.0, 
                    save_all=True, 
                    append_images=append_sheets
                )
                messagebox.showinfo("Success", f"All {len(rgb_pages)} pages saved successfully to PDF!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed compiling document structures:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegisterApp(root)
    # Set a small keyboard shortcut so hitting Ctrl+Enter automatically clicks apply
    root.bind("<Control-Return>", lambda e: app.apply_to_register(reset_to_last_page=True))
    root.mainloop()