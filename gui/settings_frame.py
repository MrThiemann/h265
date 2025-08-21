import tkinter as tk
from tkinter import ttk, filedialog
from config import ENCODERS, PRESETS, OUTPUT_FORMATS, ENCODING_PROFILES, THREAD_OPTIONS

class SettingsFrame(ttk.LabelFrame):
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, text="Konvertierungseinstellungen", **kwargs)
        self.config = config
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Erste Zeile: Encoder und Preset
        row1 = ttk.Frame(self)
        row1.pack(fill=tk.X, pady=5)
        
        # Encoder
        ttk.Label(row1, text="Encoder:").pack(side=tk.LEFT)
        self.encoder_var = tk.StringVar()
        self.encoder_combo = ttk.Combobox(row1, textvariable=self.encoder_var, 
                                         values=list(ENCODERS.keys()), 
                                         state="readonly", width=20)
        self.encoder_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Preset
        ttk.Label(row1, text="Preset:").pack(side=tk.LEFT)
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(row1, textvariable=self.preset_var, 
                                        values=PRESETS, state="readonly", width=15)
        self.preset_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Zweite Zeile: CRF und Profile
        row2 = ttk.Frame(self)
        row2.pack(fill=tk.X, pady=5)
        
        # CRF
        ttk.Label(row2, text="CRF (0-51):").pack(side=tk.LEFT)
        self.crf_var = tk.IntVar()
        self.crf_scale = ttk.Scale(row2, from_=0, to=51, variable=self.crf_var, 
                                  orient=tk.HORIZONTAL, length=150)
        self.crf_scale.pack(side=tk.LEFT, padx=(5, 10))
        self.crf_label = ttk.Label(row2, text="23")
        self.crf_label.pack(side=tk.LEFT)
        self.crf_scale.config(command=self.update_crf_label)
        
        # Profile
        ttk.Label(row2, text="Profil:").pack(side=tk.LEFT, padx=(20, 0))
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(row2, textvariable=self.profile_var, 
                                         values=ENCODING_PROFILES, state="readonly", width=15)
        self.profile_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Dritte Zeile: Ausgabeformat und Threads
        row3 = ttk.Frame(self)
        row3.pack(fill=tk.X, pady=5)
        
        # Ausgabeformat
        ttk.Label(row3, text="Ausgabe:").pack(side=tk.LEFT)
        self.output_format_var = tk.StringVar()
        self.output_format_combo = ttk.Combobox(row3, textvariable=self.output_format_var, 
                                               values=OUTPUT_FORMATS, state="readonly", width=10)
        self.output_format_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Threads
        ttk.Label(row3, text="Threads:").pack(side=tk.LEFT)
        self.threads_var = tk.StringVar()
        self.threads_combo = ttk.Combobox(row3, textvariable=self.threads_var, 
                                         values=THREAD_OPTIONS, state="readonly", width=10)
        self.threads_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Vierte Zeile: Ausgabeverzeichnis
        row4 = ttk.Frame(self)
        row4.pack(fill=tk.X, pady=5)
        
        ttk.Label(row4, text="Ausgabe:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(row4, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(row4, text="Durchsuchen", command=self.browse_output_dir)
        browse_btn.pack(side=tk.LEFT)
        
        # Fünfte Zeile: Optionen
        row5 = ttk.Frame(self)
        row5.pack(fill=tk.X, pady=5)
        
        # Überschreiben
        self.overwrite_var = tk.BooleanVar()
        overwrite_check = ttk.Checkbutton(row5, text="Existierende Dateien überschreiben", 
                                        variable=self.overwrite_var)
        overwrite_check.pack(side=tk.LEFT)
        
        # Große Dateien optimieren
        self.optimize_var = tk.BooleanVar()
        optimize_check = ttk.Checkbutton(row5, text="Große Dateien automatisch optimieren", 
                                       variable=self.optimize_var)
        optimize_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # Große Dateien teilen
        self.split_var = tk.BooleanVar()
        split_check = ttk.Checkbutton(row5, text="Sehr große Dateien teilen", 
                                    variable=self.split_var)
        split_check.pack(side=tk.LEFT, padx=(20, 0))
    
    def update_crf_label(self, value):
        """Aktualisiert das CRF-Label"""
        self.crf_label.config(text=str(int(float(value))))
    
    def browse_output_dir(self):
        """Öffnet den Ordner-Dialog für das Ausgabeverzeichnis"""
        directory = filedialog.askdirectory(title="Ausgabeverzeichnis auswählen")
        if directory:
            self.output_dir_var.set(directory)
    
    def load_current_settings(self):
        """Lädt die aktuellen Einstellungen aus der Konfiguration"""
        self.encoder_var.set(self.config.get("default_encoder", "libx264"))
        self.preset_var.set(self.config.get("default_preset", "medium"))
        self.crf_var.set(self.config.get("default_crf", 23))
        self.profile_var.set(self.config.get("default_profile", "high"))
        self.output_format_var.set(self.config.get("default_output_format", "MP4"))
        self.threads_var.set(self.config.get("max_threads", "Auto"))
        self.output_dir_var.set(self.config.get("output_directory", ""))
        self.overwrite_var.set(self.config.get("overwrite_files", False))
        self.optimize_var.set(self.config.get("auto_optimize_large_files", True))
        self.split_var.set(self.config.get("split_large_files", True))
    
    def save_settings(self):
        """Speichert die aktuellen Einstellungen in der Konfiguration"""
        self.config.set("default_encoder", self.encoder_var.get())
        self.config.set("default_preset", self.preset_var.get())
        self.config.set("default_crf", self.crf_var.get())
        self.config.set("default_profile", self.profile_var.get())
        self.config.set("default_output_format", self.output_format_var.get())
        self.config.set("max_threads", self.threads_var.get())
        self.config.set("output_directory", self.output_dir_var.get())
        self.config.set("overwrite_files", self.overwrite_var.get())
        self.config.set("auto_optimize_large_files", self.optimize_var.get())
        self.config.set("split_large_files", self.split_var.get())
    
    def get_conversion_settings(self):
        """Gibt die aktuellen Konvertierungseinstellungen zurück"""
        return {
            'encoder': self.encoder_var.get(),
            'preset': self.preset_var.get(),
            'crf': self.crf_var.get(),
            'profile': self.profile_var.get(),
            'output_format': self.output_format_var.get(),
            'threads': self.threads_var.get(),
            'output_directory': self.output_dir_var.get(),
            'overwrite': self.overwrite_var.get(),
            'optimize_large_files': self.optimize_var.get(),
            'split_large_files': self.split_var.get()
        }
