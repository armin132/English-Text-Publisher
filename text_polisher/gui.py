from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .polisher import TextPolisher

class TextPolisherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('English Text Polisher')
        self.geometry('1260x760')
        self.minsize(1020, 660)
        self.colors = {
            'bg': '#f8f9fa',
            'panel': '#ffffff',
            'border': '#dadce0',
            'text': '#202124',
            'sub': '#5f6368',
            'primary': '#1a73e8',
            'primary_hover': '#1765cc',
            'soft': '#eef3fd',
            'soft_hover': '#e2ecfd',
            'output_bg': '#fbfdff',
            'badge': '#e8f0fe',
        }
        self.configure(bg=self.colors['bg'])
        self.polisher_mode = tk.StringVar(value='balanced')
        self.status = tk.StringVar(value='Ready')
        self.stats = tk.StringVar(value='Words: 0    Characters: 0')
        self.last_result = None
        self.current_file: Path | None = None
        self.setup_style()
        self.build_ui()
        self.bind_shortcuts()

    def setup_style(self):
        style = ttk.Style(self)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('.', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('App.TFrame', background=self.colors['bg'])
        style.configure('Panel.TFrame', background=self.colors['panel'])
        style.configure('Header.TLabel', background=self.colors['bg'], foreground=self.colors['text'], font=('Segoe UI Semibold', 12))
        style.configure('Muted.TLabel', background=self.colors['bg'], foreground=self.colors['sub'], font=('Segoe UI', 10))
        style.configure('PanelTitle.TLabel', background=self.colors['panel'], foreground=self.colors['text'], font=('Segoe UI Semibold', 11))
        style.configure('Lang.TButton', background=self.colors['panel'], foreground=self.colors['primary'], borderwidth=0, focuscolor=self.colors['panel'], padding=(14, 10))
        style.map('Lang.TButton', background=[('active', self.colors['soft'])], foreground=[('active', self.colors['primary'])])
        style.configure('Primary.TButton', background=self.colors['primary'], foreground='white', borderwidth=0, focuscolor=self.colors['primary'], padding=(14, 9))
        style.map('Primary.TButton', background=[('active', self.colors['primary_hover'])], foreground=[('active', 'white')])
        style.configure('Soft.TButton', background=self.colors['soft'], foreground=self.colors['primary'], borderwidth=0, focuscolor=self.colors['soft'], padding=(14, 9))
        style.map('Soft.TButton', background=[('active', self.colors['soft_hover'])], foreground=[('active', self.colors['primary'])])
        style.configure('Plain.TButton', background=self.colors['panel'], foreground=self.colors['sub'], borderwidth=0, focuscolor=self.colors['panel'], padding=(10, 8))
        style.map('Plain.TButton', background=[('active', self.colors['soft'])], foreground=[('active', self.colors['primary'])])
        style.configure('Mode.TCombobox', fieldbackground=self.colors['panel'], background=self.colors['panel'], foreground=self.colors['text'], arrowcolor=self.colors['sub'])
        style.configure('Stat.TLabel', background=self.colors['bg'], foreground=self.colors['sub'], font=('Segoe UI', 10))

    def build_ui(self):
        shell = ttk.Frame(self, style='App.TFrame', padding=18)
        shell.pack(fill='both', expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(2, weight=1)
        self.build_topbar(shell)
        self.build_language_bar(shell)
        self.build_workspace(shell)
        self.build_footer(shell)

    def build_topbar(self, parent):
        top = ttk.Frame(parent, style='App.TFrame')
        top.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        top.columnconfigure(0, weight=1)
        left = ttk.Frame(top, style='App.TFrame')
        left.grid(row=0, column=0, sticky='w')
        ttk.Label(left, text='English Text Polisher', style='Header.TLabel').pack(anchor='w')
        ttk.Label(left, text='Correct and polish English text locally with a clean two-panel editor', style='Muted.TLabel').pack(anchor='w', pady=(3, 0))
        right = ttk.Frame(top, style='App.TFrame')
        right.grid(row=0, column=1, sticky='e')
        ttk.Label(right, text='Mode', style='Muted.TLabel').pack(side='left', padx=(0, 8))
        self.mode_box = ttk.Combobox(right, textvariable=self.polisher_mode, values=('balanced', 'smooth'), state='readonly', width=10, style='Mode.TCombobox')
        self.mode_box.pack(side='left')

    def build_language_bar(self, parent):
        bar = ttk.Frame(parent, style='Panel.TFrame', padding=(14, 10))
        bar.grid(row=1, column=0, sticky='ew', pady=(0, 12))
        bar.columnconfigure(0, weight=1)
        bar.columnconfigure(1, weight=0)
        bar.columnconfigure(2, weight=1)
        left = ttk.Frame(bar, style='Panel.TFrame')
        left.grid(row=0, column=0, sticky='w')
        ttk.Button(left, text='English Input', style='Lang.TButton').pack(side='left')
        center = ttk.Frame(bar, style='Panel.TFrame')
        center.grid(row=0, column=1)
        ttk.Button(center, text='⇄', style='Plain.TButton', command=self.swap_texts).pack()
        right = ttk.Frame(bar, style='Panel.TFrame')
        right.grid(row=0, column=2, sticky='e')
        ttk.Button(right, text='Polished Output', style='Lang.TButton').pack(side='right')

    def build_workspace(self, parent):
        area = ttk.Frame(parent, style='App.TFrame')
        area.grid(row=2, column=0, sticky='nsew')
        area.columnconfigure(0, weight=1)
        area.columnconfigure(1, weight=1)
        area.rowconfigure(0, weight=1)
        self.build_left_panel(area)
        self.build_right_panel(area)

    def build_left_panel(self, parent):
        panel = ttk.Frame(parent, style='Panel.TFrame', padding=0)
        panel.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(panel, style='Panel.TFrame', padding=(14, 10))
        toolbar.grid(row=0, column=0, sticky='ew')
        toolbar.columnconfigure(0, weight=1)
        ttk.Label(toolbar, text='Original text', style='PanelTitle.TLabel').grid(row=0, column=0, sticky='w')
        action_box = ttk.Frame(toolbar, style='Panel.TFrame')
        action_box.grid(row=0, column=1, sticky='e')
        ttk.Button(action_box, text='Open', style='Plain.TButton', command=self.open_file).pack(side='left', padx=2)
        ttk.Button(action_box, text='Paste', style='Plain.TButton', command=self.paste_into_input).pack(side='left', padx=2)
        ttk.Button(action_box, text='Clear', style='Plain.TButton', command=self.clear_input).pack(side='left', padx=2)
        self.input_wrap = self.make_text_widget(panel, bg='#ffffff')
        self.input_wrap.grid(row=1, column=0, sticky='nsew', padx=1, pady=1)
        self.input_box().bind('<KeyRelease>', self.update_stats)
        bottom = ttk.Frame(panel, style='Panel.TFrame', padding=(14, 10))
        bottom.grid(row=2, column=0, sticky='ew')
        ttk.Label(bottom, text='Type text, paste content, or open a file.', style='Muted.TLabel').pack(side='left')

    def build_right_panel(self, parent):
        panel = ttk.Frame(parent, style='Panel.TFrame', padding=0)
        panel.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(panel, style='Panel.TFrame', padding=(14, 10))
        toolbar.grid(row=0, column=0, sticky='ew')
        toolbar.columnconfigure(0, weight=1)
        ttk.Label(toolbar, text='Corrected text', style='PanelTitle.TLabel').grid(row=0, column=0, sticky='w')
        action_box = ttk.Frame(toolbar, style='Panel.TFrame')
        action_box.grid(row=0, column=1, sticky='e')
        ttk.Button(action_box, text='Copy', style='Plain.TButton', command=self.copy_corrected).pack(side='left', padx=2)
        ttk.Button(action_box, text='Save', style='Plain.TButton', command=self.save_corrected).pack(side='left', padx=2)
        ttk.Button(action_box, text='Report', style='Plain.TButton', command=self.show_report).pack(side='left', padx=2)
        self.output_wrap = self.make_text_widget(panel, bg=self.colors['output_bg'])
        self.output_wrap.grid(row=1, column=0, sticky='nsew', padx=1, pady=1)
        footer = ttk.Frame(panel, style='Panel.TFrame', padding=(14, 10))
        footer.grid(row=2, column=0, sticky='ew')
        footer.columnconfigure(0, weight=1)
        left = ttk.Frame(footer, style='Panel.TFrame')
        left.grid(row=0, column=0, sticky='w')
        ttk.Button(left, text='Polish text', style='Primary.TButton', command=self.polish_text).pack(side='left')
        ttk.Button(left, text='Load sample', style='Soft.TButton', command=self.load_sample).pack(side='left', padx=(8, 0))
        right = ttk.Frame(footer, style='Panel.TFrame')
        right.grid(row=0, column=1, sticky='e')
        self.change_badge = tk.Label(right, text='0 changes', bg=self.colors['badge'], fg=self.colors['primary'], font=('Segoe UI Semibold', 10), padx=12, pady=6)
        self.change_badge.pack(side='left', padx=(0, 8))
        self.warn_badge = tk.Label(right, text='0 suggestions', bg=self.colors['badge'], fg=self.colors['primary'], font=('Segoe UI Semibold', 10), padx=12, pady=6)
        self.warn_badge.pack(side='left')

    def build_footer(self, parent):
        footer = ttk.Frame(parent, style='App.TFrame')
        footer.grid(row=3, column=0, sticky='ew', pady=(12, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status, style='Stat.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(footer, textvariable=self.stats, style='Stat.TLabel').grid(row=0, column=1, sticky='e')

    def make_text_widget(self, parent, bg='#ffffff'):
        wrapper = tk.Frame(parent, bg=self.colors['border'], highlightthickness=1, highlightbackground=self.colors['border'])
        wrapper.columnconfigure(0, weight=1)
        wrapper.rowconfigure(0, weight=1)
        text = tk.Text(wrapper, wrap='word', undo=True, font=('Segoe UI', 12), relief='flat', borderwidth=0, padx=14, pady=14, bg=bg, fg=self.colors['text'], insertbackground=self.colors['text'], selectbackground='#d2e3fc', spacing1=2, spacing3=2)
        text.grid(row=0, column=0, sticky='nsew')
        scroll = ttk.Scrollbar(wrapper, orient='vertical', command=text.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        text.configure(yscrollcommand=scroll.set)
        return wrapper

    def bind_shortcuts(self):
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-s>', lambda e: self.save_corrected())
        self.bind('<Control-Return>', lambda e: self.polish_text())
        self.bind('<Control-l>', lambda e: self.clear_input())

    def input_box(self):
        return self.input_wrap.winfo_children()[0]

    def output_box(self):
        return self.output_wrap.winfo_children()[0]

    def get_input(self):
        return self.input_box().get('1.0', 'end-1c')

    def set_output(self, value: str):
        box = self.output_box()
        box.delete('1.0', 'end')
        box.insert('1.0', value)

    def update_stats(self, event=None):
        text = self.get_input()
        words = len([w for w in text.split() if w.strip()])
        chars = len(text)
        self.stats.set(f'Words: {words}    Characters: {chars}')

    def open_file(self):
        path = filedialog.askopenfilename(title='Open text file', filetypes=[('Text files', '*.txt'), ('Markdown files', '*.md'), ('All files', '*.*')])
        if not path:
            return
        try:
            value = Path(path).read_text(encoding='utf-8')
        except UnicodeDecodeError:
            value = Path(path).read_text(errors='replace')
        box = self.input_box()
        box.delete('1.0', 'end')
        box.insert('1.0', value)
        self.current_file = Path(path)
        self.status.set(f'Opened {self.current_file.name}')
        self.update_stats()

    def paste_into_input(self):
        try:
            content = self.clipboard_get()
        except tk.TclError:
            content = ''
        if content:
            box = self.input_box()
            box.insert('insert', content)
            self.status.set('Pasted text from clipboard')
            self.update_stats()

    def clear_input(self):
        self.input_box().delete('1.0', 'end')
        self.status.set('Input cleared')
        self.update_stats()

    def save_corrected(self):
        text = self.output_box().get('1.0', 'end-1c')
        if not text.strip():
            messagebox.showwarning('Nothing to save', 'There is no corrected text to save yet.')
            return
        initial = 'corrected_text.txt' if not self.current_file else self.current_file.stem + '_corrected' + self.current_file.suffix
        path = filedialog.asksaveasfilename(title='Save corrected text', initialfile=initial, defaultextension='.txt', filetypes=[('Text files', '*.txt'), ('Markdown files', '*.md'), ('All files', '*.*')])
        if not path:
            return
        Path(path).write_text(text, encoding='utf-8')
        self.status.set(f'Saved {Path(path).name}')

    def copy_corrected(self):
        text = self.output_box().get('1.0', 'end-1c')
        if not text.strip():
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status.set('Corrected text copied to clipboard')

    def polish_text(self):
        text = self.get_input()
        if not text.strip():
            messagebox.showwarning('Empty text', 'Type or open some English text first.')
            return
        self.last_result = TextPolisher(mode=self.polisher_mode.get()).polish(text)
        self.set_output(self.last_result.corrected)
        self.change_badge.config(text=f"{len(self.last_result.edits)} changes")
        self.warn_badge.config(text=f"{len(self.last_result.warnings)} suggestions")
        self.status.set(f'Done. {len(self.last_result.edits)} changes found.')
        self.update_stats()

    def load_sample(self):
        sample = 'i recieve alot of informations about python ,and i think it is a useful tool\nthis is is a small project for writting better english\nan university can use this tool for simple text cleanup'
        box = self.input_box()
        box.delete('1.0', 'end')
        box.insert('1.0', sample)
        self.status.set('Loaded sample text')
        self.update_stats()

    def swap_texts(self):
        in_box = self.input_box()
        out_box = self.output_box()
        original = in_box.get('1.0', 'end-1c')
        corrected = out_box.get('1.0', 'end-1c')
        in_box.delete('1.0', 'end')
        in_box.insert('1.0', corrected)
        out_box.delete('1.0', 'end')
        out_box.insert('1.0', original)
        self.status.set('Swapped original and corrected text')
        self.update_stats()

    def show_report(self):
        if not self.last_result:
            messagebox.showinfo('No report', 'Polish some text first to generate a report.')
            return
        win = tk.Toplevel(self)
        win.title('Correction Report')
        win.geometry('820x560')
        win.configure(bg=self.colors['bg'])
        frame = tk.Frame(win, bg=self.colors['border'], highlightthickness=1, highlightbackground=self.colors['border'])
        frame.pack(fill='both', expand=True, padx=18, pady=18)
        text = tk.Text(frame, wrap='word', bg='#ffffff', fg=self.colors['text'], relief='flat', borderwidth=0, padx=16, pady=16, font=('Segoe UI', 11), insertbackground=self.colors['text'])
        text.pack(side='left', fill='both', expand=True)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        scroll.pack(side='right', fill='y')
        text.configure(yscrollcommand=scroll.set)
        lines = ['Correction report', '=' * 64, '', 'Corrected text:', self.last_result.corrected, '', 'Changes:']
        for i, edit in enumerate(self.last_result.edits, 1):
            lines.append(f'{i}. [{edit.kind}] {edit.before} -> {edit.after}')
            lines.append(f'   {edit.detail}')
        if self.last_result.warnings:
            lines.extend(['', 'Suggestions:'])
            for warning in self.last_result.warnings:
                lines.append(f'- {warning}')
        text.insert('1.0', '\n'.join(lines))
        text.configure(state='disabled')


def main():
    app = TextPolisherApp()
    app.mainloop()

if __name__ == '__main__':
    main()
