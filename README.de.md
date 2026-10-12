# esphome-configs

Wiederverwendbare ESPHome-Packages und adoptierbare Geräte-Configs. [English](README.md)

## Aufbau
| Ordner | Inhalt |
|---|---|
| `core/` | api, ota, wifi |
| `hardware/` | Bausteine nach Funktion (Boards, Sensoren, Leistungsmessung, Licht ...) |
| `i18n/` | sichtbare Texte (`en` vollständig, `de` überschreibt) |
| `projects/` | komplette Geräte, über das ESPHome-Dashboard adoptierbar |
| `templates/` | Vorlagen für neue Dateien |

## Gerät adoptieren
1. Gerät mit einer Config aus `projects/` flashen.
2. Im ESPHome-Dashboard erscheint es als *discovered*, auf *Adopt* klicken.
3. Deine `secrets.yaml` braucht `wifi_ssid` und `wifi_password` (siehe `secrets.example.yaml`).

## Sprache
Das Sprach-Package nach dem Basis-Package einbinden, für Englisch die Zeile weglassen:
```yaml
packages:
  i18n_base: github://OWNER/esphome-configs/i18n/en.yaml@<tag>
  i18n_lang: github://OWNER/esphome-configs/i18n/de.yaml@<tag>
```
Home-Assistant-Entity-IDs entstehen aus dem Namen, ein in anderer Sprache adoptiertes Gerät bekommt andere IDs.

## Was enthalten ist
[docs/CATALOG.md](docs/CATALOG.md) listet jedes Package mit Zweck, Chip und Voraussetzungen (aus den Datei-Köpfen erzeugt).
Fertige Geräte liegen in `projects/`, `examples/` zeigt, wie einzelne Bausteine kombiniert werden.

## Mehrere Instanzen
Batterien, PID-Lüfter und BME680-Sensoren werden pro Instanz mit `vars:` eingebunden und sind jeweils ein eigenes Sub-Gerät
in Home Assistant, siehe [CONVENTIONS.md](CONVENTIONS.md#multi-instance-modules-and-sub-devices).

## Mitarbeit
[CONVENTIONS.md](CONVENTIONS.md) lesen, dann `python scripts/check.py` (Konventionen) und
`python scripts/check.py --esphome` (ESPHome-Prüfung). Releases: `python scripts/bump-tag.py`.
