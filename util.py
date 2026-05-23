import tkinter as tk
from typing import Optional


class Tooltip:
    OFFSET_X: int = 20
    OFFSET_Y: int = 5
    MARGIN: int = 10
    
    def __init__(self, widget: tk.Widget, hover_text: str = "", delay: int = 100) -> None:
        self.widget: tk.Widget = widget
        self.hover_text: str = hover_text
        self.delay: int = delay
        
        self.tip_window: Optional[tk.Toplevel] = None
        self.tip_id: Optional[str] = None
        
        self._alive: bool = True
        
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<ButtonPress>", self._on_leave)
        
        self._bind_scroll_events(widget)
    
    def _bind_scroll_events(self, widget: tk.Widget) -> None:
        parent: Optional[tk.Widget] = widget.master # pyright: ignore[reportAssignmentType]
        while parent:
            if isinstance(parent, (tk.Canvas, tk.Text, tk.Listbox)):
                parent.bind("<MouseWheel>", self._on_scroll, add=True)
                parent.bind("<Button-4>", self._on_scroll, add=True)
                parent.bind("<Button-5>", self._on_scroll, add=True)
            parent = parent.master # pyright: ignore[reportAssignmentType]
    
    def _on_enter(self, event: Optional[tk.Event] = None) -> None:
        if not self._alive or not self.hover_text:
            return
        
        self._cancel_timer()
        self.tip_id = self.widget.after(self.delay, self._show_tip)
    
    def _on_leave(self, event: Optional[tk.Event] = None) -> None:
        if not self._alive:
            return
        
        self._hide_tip()
    
    def _on_scroll(self, event: Optional[tk.Event] = None) -> None:
        if self.tip_window:
            self._hide_tip()
    
    def _cancel_timer(self) -> None:
        if self.tip_id:
            try:
                self.widget.after_cancel(self.tip_id)
            except:
                pass
            self.tip_id = None
    
    def _hide_tip(self) -> None:
        self._cancel_timer()
        
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except tk.TclError:
                pass
            finally:
                self.tip_window = None
    
    def _show_tip(self) -> None:
        if not self._alive or self.tip_window or not self.hover_text:
            return
        
        try:
            root_x: int = self.widget.winfo_rootx()
            root_y: int = self.widget.winfo_rooty()
            widget_width: int = self.widget.winfo_width()
            widget_height: int = self.widget.winfo_height()
        except tk.TclError:
            return
        
        x: int = root_x + self.OFFSET_X
        y: int = root_y + widget_height + self.OFFSET_Y
        
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        
        frame: tk.Frame = tk.Frame(self.tip_window, relief="solid", borderwidth=1, bg="#ffffe0")
        frame.pack()
        
        label: tk.Label = tk.Label(
            frame,
            text=self.hover_text,
            justify="left",
            relief="flat",
            padx=4,
            pady=2,
            bg="#ffffe0"
        )
        label.pack()
        
        screen_width: int = self._get_screen_width(x, y)
        screen_height: int = self._get_screen_height(x, y)
        
        self.tip_window.update_idletasks()
        tip_width: int = self.tip_window.winfo_width()
        tip_height: int = self.tip_window.winfo_height()
        
        if x + tip_width > screen_width:
            x = screen_width - tip_width - self.MARGIN
        
        if y + tip_height > screen_height:
            y = root_y - tip_height - self.OFFSET_Y
            if y < 0:
                y = screen_height - tip_height - self.MARGIN
        
        if x < self.MARGIN:
            x = self.MARGIN
        
        if y < self.MARGIN:
            y = self.MARGIN
        
        self.tip_window.wm_geometry(f"+{int(x)}+{int(y)}")
    
    def _get_screen_width(self, x: int, y: int) -> int:
        try:
            return self.tip_window.winfo_screenwidth() # pyright: ignore[reportOptionalMemberAccess]
        except:
            root: tk.Tk = self.widget.winfo_toplevel() # pyright: ignore[reportAssignmentType]
            return root.winfo_screenwidth()
    
    def _get_screen_height(self, x: int, y: int) -> int:
        try:
            return self.tip_window.winfo_screenheight() # pyright: ignore[reportOptionalMemberAccess]
        except:
            root: tk.Tk = self.widget.winfo_toplevel() # pyright: ignore[reportAssignmentType]
            return root.winfo_screenheight()
    
    def config(self, hover_text: Optional[str] = None, delay: Optional[int] = None) -> None:
        if hover_text is not None:
            self.hover_text = hover_text
        
        if delay is not None:
            self.delay = delay
        
        if self.tip_window and self.tip_window.winfo_exists():
            self._hide_tip()
            self._on_enter()
    
    def destroy(self) -> None:
        self._alive = False
        self._hide_tip()
        
        try:
            self.widget.unbind("<Enter>")
            self.widget.unbind("<Leave>")
            self.widget.unbind("<ButtonPress>")
        except:
            pass
    
    def __del__(self) -> None:
        self.destroy()