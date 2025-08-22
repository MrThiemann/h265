# H.264 AVC Converter - H.265(HEVC) zu libx264

Ein professionelles Tool zur Konvertierung von H.265/HEVC Video-Dateien in das H.264/AVC Format für bessere Kompatibilität auf allen Geräten.

**Entwickelt von:** Karsten Thiemann  
**GitHub Repository:** https://github.com/MrThiemann/h265

## 🎯 Hauptfunktionen

### Kernfunktionen
- **Format-Konvertierung**: H.265/HEVC → H.264/AVC
- **Unterstützte Eingabeformate**: MP4, MKV, MOV, AVI, FLV, WMV, WEBM
- **Ausgabeformate**: MP4, MKV, MOV, AVI, FLV
- **Batch-Verarbeitung**: Mehrere Dateien gleichzeitig konvertieren
- **Ordner-Import**: Alle Videodateien aus einem Ordner importieren

### Encoder-Optionen
- **Software-Encoder**: libx264 (x264) - **Immer verfügbar und zuverlässig**
- **Hardware-Encoder**: 
  - NVIDIA GPU: h264_nvenc
  - AMD GPU: h264_amf
  - Intel Quick Sync: h264_qsv
- **Intelligente Encoder-Erkennung**: Nur funktionsfähige Encoder werden angezeigt
- **Automatischer Fallback**: Bei Hardware-Encoder-Problemen → Software-Encoder

### Erweiterte Features
- **CRF-Qualitätsanpassung**: 0-51 (0 = verlustfrei, 51 = schlechteste Qualität)
- **Preset-Geschwindigkeit**: 9 Stufen von ultrafast bis veryslow
- **Encoding-Profile**: baseline, main, high, high10, high422, high444
- **Multi-Threading**: Auto, 1, 2, 4 oder Max Threads
- **Automatische Optimierung**: Große Dateien (>500MB) werden automatisch optimiert
- **Datei-Teilung**: Sehr große Dateien (>1GB) werden automatisch geteilt und wieder zusammengefügt

### 🆕 Neue Features (v1.1+)
- **Intelligente Farbtiefe-Auswahl**: 
  - 🔄 **Automatisch**: Wählt beste Farbtiefe basierend auf Quellvideo
  - 🎨 **Hohe Qualität**: 10-Bit für moderne Player (VLC, Windows Media Player)
  - 🔗 **Maximale Kompatibilität**: 8-Bit für alle Player (QuickTime, ältere Geräte)
- **Automatische Profil-Anpassung**: 10-Bit Videos → high10 Profil
- **Video-Analyse**: Automatische Erkennung von Farbtiefe und Eigenschaften
- **Verbesserte Fehlerbehandlung**: Detaillierte Logs und automatische Fallbacks

## 🚀 Installation

### Voraussetzungen

1. **Python 3.7+** installieren
   - Download: https://www.python.org/downloads/
   - Bei der Installation "Add Python to PATH" aktivieren

2. **FFmpeg** installieren
   - Download: https://ffmpeg.org/download.html
   - Oder über Package Manager:
     - Windows: `choco install ffmpeg`
     - macOS: `brew install ffmpeg`
     - Linux: `sudo apt install ffmpeg`

### Installation der Anwendung

1. **Repository klonen oder herunterladen**
   ```bash
   git clone https://github.com/yourusername/h264-converter.git
   cd h264-converter
   ```

2. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

3. **Anwendung starten**
   ```bash
   python main.py
   ```

### Windows-Installation (einfach)

1. **Batch-Datei ausführen**: `install_and_run.bat`
2. **Oder manuell**:
   ```cmd
   pip install -r requirements.txt
   python main.py
   ```

## 📱 Verwendung

### Schnellstart

1. **Anwendung starten**
2. **Videodateien hinzufügen** (einzeln oder Ordner)
3. **Farbtiefe-Modus wählen** (Qualität vs. Kompatibilität)
4. **Einstellungen anpassen** (Encoder, Qualität, etc.)
5. **Ausgabeverzeichnis wählen**
6. **Konvertierung starten**

### Detaillierte Einstellungen

#### Farbtiefe-Modus (NEU!)
- **🔄 Automatisch (empfohlen)**: 
  - Wählt automatisch beste Farbtiefe basierend auf Quellvideo
  - 10-Bit Videos → high10 Profil, 8-Bit Videos → angeforderte Profil
- **🎨 Hohe Qualität (10-Bit)**:
  - Behält 10-Bit Farbtiefe bei (beste Qualität)
  - Für moderne Player (VLC, Windows Media Player, etc.)
  - Größere Dateien, aber beste Bildqualität
- **🔗 Maximale Kompatibilität (8-Bit)**:
  - Konvertiert zu 8-Bit (maximale Kompatibilität)
  - Funktioniert mit allen Playern (QuickTime, ältere Geräte, etc.)
  - Kleinere Dateien, aber 8-Bit Qualität

#### Encoder-Auswahl
- **libx264**: Beste Qualität, langsamste Geschwindigkeit, **immer verfügbar**
- **h264_nvenc**: NVIDIA GPU, schnell, gute Qualität
- **h264_amf**: AMD GPU, schnell, gute Qualität
- **h264_qsv**: Intel Quick Sync, schnell, mittlere Qualität

#### CRF-Werte (Constant Rate Factor)
- **0-18**: Visuell verlustfrei
- **19-23**: Sehr hohe Qualität (Standard: 23)
- **24-28**: Hohe Qualität
- **29-35**: Mittlere Qualität
- **36-51**: Niedrige Qualität

#### Preset-Geschwindigkeit
- **ultrafast**: Schnellste Konvertierung, niedrigste Qualität
- **superfast**: Sehr schnell
- **veryfast**: Schnell
- **faster**: Schneller als Standard
- **fast**: Schnell
- **medium**: Ausgewogen (Standard)
- **slow**: Langsam
- **slower**: Langsamer
- **veryslow**: Langsamste Konvertierung, beste Qualität

## ⚙️ Konfiguration

Die Anwendung speichert alle Einstellungen automatisch in `converter_config.json`. Diese Datei wird im Anwendungsverzeichnis erstellt.

### Konfigurationsoptionen
- Ausgabeverzeichnis
- Standard-Encoder
- Standard-CRF-Wert
- Standard-Preset
- Standard-Ausgabeformat
- Standard-Encoding-Profil
- Thread-Anzahl
- Überschreiben existierender Dateien
- Automatische Optimierung großer Dateien
- Automatische Teilung sehr großer Dateien
- **Farbtiefe-Modus** (NEU!)
- **Erzwungene 8-Bit Konvertierung** (NEU!)

## 🔧 Troubleshooting

### Häufige Probleme

#### FFmpeg nicht gefunden
- **Lösung**: FFmpeg installieren und zum PATH hinzufügen
- **Windows**: FFmpeg-Ordner zu den Umgebungsvariablen hinzufügen
- **macOS/Linux**: `export PATH=$PATH:/path/to/ffmpeg`

#### Hardware-Encoder nicht verfügbar
- **NVIDIA**: Neueste Treiber installieren
- **AMD**: Neueste Treiber installieren
- **Intel**: Quick Sync in BIOS aktivieren
- **Hinweis**: Nur funktionsfähige Encoder werden angezeigt

#### QuickTime-Kompatibilitätsprobleme
- **Lösung**: Farbtiefe-Modus auf "Maximale Kompatibilität (8-Bit)" setzen
- **Alternative**: Moderne Player wie VLC verwenden
- **Automatisch**: Farbtiefe-Modus "Automatisch" wählen

#### Speicherfehler bei großen Dateien
- **Lösung**: Automatische Optimierung aktivieren
- **Alternative**: Dateien manuell teilen

#### Langsame Konvertierung
- **Tipp**: Hardware-Encoder verwenden (falls verfügbar)
- **Tipp**: Preset auf "fast" oder "veryfast" setzen
- **Tipp**: Thread-Anzahl erhöhen

### Log-Dateien

Das Konvertierungsprotokoll kann als Textdatei gespeichert werden und enthält detaillierte Informationen über den Konvertierungsprozess.

## 📊 Performance-Tipps

### Optimale Einstellungen für verschiedene Anwendungsfälle

#### Schnelle Konvertierung
- Encoder: h264_nvenc (NVIDIA) oder h264_amf (AMD)
- Preset: ultrafast oder superfast
- CRF: 28-35
- Threads: Max

#### Beste Qualität
- Encoder: libx264
- Preset: veryslow
- CRF: 18-23
- Threads: Auto
- Farbtiefe: Hohe Qualität (10-Bit)

#### Ausgewogen
- Encoder: libx264
- Preset: medium
- CRF: 23
- Threads: Auto
- Farbtiefe: Automatisch

#### Maximale Kompatibilität
- Encoder: libx264
- Preset: medium
- CRF: 23
- Threads: Auto
- Farbtiefe: Maximale Kompatibilität (8-Bit)

## 🆘 Support

### Bekannte Einschränkungen
- Audio wird standardmäßig kopiert (nicht neu kodiert)
- Einige exotische Videoformate werden möglicherweise nicht unterstützt
- Hardware-Encoder benötigen entsprechende Treiber
- 10-Bit Videos benötigen moderne Player für beste Qualität

### Hilfe bekommen
1. **Log-Datei prüfen**: Enthält detaillierte Fehlerinformationen
2. **FFmpeg-Status prüfen**: Menü → Hilfe → FFmpeg-Status
3. **Standardwerte zurücksetzen**: Menü → Einstellungen → Standardwerte wiederherstellen
4. **Farbtiefe-Modus anpassen**: Für QuickTime-Kompatibilität auf 8-Bit setzen

## 📝 Changelog

### Version 1.1.0
- **Intelligente Farbtiefe-Auswahl**: Automatisch, Qualität, Kompatibilität
- **Automatische Profil-Anpassung**: 10-Bit Videos → high10 Profil
- **Verbesserte Encoder-Erkennung**: Nur funktionsfähige Encoder werden angezeigt
- **Automatischer Software-Fallback**: Bei Hardware-Encoder-Problemen
- **Video-Analyse**: Automatische Erkennung von Farbtiefe und Eigenschaften
- **QuickTime-Kompatibilität**: 8-Bit Modus für maximale Kompatibilität

### Version 1.0.0
- Erste Veröffentlichung
- Vollständige H.264/AVC Konvertierung
- Hardware-Encoder-Unterstützung
- Batch-Verarbeitung
- Automatische Optimierung großer Dateien

## 🤝 Beitragen

Verbesserungsvorschläge und Bug-Reports sind willkommen!

**Entwickler:** Karsten Thiemann  
**GitHub:** https://github.com/MrThiemann/h265

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

## 🙏 Danksagungen

- **FFmpeg**: Für die leistungsstarke Videokonvertierung
- **Python**: Für die flexible Programmiersprache
- **tkinter**: Für die plattformunabhängige GUI

---

**Entwickelt mit ❤️ für die Video-Community**
