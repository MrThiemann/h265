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
            # libx264 unterstützt alle Presets
            cmd.extend(['-preset', preset])
        elif encoder == "h264_nvenc":
            cmd.extend(['-c:v', 'h264_nvenc'])
            # NVIDIA NVENC unterstützt nur bestimmte Presets
            if preset in ["veryslow", "slower", "slow"]:
                cmd.extend(['-preset', 'slow'])
            elif preset in ["faster", "veryfast", "superfast", "ultrafast"]:
                cmd.extend(['-preset', 'fast'])
            else:
                cmd.extend(['-preset', 'medium'])
        elif encoder == "h264_amf":
            cmd.extend(['-c:v', 'h264_amf'])
            # AMD AMF verwendet quality-Parameter statt preset
            if preset in ["veryslow", "slower", "slow"]:
                cmd.extend(['-quality', 'quality'])
            elif preset in ["faster", "veryfast", "superfast", "ultrafast"]:
                cmd.extend(['-quality', 'speed'])
            else:
                cmd.extend(['-quality', 'balanced'])
            
            # AMD-spezifische Parameter für bessere Qualität
            cmd.extend(['-rc', 'cqp'])  # Constant QP Rate Control
            cmd.extend(['-qp_i', '23'])  # I-Frame QP
            cmd.extend(['-qp_p', '23'])  # P-Frame QP
            cmd.extend(['-qp_b', '23'])  # B-Frame QP
        elif encoder == "h264_qsv":
            cmd.extend(['-c:v', 'h264_qsv'])
            # Intel QSV unterstützt nur bestimmte Presets
            if preset in ["veryslow", "slower", "slow"]:
                cmd.extend(['-preset', 'slow'])
            elif preset in ["faster", "veryfast", "superfast", "ultrafast"]:
                cmd.extend(['-preset', 'fast'])
            else:
                cmd.extend(['-preset', 'medium'])
        
        # Qualität (CRF für libx264, QP für Hardware-Encoder)
        if encoder == "libx264":
            cmd.extend(['-crf', str(crf)])
        elif encoder == "h264_amf":
            # AMD AMF verwendet bereits QP-Parameter oben
            pass  # QP-Parameter wurden bereits gesetzt
        else:
            # Andere Hardware-Encoder verwenden QP statt CRF
            qp = max(0, min(51, crf))  # Konvertiere CRF zu QP
            cmd.extend(['-qp', str(qp)])
        
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
    
    def get_video_info(self, input_file: str) -> dict:
        """Ermittelt Informationen über das Video"""
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
                   '-show_streams', '-select_streams', 'v:0', input_file]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if 'streams' in data and len(data['streams']) > 0:
                    stream = data['streams'][0]
                    return {
                        'width': stream.get('width', 0),
                        'height': stream.get('height', 0),
                        'pix_fmt': stream.get('pix_fmt', ''),
                        'bit_depth': stream.get('bits_per_raw_sample', 8),
                        'codec_name': stream.get('codec_name', ''),
                        'duration': stream.get('duration', 0)
                    }
        except Exception as e:
            self.log(f"Fehler beim Ermitteln der Video-Informationen: {str(e)}")
        
        return {}
    
    def get_optimal_profile(self, video_info: dict, requested_profile: str, color_depth_mode: str = "auto") -> str:
        """Ermittelt das optimale Encoding-Profil basierend auf der Video-Farbtiefe und Benutzerauswahl"""
        bit_depth = video_info.get('bit_depth', 8)
        pix_fmt = video_info.get('pix_fmt', '')
        is_10bit = bit_depth == 10 or '10' in pix_fmt
        
        # Farbtiefe-Modus bestimmen
        if color_depth_mode == "compatibility":
            # Erzwinge 8-Bit für maximale Kompatibilität
            if requested_profile in ['baseline', 'main', 'high']:
                return requested_profile
            else:
                return 'high'  # Fallback auf high für 8-Bit
        elif color_depth_mode == "quality":
            # Erzwinge 10-Bit für beste Qualität
            if is_10bit:
                if requested_profile in ['baseline', 'main', 'high']:
                    return 'high10'
                else:
                    return requested_profile
            else:
                # 8-Bit Video - verwende angeforderte Profil
                return requested_profile
        else:  # auto
            # Automatische Entscheidung basierend auf Quellvideo
            if is_10bit:
                if requested_profile in ['baseline', 'main', 'high']:
                    self.log(f"10-Bit Video erkannt - verwende 'high10' Profil statt '{requested_profile}'")
                    return 'high10'
                elif requested_profile in ['high422', 'high444']:
                    return requested_profile
                else:
                    return 'high10'
            else:
                # 8-Bit Video - verwende angeforderte Profil
                return requested_profile
    
    def convert_single_file(self, input_file: str, output_file: str, 
                           encoder: str, crf: int, preset: str, 
                           profile: str, threads: str, color_depth_mode: str = "auto") -> bool:
        """Konvertiert eine einzelne Datei"""
        try:
            # Erstelle Ausgabeverzeichnis
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Hole Video-Informationen für optimale Profil-Auswahl
            video_info = self.get_video_info(input_file)
            optimal_profile = self.get_optimal_profile(video_info, profile, color_depth_mode)
            
            # Baue FFmpeg-Befehl
            cmd = self.build_ffmpeg_command(input_file, output_file, encoder, 
                                          crf, preset, optimal_profile, threads)
            
            self.log(f"Starte Konvertierung: {os.path.basename(input_file)}")
            self.log(f"Encoder: {encoder}, Preset: {preset}, Qualität: {crf}")
            self.log(f"Farbtiefe-Modus: {color_depth_mode}")
            
            if optimal_profile != profile:
                self.log(f"Profil angepasst: {profile} → {optimal_profile}")
                if color_depth_mode == "compatibility":
                    self.log("8-Bit Profil für maximale Kompatibilität (QuickTime, etc.)")
                elif color_depth_mode == "quality":
                    self.log("10-Bit Profil für beste Qualität (moderne Player)")
                else:
                    self.log(f"Automatische Anpassung wegen {video_info.get('bit_depth', 8)}-Bit Video")
            
            # Führe FFmpeg aus
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True, 
                                     bufsize=1, universal_newlines=True)
            
            # Überwache den Prozess
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Filtere wichtige Nachrichten
                    output = output.strip()
                    if output and not output.startswith('frame='):
                        if self.progress_callback:
                            self.progress_callback(output)
            
            # Warte auf Beendigung
            return_code = process.wait()
            
            if return_code == 0:
                self.log(f"Konvertierung erfolgreich: {os.path.basename(output_file)}")
                return True
            else:
                # Prüfe ob es ein Hardware-Encoder-Problem ist
                if encoder != "libx264" and "Cannot load" in str(process.stderr) or "Error while opening encoder" in str(process.stderr):
                    self.log(f"Hardware-Encoder {encoder} fehlgeschlagen, versuche Software-Encoder...")
                    return self.convert_with_software_fallback(input_file, output_file, crf, preset, profile, threads)
                else:
                    self.log(f"Fehler bei der Konvertierung: {os.path.basename(input_file)} (Code: {return_code})")
                    return False
                
        except Exception as e:
            self.log(f"Fehler: {str(e)}")
            return False
    
    def convert_with_software_fallback(self, input_file: str, output_file: str, 
                                     crf: int, preset: str, profile: str, threads: str) -> bool:
        """Konvertiert mit Software-Encoder als Fallback"""
        try:
            self.log("Verwende Software-Encoder (libx264) als Fallback...")
            
            # Baue FFmpeg-Befehl für Software-Encoder
            cmd = ['ffmpeg', '-i', input_file, '-y', '-c:v', 'libx264', 
                   '-preset', preset, '-crf', str(crf), '-profile:v', profile, 
                   '-c:a', 'copy', output_file]
            
            # Threading
            if threads != "Auto":
                if threads == "Max":
                    cmd.extend(['-threads', '0'])
                else:
                    cmd.extend(['-threads', threads])
            
            # Führe FFmpeg aus
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True, 
                                     bufsize=1, universal_newlines=True)
            
            # Überwache den Prozess
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output = output.strip()
                    if output and not output.startswith('frame='):
                        if self.progress_callback:
                            self.progress_callback(f"[Software-Fallback] {output}")
            
            # Warte auf Beendigung
            return_code = process.wait()
            
            if return_code == 0:
                self.log(f"Software-Encoder Konvertierung erfolgreich: {os.path.basename(output_file)}")
                return True
            else:
                self.log(f"Software-Encoder Konvertierung fehlgeschlagen: {os.path.basename(input_file)} (Code: {return_code})")
                return False
                
        except Exception as e:
            self.log(f"Fehler bei Software-Encoder Fallback: {str(e)}")
            return False
    
    def convert_files(self, file_list: List[Dict], encoder: str, crf: int, 
                     preset: str, profile: str, threads: str, 
                     output_format: str, overwrite: bool = False, color_depth_mode: str = "auto"):
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
                                          crf, preset, profile, threads, color_depth_mode):
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
        
        # Prüfe AMD (Priorität für AMD-Systeme)
        try:
            result = subprocess.run(['ffmpeg', '-encoders'], 
                                  capture_output=True, text=True, timeout=10)
            if 'h264_amf' in result.stdout:
                # Teste ob der AMD Encoder tatsächlich funktioniert
                test_result = subprocess.run([
                    'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                    '-c:v', 'h264_amf', '-t', '1', '-y', 'NUL'
                ], capture_output=True, text=True, timeout=30)
                if test_result.returncode == 0:
                    available.append("h264_amf")
                    self.log("AMD AMF Encoder: Verfügbar und funktionsfähig")
                else:
                    self.log("AMD AMF Encoder: Verfügbar aber nicht funktionsfähig (Treiber-Problem)")
        except Exception as e:
            self.log(f"Fehler beim Testen von AMD AMF: {str(e)}")
        
        # Prüfe Intel Quick Sync
        try:
            if 'h264_qsv' in result.stdout:
                test_result = subprocess.run([
                    'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                    '-c:v', 'h264_qsv', '-t', '1', '-y', 'NUL'
                ], capture_output=True, text=True, timeout=30)
                if test_result.returncode == 0:
                    available.append("h264_qsv")
                    self.log("Intel QSV Encoder: Verfügbar und funktionsfähig")
                else:
                    self.log("Intel QSV Encoder: Verfügbar aber nicht funktionsfähig")
        except Exception as e:
            self.log(f"Fehler beim Testen von Intel QSV: {str(e)}")
        
        # NVIDIA nur prüfen wenn explizit gewünscht (für Hybrid-Systeme)
        # Für reine AMD-Systeme überspringen wir NVIDIA
        try:
            # Prüfe ob wir auf einem AMD-System sind
            if 'h264_amf' in available:
                self.log("AMD-System erkannt - NVIDIA NVENC wird übersprungen")
            else:
                # Nur prüfen wenn AMD nicht verfügbar ist
                if 'h264_nvenc' in result.stdout:
                    test_result = subprocess.run([
                        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
                        '-c:v', 'h264_nvenc', '-t', '1', '-y', 'NUL'
                    ], capture_output=True, text=True, timeout=30)
                    if test_result.returncode == 0:
                        available.append("h264_nvenc")
                        self.log("NVIDIA NVENC Encoder: Verfügbar und funktionsfähig")
                    else:
                        self.log("NVIDIA NVENC Encoder: Verfügbar aber nicht funktionsfähig (CUDA-Treiber fehlen)")
        except Exception as e:
            self.log(f"Fehler beim Testen von NVIDIA NVENC: {str(e)}")
        
        return available
