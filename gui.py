# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import ImageTk
import os

from engine import render_chars_to_pages

class RegisterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Premium High-Speed Writer Workspace")
        self.root.geometry("1400x900") 
        
        self.paper_paths = {
            "Register Page": "assets/register_bg.png",
            "Blank A4 Paper": "assets/blank_a4_bg.png"
        }
        
        self.generated_pages_stream = [] 
        self.page_offsets = [0] 
        self.thumbnail_images_cache = [] 
        self.selected_viewing_page_idx = 0
        
        self.setup_ui()
        self.trigger_canvas_render() # Initial render

    def setup_ui(self):
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- LEFT PANEL (TEXT EDITOR WITH TOP TOOLBAR) ---
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1) 
        
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Tools packed to the left
        ttk.Button(toolbar, text="🖍️ Marker", command=self.apply_marker_format).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🖊️ Pen", command=self.clear_marker_format).pack(side=tk.LEFT, padx=2)
        
        self.btn_apply = tk.Button(toolbar, text="⚡ Apply", font=("Arial", 9, "bold"), bg="#0078d7", fg="white", activebackground="#005a9e", activeforeground="white", padx=6, command=self.trigger_canvas_render)
        self.btn_apply.pack(side=tk.LEFT, padx=5)
        
        # --- ADDED: Reminder text typed right next to the Apply button ---
        self.reminder_lbl = ttk.Label(
            toolbar, 
            text="Always click apply for the changes to appear!", 
            font=("Arial", 9, "italic"), 
            foreground="#a02020"
        )
        self.reminder_lbl.pack(side=tk.LEFT, padx=5)
        
        # Save PDF button at the top-right corner of the editor panel
        ttk.Button(toolbar, text="💾 Save PDF", command=self.save_as_pdf).pack(side=tk.RIGHT, padx=2)
        
        # Text input container matching margins exactly
        editor_scroll_container = ttk.Frame(left_frame)
        editor_scroll_container.pack(fill=tk.Y, side=tk.LEFT, expand=False)

        self.text_editor = tk.Text(
            editor_scroll_container, 
            wrap=tk.WORD, 
            font=("Courier", 14), 
            spacing3=8, 
            insertbackground='black',
            undo=True,          
            maxundo=100,        
            autoseparators=True,
            width=58,
            padx=20,
            pady=15
        )
        self.text_editor.pack(fill=tk.Y, side=tk.LEFT, expand=False)
        self.text_editor.tag_configure("bold_marker", font=("Courier", 14, "bold"), foreground="#060E37")
        self.text_editor.focus_set()
        
        text_scroll = ttk.Scrollbar(editor_scroll_container, orient=tk.VERTICAL, command=self.text_editor.yview)
        self.text_editor.configure(yscrollcommand=text_scroll.set)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_editor.bind("<Control-z>", self.handle_undo)
        self.text_editor.bind("<Control-y>", self.handle_redo)
        self.text_editor.bind("<Command-z>", self.handle_undo)
        self.text_editor.bind("<Command-Shift-Z>", self.handle_redo)
        self.text_editor.bind("<Command-y>", self.handle_redo)

        # --- MIDDLE PANEL (ACTIVE PAGE PREVIEW) ---
        middle_frame = ttk.LabelFrame(main_paned, text=" Active Page View ")
        main_paned.add(middle_frame, weight=6) 
        
        self.preview_container = ttk.Frame(middle_frame)
        self.preview_container.pack(fill=tk.BOTH, expand=True)
        
        paper_selection_bar = ttk.Frame(self.preview_container)
        paper_selection_bar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(paper_selection_bar, text="Paper:").pack(side=tk.LEFT, padx=2)
        
        self.paper_selector = ttk.Combobox(paper_selection_bar, values=list(self.paper_paths.keys()), state="readonly", width=15)
        self.paper_selector.set("Register Page")
        self.paper_selector.pack(side=tk.LEFT, padx=5)
        self.paper_selector.bind("<<ComboboxSelected>>", lambda event: self.trigger_canvas_render())
        
        self.status_lbl = ttk.Label(paper_selection_bar, text="Page 1 of 1", font=("Arial", 10, "bold"))
        self.status_lbl.pack(side=tk.RIGHT, padx=10)

        self.view_stack = ttk.Frame(self.preview_container)
        self.view_stack.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.big_preview_label = ttk.Label(self.view_stack, anchor=tk.CENTER)
        self.big_preview_label.pack(fill=tk.BOTH, expand=True)

        self.overlay_layer = tk.Frame(self.view_stack, bg="#ffffff")
        self.spinner_canvas = tk.Canvas(self.overlay_layer, width=180, height=100, bg="#ffffff", highlightthickness=0)
        self.spinner_canvas.pack(expand=True)
        
        # --- RIGHT PANEL (PAGES LIST THUMBNAILS WITH FIXES) ---
        right_frame = ttk.LabelFrame(main_paned, text=" Pages ")
        main_paned.add(right_frame, weight=1)
        
        self.thumb_canvas = tk.Canvas(right_frame, width=130, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_scroll_content = ttk.Frame(self.thumb_canvas)
        self.thumb_scroll_content.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        self.thumb_canvas.create_window((0, 0), window=self.thumb_scroll_content, anchor="nw")
        self.thumb_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.thumb_canvas.bind_all("<MouseWheel>", self.on_mousewheel_scroll) 
        self.thumb_canvas.bind_all("<Button-4>", self.on_mousewheel_scroll)  
        self.thumb_canvas.bind_all("<Button-5>", self.on_mousewheel_scroll)  

    def on_mousewheel_scroll(self, event):
        x, y = self.root.winfo_pointerxy()
        widget_under_mouse = self.root.winfo_containing(x, y)
        
        if widget_under_mouse and (str(widget_under_mouse).startswith(str(self.thumb_canvas)) or "thumb" in str(widget_under_mouse)):
            if event.num == 4:    
                self.thumb_canvas.yview_scroll(-1, "units")
            elif event.num == 5:  
                self.thumb_canvas.yview_scroll(1, "units")
            else:                 
                self.thumb_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def handle_undo(self, event=None):
        try: self.text_editor.edit_undo()
        except tk.TclError: pass 
        return "break" 

    def handle_redo(self, event=None):
        try: self.text_editor.edit_redo()
        except tk.TclError: pass 
        return "break"

    def show_processing_spinner(self):
        self.overlay_layer.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        self.spinner_canvas.delete("all")
        self.spinner_canvas.create_arc(70, 15, 110, 55, start=0, extent=280, width=4, outline="#0078d7", style=tk.ARC, tags="spinner")
        self.spinner_canvas.create_text(90, 80, text="Rendering Canvas...", font=("Arial", 11, "bold"), fill="#555555")
        self.rotate_spinner_angle(0)

    def rotate_spinner_angle(self, angle):
        if self.overlay_layer.winfo_viewable():
            self.spinner_canvas.delete("spinner")
            self.spinner_canvas.create_arc(70, 15, 110, 55, start=angle, extent=280, width=4, outline="#0078d7", style=tk.ARC, tags="spinner")
            self.root.after(40, lambda: self.rotate_spinner_angle((angle + 15) % 360))

    def hide_processing_spinner(self):
        self.overlay_layer.place_forget()

    def apply_marker_format(self):
        if not self.text_editor.tag_ranges("sel"):
            messagebox.showwarning("Selection Required", "Please select some text first!")
            return
        try: self.text_editor.tag_add("bold_marker", "sel.first", "sel.last")
        except tk.TclError: pass

    def clear_marker_format(self):
        if not self.text_editor.tag_ranges("sel"):
            messagebox.showwarning("Selection Required", "Please select some text first!")
            return
        try: self.text_editor.tag_remove("bold_marker", "sel.first", "sel.last")
        except tk.TclError: pass

    def trigger_canvas_render(self):
        self.show_processing_spinner()
        
        raw_text = self.text_editor.get("1.0", "end - 1 chars")
        raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        
        if not raw_text:
            structured_chars = []
        else:
            is_bold_array = [False] * len(raw_text)
            tag_ranges = self.text_editor.tag_ranges("bold_marker")
            for i in range(0, len(tag_ranges), 2):
                start_offset = len(self.text_editor.get("1.0", tag_ranges[i]))
                end_offset = len(self.text_editor.get("1.0", tag_ranges[i+1]))
                for idx in range(start_offset, end_offset):
                    if idx < len(is_bold_array):
                        is_bold_array[idx] = True
            
            structured_chars = [(char, False if char == '\n' else is_bold_array[idx]) for idx, char in enumerate(raw_text)]

        selected_paper_name = self.paper_selector.get()
        chosen_bg_path = self.paper_paths[selected_paper_name]
        engine_paper_tag = "a4" if "A4" in selected_paper_name else "register"

        try:
            self.generated_pages_stream, self.page_offsets = render_chars_to_pages(chosen_bg_path, structured_chars, paper_type=engine_paper_tag)
            
            # Force the view index to stick onto the very first page
            self.selected_viewing_page_idx = 0
                
            self.refresh_thumbnails_sidebar()
            self.switch_active_preview_page(self.selected_viewing_page_idx, auto_scroll_text=False)
        except Exception as e:
            print(f"Render Error: {e}")
        finally:
            self.root.after(150, self.hide_processing_spinner)

    def switch_active_preview_page(self, page_index, auto_scroll_text=True):
        if 0 <= page_index < len(self.generated_pages_stream):
            self.selected_viewing_page_idx = page_index
            display_img = self.generated_pages_stream[page_index].copy()
            
            # Scaled constraints safely to 500x720 to show whole image perfectly
            display_img.thumbnail((500, 720))
            
            self.main_preview_photo = ImageTk.PhotoImage(display_img)
            self.big_preview_label.configure(image=self.main_preview_photo)
            self.status_lbl.configure(text=f"Page {page_index + 1} of {len(self.generated_pages_stream)}")
            
            if auto_scroll_text and page_index < len(self.page_offsets):
                char_offset = self.page_offsets[page_index]
                target_tk_index = f"1.0 + {char_offset} chars"
                self.text_editor.see(target_tk_index)
                self.text_editor.mark_set("insert", target_tk_index)

    def refresh_thumbnails_sidebar(self):
        for widget in self.thumb_scroll_content.winfo_children():
            widget.destroy()
        self.thumbnail_images_cache.clear()
        
        for idx, page_img in enumerate(self.generated_pages_stream):
            thumb_img = page_img.copy()
            thumb_img.thumbnail((90, 120))
            photo_tk = ImageTk.PhotoImage(thumb_img)
            self.thumbnail_images_cache.append(photo_tk)
            
            row_frame = ttk.Frame(self.thumb_scroll_content, padding=4)
            row_frame.pack(fill=tk.X, pady=4)
            
            border_color = "#0078d7" if idx == self.selected_viewing_page_idx else "#cccccc"
            btn = tk.Button(row_frame, image=photo_tk, command=lambda p_idx=idx: self.switch_active_preview_page(p_idx, auto_scroll_text=True), relief=tk.FLAT, bd=1, highlightbackground=border_color)
            btn.pack()
            ttk.Label(row_frame, text=f"Page {idx + 1}", font=("Arial", 8)).pack(pady=2)

    def save_as_pdf(self):
        if not self.generated_pages_stream: return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")], title="Save Multi-Page Document")
        if file_path:
            try:
                rgb_pages = [img.convert('RGB') for img in self.generated_pages_stream]
                rgb_pages[0].save(file_path, "PDF", resolution=100.0, save_all=True, append_images=rgb_pages[1:])
                messagebox.showinfo("Success", f"All {len(rgb_pages)} pages saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed compiling document: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegisterApp(root)
    root.mainloop()