#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H.264 AVC Converter - H.265(HEVC) zu libx264
Ein Tool zur Konvertierung von Video-Dateien in das H.264/AVC Format
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
from pathlib import Path

# Importiere lokale Module
from config import Config, ENCODERS
from converter import VideoConverter
from gui.file_list import FileListFrame
from gui.settings_frame import SettingsFrame
from gui.log_frame import LogFrame

class H264ConverterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.config = Config()
        self.converter = None
        
        self.setup_main_window()
        self.setup_menu()
        self.setup_ui()
        self.setup_converter()
        
        # Prüfe FFmpeg
        self.check_ffmpeg()
    
    def setup_main_window(self):
        """Konfiguriert das Hauptfenster"""
        self.root.title("H.264 AVC Converter - H.265(HEVC) zu libx264")
        self.root.geometry("900x700")  # Kompaktere Größe
        self.root.minsize(700, 500)   # Kleinere Mindestgröße
        
        # Icon (falls vorhanden)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Styling
        style = ttk.Style()
        style.theme_use('clam')
    
    def setup_menu(self):
        """Erstellt die Menüleiste"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Dateien hinzufügen", command=self.add_files)
        file_menu.add_command(label="Ordner hinzufügen", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        
        # Einstellungen-Menü
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Einstellungen", menu=settings_menu)
        settings_menu.add_command(label="Konfiguration speichern", command=self.save_settings)
        settings_menu.add_command(label="Standardwerte wiederherstellen", command=self.reset_settings)
        
        # Hilfe-Menü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Über", command=self.show_about)
        help_menu.add_command(label="FFmpeg-Status", command=self.show_ffmpeg_status)
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Hauptframe
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Linke Seite: Dateiliste und Einstellungen
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Dateiliste
        self.file_list_frame = FileListFrame(left_frame)
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))  # Reduzierter Abstand von 10 auf 5
        
        # Einstellungen
        self.settings_frame = SettingsFrame(left_frame, self.config)
        self.settings_frame.pack(fill=tk.X, pady=(0, 5))  # Reduzierter Abstand von 10 auf 5
        
        # Konvertierungs-Buttons
        self.setup_conversion_buttons(left_frame)
        
        # Rechte Seite: Protokoll
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Protokoll
        self.log_frame = LogFrame(right_frame)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Statusleiste
        self.setup_status_bar()
    
    def setup_conversion_buttons(self, parent):
        """Erstellt die Konvertierungs-Buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start-Button
        self.start_btn = ttk.Button(button_frame, text="Konvertierung starten", 
                                   command=self.start_conversion, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Stopp-Button
        self.stop_btn = ttk.Button(button_frame, text="Konvertierung stoppen", 
                                  command=self.stop_conversion, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Einstellungen speichern
        save_btn = ttk.Button(button_frame, text="Einstellungen speichern", 
                             command=self.save_settings)
        save_btn.pack(side=tk.RIGHT)
    
    def setup_status_bar(self):
        """Erstellt die Statusleiste"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # FFmpeg-Status
        self.ffmpeg_status = ttk.Label(self.status_bar, text="FFmpeg: Wird geprüft...")
        self.ffmpeg_status.pack(side=tk.LEFT, padx=5)
        
        # Verfügbare Encoder
        self.encoder_status = ttk.Label(self.status_bar, text="Encoder: Wird geprüft...")
        self.encoder_status.pack(side=tk.LEFT, padx=5)
        
        # Version
        version_label = ttk.Label(self.status_bar, text="v1.0.0")
        version_label.pack(side=tk.RIGHT, padx=5)
    
    def setup_converter(self):
        """Initialisiert den Video-Konverter"""
        self.converter = VideoConverter(
            config=self.config,
            progress_callback=self.update_progress,
            log_callback=self.update_log
        )
    
    def check_ffmpeg(self):
        """Überprüft den FFmpeg-Status"""
        if self.converter.check_ffmpeg():
            self.ffmpeg_status.config(text="FFmpeg: Verfügbar", foreground="green")
            self.update_encoder_status()
        else:
            self.ffmpeg_status.config(text="FFmpeg: Nicht verfügbar", foreground="red")
            self.encoder_status.config(text="Encoder: FFmpeg erforderlich")
            self.log_frame.add_error("FFmpeg ist nicht installiert oder nicht im PATH verfügbar!")
    
    def update_encoder_status(self):
        """Aktualisiert den Encoder-Status"""
        available_encoders = self.converter.get_available_encoders()
        encoder_text = f"Encoder: {', '.join(available_encoders)}"
        self.encoder_status.config(text=encoder_text)
        
        # Aktualisiere die Encoder-Liste in den Einstellungen
        self.settings_frame.set_available_encoders(available_encoders)
        
        # Zeige Warnung wenn Hardware-Encoder nicht verfügbar sind
        if len(available_encoders) == 1 and "libx264" in available_encoders:
            self.log_frame.add_warning("Nur Software-Encoder verfügbar. Hardware-Encoder benötigen entsprechende Treiber.")
        elif len(available_encoders) > 1:
            self.log_frame.add_success(f"Hardware-Encoder verfügbar: {', '.join([e for e in available_encoders if e != 'libx264'])}")
    
    def add_files(self):
        """Öffnet den Datei-Dialog"""
        self.file_list_frame.add_files()
    
    def add_folder(self):
        """Öffnet den Ordner-Dialog"""
        self.file_list_frame.add_folder()
    
    def save_settings(self):
        """Speichert die aktuellen Einstellungen"""
        try:
            self.settings_frame.save_settings()
            self.log_frame.add_success("Einstellungen gespeichert")
        except Exception as e:
            self.log_frame.add_error(f"Fehler beim Speichern der Einstellungen: {str(e)}")
    
    def reset_settings(self):
        """Stellt die Standardeinstellungen wieder her"""
        if messagebox.askyesno("Bestätigung", "Möchten Sie wirklich alle Einstellungen auf Standardwerte zurücksetzen?"):
            # Lösche die Konfigurationsdatei
            try:
                if self.config.config_file.exists():
                    self.config.config_file.unlink()
                
                # Lade die Standardeinstellungen neu
                self.config = Config()
                self.settings_frame.config = self.config
                self.settings_frame.load_current_settings()
                
                self.log_frame.add_success("Einstellungen auf Standardwerte zurückgesetzt")
            except Exception as e:
                self.log_frame.add_error(f"Fehler beim Zurücksetzen der Einstellungen: {str(e)}")
    
    def start_conversion(self):
        """Startet die Konvertierung"""
        if not self.file_list_frame.has_files():
            messagebox.showwarning("Warnung", "Bitte fügen Sie zuerst Videodateien hinzu!")
            return
        
        if not self.converter.check_ffmpeg():
            messagebox.showerror("Fehler", "FFmpeg ist nicht verfügbar!")
            return
        
        # Hole die Konvertierungseinstellungen
        settings = self.settings_frame.get_conversion_settings()
        
        # Prüfe das Ausgabeverzeichnis
        if not settings['output_directory']:
            messagebox.showerror("Fehler", "Bitte wählen Sie ein Ausgabeverzeichnis aus!")
            return
        
        # Bestätigung
        file_count = len(self.file_list_frame.get_file_list())
        if not messagebox.askyesno("Bestätigung", 
                                 f"Möchten Sie {file_count} Datei(en) konvertieren?\n\n"
                                 f"Encoder: {settings['encoder']}\n"
                                 f"Preset: {settings['preset']}\n"
                                 f"CRF: {settings['crf']}\n"
                                 f"Ausgabe: {settings['output_format']}"):
            return
        
        # Starte die Konvertierung in einem separaten Thread
        self.log_frame.add_info("Konvertierung wird gestartet...")
        
        conversion_thread = threading.Thread(
            target=self.run_conversion,
            args=(settings,),
            daemon=True
        )
        conversion_thread.start()
        
        # Aktualisiere die UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
    
    def run_conversion(self, settings):
        """Führt die Konvertierung in einem separaten Thread aus"""
        try:
            file_list = self.file_list_frame.get_file_list()
            
            self.converter.convert_files(
                file_list=file_list,
                encoder=settings['encoder'],
                crf=settings['crf'],
                preset=settings['preset'],
                profile=settings['profile'],
                threads=settings['threads'],
                output_format=settings['output_format'],
                overwrite=settings['overwrite'],
                color_depth_mode=settings['color_depth_mode']
            )
            
        except Exception as e:
            self.log_frame.add_error(f"Fehler bei der Konvertierung: {str(e)}")
        
        finally:
            # Aktualisiere die UI im Hauptthread
            self.root.after(0, self.conversion_finished)
    
    def stop_conversion(self):
        """Stoppt die laufende Konvertierung"""
        if self.converter:
            self.converter.stop_conversion()
        
        self.log_frame.add_warning("Konvertierung wird gestoppt...")
    
    def conversion_finished(self):
        """Wird aufgerufen, wenn die Konvertierung beendet ist"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_frame.add_info("Konvertierung beendet")
    
    def update_progress(self, message):
        """Aktualisiert den Fortschritt"""
        self.log_frame.add_progress(message)
    
    def update_log(self, message):
        """Aktualisiert das Protokoll"""
        self.log_frame.add_info(message)
    
    def show_about(self):
        """Zeigt den Über-Dialog"""
        about_text = """H.264 AVC Converter v1.1.0

Ein Tool zur Konvertierung von H.265/HEVC Videos 
in das H.264/AVC Format für bessere Kompatibilität.

Features:
• Unterstützt alle gängigen Videoformate
• Hardware-Encoder (NVIDIA, AMD, Intel)
• Batch-Verarbeitung
• Automatische Optimierung großer Dateien
• Detailliertes Konvertierungsprotokoll
• Intelligente Farbtiefe-Auswahl
• QuickTime-Kompatibilität

Entwickelt mit Python und FFmpeg

Entwickler: Karsten Thiemann
GitHub: https://github.com/MrThiemann/h265"""
        
        messagebox.showinfo("Über", about_text)
    
    def show_ffmpeg_status(self):
        """Zeigt den FFmpeg-Status"""
        if self.converter.check_ffmpeg():
            available_encoders = self.converter.get_available_encoders()
            status_text = f"FFmpeg: Verfügbar\n\nVerfügbare Encoder:\n"
            for encoder in available_encoders:
                status_text += f"• {encoder}: {ENCODERS.get(encoder, 'Unbekannt')}\n"
        else:
            status_text = """FFmpeg: Nicht verfügbar

Bitte installieren Sie FFmpeg und stellen Sie sicher, 
dass es im System-PATH verfügbar ist.

Download: https://ffmpeg.org/download.html"""
        
        messagebox.showinfo("FFmpeg-Status", status_text)
    
    def run(self):
        """Startet die Anwendung"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nAnwendung wird beendet...")
        except Exception as e:
            print(f"Fehler: {str(e)}")

def main():
    """Hauptfunktion"""
    try:
        app = H264ConverterApp()
        app.run()
    except Exception as e:
        print(f"Kritischer Fehler: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
