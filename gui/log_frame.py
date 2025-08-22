import tkinter as tk
from tkinter import ttk, scrolledtext
import time

class LogFrame(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="Konvertierungsprotokoll", **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Log-Textbereich
        self.log_text = scrolledtext.ScrolledText(self, height=8, width=80,  # Reduzierte Höhe von 10 auf 8
                                                wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button-Frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Log leeren
        clear_btn = ttk.Button(button_frame, text="Protokoll leeren", 
                              command=self.clear_log)
        clear_btn.pack(side=tk.LEFT)
        
        # In Datei speichern
        save_btn = ttk.Button(button_frame, text="Als Datei speichern", 
                             command=self.save_log)
        save_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status-Label
        self.status_label = ttk.Label(button_frame, text="Bereit")
        self.status_label.pack(side=tk.RIGHT)
    
    def add_log_entry(self, message: str, level: str = "INFO"):
        """Fügt einen neuen Log-Eintrag hinzu"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Aktiviere den Textbereich zum Bearbeiten
        self.log_text.config(state=tk.NORMAL)
        
        # Füge die Nachricht hinzu
        self.log_text.insert(tk.END, formatted_message)
        
        # Scrolle zum Ende
        self.log_text.see(tk.END)
        
        # Deaktiviere den Textbereich wieder
        self.log_text.config(state=tk.DISABLED)
        
        # Aktualisiere den Status
        self.update_status(message)
    
    def add_info(self, message: str):
        """Fügt eine Info-Nachricht hinzu"""
        self.add_log_entry(message, "INFO")
    
    def add_warning(self, message: str):
        """Fügt eine Warnung hinzu"""
        self.add_log_entry(message, "WARNUNG")
    
    def add_error(self, message: str):
        """Fügt eine Fehlermeldung hinzu"""
        self.add_log_entry(message, "FEHLER")
    
    def add_success(self, message: str):
        """Fügt eine Erfolgsmeldung hinzu"""
        self.add_log_entry(message, "ERFOLG")
    
    def add_progress(self, message: str):
        """Fügt eine Fortschrittsmeldung hinzu"""
        self.add_log_entry(message, "FORTSCHRITT")
    
    def clear_log(self):
        """Leert das Protokoll"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.status_label.config(text="Protokoll geleert")
    
    def save_log(self):
        """Speichert das Protokoll in eine Datei"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="Protokoll speichern",
                defaultextension=".txt",
                filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                
                self.add_info(f"Protokoll gespeichert: {filename}")
        except Exception as e:
            self.add_error(f"Fehler beim Speichern des Protokolls: {str(e)}")
    
    def update_status(self, message: str):
        """Aktualisiert den Status-Text"""
        # Kürze lange Nachrichten
        if len(message) > 50:
            status_text = message[:47] + "..."
        else:
            status_text = message
        
        self.status_label.config(text=status_text)
    
    def get_log_content(self) -> str:
        """Gibt den aktuellen Protokollinhalt zurück"""
        return self.log_text.get(1.0, tk.END)
    
    def set_status(self, status: str):
        """Setzt den Status-Text direkt"""
        self.status_label.config(text=status)
