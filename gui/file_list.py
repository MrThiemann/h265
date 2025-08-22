import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os
from config import INPUT_FORMATS

class FileListFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.file_list = []
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Titel
        title_label = ttk.Label(self, text="Videodateien", font=("Arial", 10, "bold"))
        title_label.pack(pady=(0, 3))
        
        # Dateiliste
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 3))
        
        # Scrollbar für die Liste
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox für Dateien
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                      selectmode=tk.EXTENDED, height=2)  # Sehr kompakte Höhe
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Buttons in einer Reihe
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(0, 3))
        
        # Einzelne Dateien hinzufügen
        add_files_btn = ttk.Button(button_frame, text="Dateien hinzufügen", 
                                  command=self.add_files)
        add_files_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Ordner hinzufügen
        add_folder_btn = ttk.Button(button_frame, text="Ordner hinzufügen", 
                                   command=self.add_folder)
        add_folder_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Dateien entfernen
        remove_btn = ttk.Button(button_frame, text="Entfernen", 
                               command=self.remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Liste leeren
        clear_btn = ttk.Button(button_frame, text="Liste leeren", 
                              command=self.clear_list)
        clear_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_label = ttk.Label(self, text="Keine Dateien ausgewählt", font=("Arial", 8))
        self.status_label.pack()
    
    def add_files(self):
        """Fügt einzelne Videodateien hinzu"""
        filetypes = [("Video-Dateien", "*" + ext) for ext in INPUT_FORMATS]
        filetypes.append(("Alle Dateien", "*.*"))
        
        files = filedialog.askopenfilenames(
            title="Videodateien auswählen",
            filetypes=filetypes
        )
        
        if files:
            for file_path in files:
                self.add_file(file_path)
    
    def add_folder(self):
        """Fügt alle Videodateien aus einem Ordner hinzu"""
        folder = filedialog.askdirectory(title="Ordner auswählen")
        
        if folder:
            video_files = []
            for ext in INPUT_FORMATS:
                video_files.extend(Path(folder).glob(f"*{ext}"))
                video_files.extend(Path(folder).glob(f"*{ext.upper()}"))
            
            if video_files:
                for file_path in video_files:
                    self.add_file(str(file_path))
            else:
                messagebox.showinfo("Info", "Keine Videodateien im ausgewählten Ordner gefunden.")
    
    def add_file(self, file_path):
        """Fügt eine einzelne Datei zur Liste hinzu"""
        if file_path not in [f['path'] for f in self.file_list]:
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': self.get_file_size(file_path)
            }
            
            self.file_list.append(file_info)
            self.file_listbox.insert(tk.END, f"{file_info['name']} ({file_info['size']})")
            self.update_status()
    
    def remove_selected(self):
        """Entfernt ausgewählte Dateien aus der Liste"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Bitte wählen Sie Dateien zum Entfernen aus.")
            return
        
        # Entferne in umgekehrter Reihenfolge (damit sich die Indizes nicht ändern)
        for index in reversed(selection):
            self.file_list.pop(index)
            self.file_listbox.delete(index)
        
        self.update_status()
    
    def clear_list(self):
        """Leert die gesamte Dateiliste"""
        if self.file_list:
            if messagebox.askyesno("Bestätigung", "Möchten Sie wirklich alle Dateien aus der Liste entfernen?"):
                self.file_list.clear()
                self.file_listbox.delete(0, tk.END)
                self.update_status()
    
    def get_file_size(self, file_path):
        """Ermittelt die Dateigröße in lesbarer Form"""
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
        except:
            return "Unbekannt"
    
    def update_status(self):
        """Aktualisiert den Status-Text"""
        count = len(self.file_list)
        if count == 0:
            self.status_label.config(text="Keine Dateien ausgewählt")
        elif count == 1:
            self.status_label.config(text="1 Datei ausgewählt")
        else:
            self.status_label.config(text=f"{count} Dateien ausgewählt")
    
    def get_file_list(self):
        """Gibt die aktuelle Dateiliste zurück"""
        return self.file_list.copy()
    
    def has_files(self):
        """Prüft, ob Dateien in der Liste sind"""
        return len(self.file_list) > 0
