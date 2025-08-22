import tkinter as tk
from tkinter import ttk, filedialog
from config import ENCODERS, PRESETS, OUTPUT_FORMATS, ENCODING_PROFILES, THREAD_OPTIONS, COLOR_DEPTH_MODES, COLOR_DEPTH_DESCRIPTIONS

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
        row1.pack(fill=tk.X, pady=2)  # Reduzierter Abstand von 3 auf 2
        
        # Encoder
        ttk.Label(row1, text="Encoder:").pack(side=tk.LEFT)
        self.encoder_var = tk.StringVar()
        self.encoder_combo = ttk.Combobox(row1, textvariable=self.encoder_var, 
                                         values=list(ENCODERS.keys()), 
                                         state="readonly", width=20)
        self.encoder_combo.pack(side=tk.LEFT, padx=(5, 20))
        self.encoder_combo.bind('<<ComboboxSelected>>', self.on_encoder_change)
        
        # Preset
        ttk.Label(row1, text="Preset:").pack(side=tk.LEFT)
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(row1, textvariable=self.preset_var, 
                                        values=PRESETS, state="readonly", width=15)
        self.preset_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.preset_combo.bind('<<ComboboxSelected>>', self.on_preset_change)
        
        # Warnung für Hardware-Encoder
        self.warning_label = ttk.Label(row1, text="", foreground="orange")
        self.warning_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Zweite Zeile: CRF und Profile
        row2 = ttk.Frame(self)
        row2.pack(fill=tk.X, pady=2)  # Reduzierter Abstand von 3 auf 2
        
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
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_change)
        
        # Info über automatische Profil-Anpassung
        self.profile_info = ttk.Label(row2, text="", foreground="blue", font=("Arial", 8))
        self.profile_info.pack(side=tk.LEFT, padx=(10, 0))
        
        # Dritte Zeile: Ausgabeformat und Threads
        row3 = ttk.Frame(self)
        row3.pack(fill=tk.X, pady=2)  # Reduzierter Abstand von 3 auf 2
        
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
        row4.pack(fill=tk.X, pady=2)  # Reduzierter Abstand von 3 auf 2
        
        ttk.Label(row4, text="Ausgabe:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(row4, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(row4, text="Durchsuchen", command=self.browse_output_dir)
        browse_btn.pack(side=tk.LEFT)
        
        # Fünfte Zeile: Optionen
        row5 = ttk.Frame(self)
        row5.pack(fill=tk.X, pady=2)  # Reduzierter Abstand von 3 auf 2
        
        # Farbtiefe-Modus
        ttk.Label(row5, text="Farbtiefe:").pack(side=tk.LEFT)
        self.color_depth_var = tk.StringVar()
        self.color_depth_combo = ttk.Combobox(row5, textvariable=self.color_depth_var, 
                                             values=list(COLOR_DEPTH_MODES.keys()), 
                                             state="readonly", width=25)
        self.color_depth_combo.pack(side=tk.LEFT, padx=(5, 20))
        self.color_depth_combo.bind('<<ComboboxSelected>>', self.on_color_depth_change)
        
        # Farbtiefe-Beschreibung
        self.color_depth_desc = ttk.Label(row5, text="", foreground="blue", font=("Arial", 8))
        self.color_depth_desc.pack(side=tk.LEFT, padx=(0, 20))
        
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
    
    def update_profile_info(self):
        """Aktualisiert die Profil-Information"""
        profile = self.profile_var.get()
        
        if profile in ['baseline', 'main', 'high']:
            self.profile_info.config(text="⚠️ Wird bei 10-Bit Videos automatisch zu high10 angepasst")
        elif profile in ['high10', 'high422', 'high444']:
            self.profile_info.config(text="✅ Unterstützt 10-Bit Videos")
        else:
            self.profile_info.config(text="")
    
    def on_profile_change(self, event=None):
        """Wird aufgerufen, wenn sich das Profil ändert"""
        self.update_profile_info()
        self.update_preset_warning()
    
    def on_color_depth_change(self, event=None):
        """Wird aufgerufen, wenn sich der Farbtiefe-Modus ändert"""
        self.update_color_depth_description()
    
    def update_color_depth_description(self):
        """Aktualisiert die Farbtiefe-Beschreibung"""
        mode = self.color_depth_var.get()
        description = COLOR_DEPTH_DESCRIPTIONS.get(mode, "")
        self.color_depth_desc.config(text=description)
    
    def on_encoder_change(self, event=None):
        """Wird aufgerufen, wenn sich der Encoder ändert"""
        self.update_preset_warning()
    
    def on_preset_change(self, event=None):
        """Wird aufgerufen, wenn sich das Preset ändert"""
        self.update_preset_warning()
    
    def update_preset_warning(self):
        """Aktualisiert die Warnung für Hardware-Encoder"""
        encoder = self.encoder_var.get()
        preset = self.preset_var.get()
        
        if encoder == "h264_nvenc":
            if preset in ["veryslow", "slower", "slow"]:
                self.warning_label.config(text="→ slow", foreground="orange")
            elif preset in ["faster", "veryfast", "superfast", "ultrafast"]:
                self.warning_label.config(text="→ fast", foreground="orange")
            else:
                self.warning_label.config(text="→ medium", foreground="orange")
        elif encoder == "h264_amf":
            if preset in ["veryslow", "slower", "slow"]:
                self.warning_label.config(text="→ quality", foreground="orange")
            elif preset in ["faster", "veryfast", "superfast", "ultrafast"]:
                self.warning_label.config(text="→ speed", foreground="orange")
            else:
                self.warning_label.config(text="→ balanced", foreground="orange")
        elif encoder == "h264_qsv":
            if preset in ["veryslow", "slower", "slow"]:
                self.warning_label.config(text="→ slow", foreground="orange")
            elif preset in ["faster", "veryfast", "superfast", "ultrafast"]:
                self.warning_label.config(text="→ fast", foreground="orange")
            else:
                self.warning_label.config(text="→ medium", foreground="orange")
        else:
            self.warning_label.config(text="", foreground="orange")
    
    def set_available_encoders(self, available_encoders):
        """Setzt die verfügbaren Encoder basierend auf der tatsächlichen Verfügbarkeit"""
        current_encoder = self.encoder_var.get()
        
        # Aktualisiere die Encoder-Liste
        self.encoder_combo['values'] = available_encoders
        
        # Prüfe ob der aktuelle Encoder noch verfügbar ist
        if current_encoder not in available_encoders:
            if "libx264" in available_encoders:
                self.encoder_var.set("libx264")
                self.warning_label.config(text="⚠️ Hardware-Encoder nicht verfügbar", foreground="red")
            else:
                self.warning_label.config(text="⚠️ Keine Encoder verfügbar", foreground="red")
        else:
            self.warning_label.config(text="", foreground="orange")
        
        # Aktualisiere die Preset-Warnung
        self.update_preset_warning()
    
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
        self.color_depth_var.set(self.config.get("color_depth_mode", "auto"))
        
        # Aktualisiere die Preset-Warnung
        self.update_preset_warning()
        self.update_profile_info() # Aktualisiere die Profil-Info beim Laden
        self.update_color_depth_description() # Aktualisiere die Farbtiefe-Beschreibung beim Laden
    
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
        self.config.set("color_depth_mode", self.color_depth_var.get())
    
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
            'split_large_files': self.split_var.get(),
            'color_depth_mode': self.color_depth_var.get()
        }
