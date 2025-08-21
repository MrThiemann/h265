import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_file = Path("converter_config.json")
        self.default_config = {
            "output_directory": str(Path.home() / "Videos" / "Converted"),
            "default_encoder": "libx264",
            "default_crf": 23,
            "default_preset": "medium",
            "default_output_format": "MP4",
            "default_profile": "high",
            "max_threads": "Auto",
            "overwrite_files": False,
            "language": "de",
            "auto_optimize_large_files": True,
            "split_large_files": True,
            "large_file_threshold_mb": 500,
            "extra_large_file_threshold_gb": 1
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Lädt die Konfiguration aus der JSON-Datei"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            except:
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """Speichert die aktuelle Konfiguration"""
        os.makedirs(self.config_file.parent, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        """Holt einen Konfigurationswert"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Setzt einen Konfigurationswert"""
        self.config[key] = value
        self.save_config()

# Encoder-Profile
ENCODERS = {
    "libx264": "Software Encoder (x264)",
    "h264_nvenc": "NVIDIA GPU Encoder",
    "h264_amf": "AMD GPU Encoder", 
    "h264_qsv": "Intel Quick Sync"
}

# Preset-Geschwindigkeiten
PRESETS = [
    "ultrafast", "superfast", "veryfast", "faster", 
    "fast", "medium", "slow", "slower", "veryslow"
]

# Ausgabeformate
OUTPUT_FORMATS = ["MP4", "MKV", "MOV", "AVI", "FLV"]

# Encoding-Profile
ENCODING_PROFILES = ["baseline", "main", "high", "high10", "high422", "high444"]

# Unterstützte Eingabeformate
INPUT_FORMATS = [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm"]

# Threading-Optionen
THREAD_OPTIONS = ["Auto", "1", "2", "4", "Max"]

# Sprachen
LANGUAGES = {
    "de": "Deutsch",
    "en": "English"
}
