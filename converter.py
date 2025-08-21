import subprocess
import os
import time
import threading
from pathlib import Path
from typing import List, Dict, Callable
import json

class VideoConverter:
    def __init__(self, config, progress_callback=None, log_callback=None):
        self.config = config
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.is_converting = False
        self.current_job = None
        
    def log(self, message: str):
        """Sendet eine Log-Nachricht an den Callback"""
        if self.log_callback:
            self.log_callback(message)
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def check_ffmpeg(self) -> bool:
        """Überprüft, ob FFmpeg installiert ist"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def get_file_size_mb(self, file_path: str) -> float:
        """Ermittelt die Dateigröße in MB"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except:
            return 0
    
    def should_split_file(self, file_path: str) -> bool:
        """Ermittelt, ob eine Datei geteilt werden sollte"""
        size_gb = self.get_file_size_mb(file_path) / 1024
        return size_gb > self.config.get("extra_large_file_threshold_gb", 1)
    
    def should_optimize_file(self, file_path: str) -> bool:
        """Ermittelt, ob eine Datei optimiert werden sollte"""
        size_mb = self.get_file_size_mb(file_path)
        return size_mb > self.config.get("large_file_threshold_mb", 500)
    
    def build_ffmpeg_command(self, input_file: str, output_file: str, 
                           encoder: str, crf: int, preset: str, 
                           profile: str, threads: str) -> List[str]:
        """Baut den FFmpeg-Befehl zusammen"""
        cmd = ['ffmpeg', '-i', input_file, '-y']  # -y überschreibt existierende Dateien
        
        # Encoder-spezifische Parameter
        if encoder == "libx264":
            cmd.extend(['-c:v', 'libx264'])
        elif encoder == "h264_nvenc":
            cmd.extend(['-c:v', 'h264_nvenc'])
        elif encoder == "h264_amf":
            cmd.extend(['-c:v', 'h264_amf'])
        elif encoder == "h264_qsv":
            cmd.extend(['-c:v', 'h264_qsv'])
        
        # Qualität und Geschwindigkeit
        cmd.extend(['-crf', str(crf), '-preset', preset])
        
        # Encoding-Profil
        cmd.extend(['-profile:v', profile])
        
        # Threading
        if threads != "Auto":
            if threads == "Max":
                cmd.extend(['-threads', '0'])  # 0 = alle verfügbaren Threads
            else:
                cmd.extend(['-threads', threads])
        
        # Audio-Codec (Kopie)
        cmd.extend(['-c:a', 'copy'])
        
        # Große Datei-Optimierung
        if self.should_optimize_file(input_file):
            self.log(f"Optimiere große Datei: {os.path.basename(input_file)}")
            cmd.extend(['-max_muxing_queue_size', '1024'])
        
        # Ausgabedatei
        cmd.append(output_file)
        
        return cmd
    
    def convert_single_file(self, input_file: str, output_file: str, 
                          encoder: str, crf: int, preset: str, 
                          profile: str, threads: str) -> bool:
        """Konvertiert eine einzelne Datei"""
        try:
            # Erstelle Ausgabeverzeichnis
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Baue FFmpeg-Befehl
            cmd = self.build_ffmpeg_command(input_file, output_file, encoder, 
                                          crf, preset, profile, threads)
            
            self.log(f"Starte Konvertierung: {os.path.basename(input_file)}")
            self.log(f"Befehl: {' '.join(cmd)}")
            
            # Führe FFmpeg aus
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            
            # Überwache den Prozess
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Hier könnte man den Fortschritt parsen
                    if self.progress_callback:
                        self.progress_callback(output)
            
            # Warte auf Beendigung
            return_code = process.wait()
            
            if return_code == 0:
                self.log(f"Konvertierung erfolgreich: {os.path.basename(output_file)}")
                return True
            else:
                self.log(f"Fehler bei der Konvertierung: {os.path.basename(input_file)}")
                return False
                
        except Exception as e:
            self.log(f"Fehler: {str(e)}")
            return False
    
    def convert_files(self, file_list: List[Dict], encoder: str, crf: int, 
                     preset: str, profile: str, threads: str, 
                     output_format: str, overwrite: bool = False):
        """Konvertiert mehrere Dateien"""
        if self.is_converting:
            self.log("Konvertierung läuft bereits!")
            return
        
        self.is_converting = True
        total_files = len(file_list)
        successful = 0
        
        try:
            for i, file_info in enumerate(file_list):
                if not self.is_converting:  # Abbruch
                    break
                
                input_file = file_info['path']
                filename = os.path.splitext(os.path.basename(input_file))[0]
                
                # Bestimme Ausgabedatei
                output_filename = f"{filename}_H264.{output_format.lower()}"
                output_file = os.path.join(self.config.get("output_directory"), output_filename)
                
                # Prüfe, ob Datei bereits existiert
                if os.path.exists(output_file) and not overwrite:
                    self.log(f"Überspringe existierende Datei: {output_filename}")
                    continue
                
                # Konvertiere Datei
                if self.convert_single_file(input_file, output_file, encoder, 
                                          crf, preset, profile, threads):
                    successful += 1
                
                # Fortschritt
                progress = ((i + 1) / total_files) * 100
                if self.progress_callback:
                    self.progress_callback(f"Fortschritt: {progress:.1f}% ({i+1}/{total_files})")
            
            self.log(f"Konvertierung abgeschlossen: {successful}/{total_files} erfolgreich")
            
        except Exception as e:
            self.log(f"Fehler bei der Batch-Konvertierung: {str(e)}")
        
        finally:
            self.is_converting = False
    
    def stop_conversion(self):
        """Stoppt die laufende Konvertierung"""
        self.is_converting = False
        self.log("Konvertierung wird gestoppt...")
    
    def get_available_encoders(self) -> List[str]:
        """Ermittelt verfügbare Hardware-Encoder"""
        available = ["libx264"]  # Software-Encoder ist immer verfügbar
        
        # Prüfe NVIDIA
        try:
            result = subprocess.run(['ffmpeg', '-encoders'], 
                                  capture_output=True, text=True, timeout=10)
            if 'h264_nvenc' in result.stdout:
                available.append("h264_nvenc")
        except:
            pass
        
        # Prüfe AMD
        try:
            if 'h264_amf' in result.stdout:
                available.append("h264_amf")
        except:
            pass
        
        # Prüfe Intel
        try:
            if 'h264_qsv' in result.stdout:
                available.append("h264_qsv")
        except:
            pass
        
        return available
