# Iftar Time Widget Options

| Option               | Type    | Default                                                                   | Description                                                                                                           |
|----------------------|---------|---------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| `label`              | string  | `'<span>\uf017</span> Iftar: {iftar_time}'`                               | Format string for the main label. Supports `{iftar_time}`, `{sahur_time}`, and `{remaining}` placeholders.           |
| `label_alt`          | string  | `'<span>\uf017</span> Sahur: {sahur_time} \| Iftar: {iftar_time} \| Remaining: {remaining}'` | Alternative format string for the label.                              |
| `class_name`         | string  | `""`                                                                      | Additional CSS class name for the widget.                                                                             |
| `city`               | string  | `"Istanbul"`                                                              | City for which prayer times are fetched.                                                                              |
| `country`            | string  | `"Turkey"`                                                                | Country for the city.                                                                                                 |
| `calculation_method` | integer | `13`                                                                      | Prayer time calculation method. `13` = Diyanet İşleri Başkanlığı (Turkey). See [Aladhan methods](https://aladhan.com/calculation-methods). |
| `time_format`        | string  | `"24h"`                                                                   | Clock format for displayed times. Can be `"24h"` or `"12h"`.                                                         |
| `update_interval`    | integer | `3600`                                                                    | How often (in seconds) to refresh prayer times from the API. Min 60, Max 86400.                                       |
| `tooltip`            | boolean | `true`                                                                    | Whether to show a tooltip with full prayer-time details.                                                              |
| `animation`          | dict    | `{'enabled': true, 'type': 'fadeInOut', 'duration': 200}`                | Animation settings for the widget.                                                                                    |
| `container_shadow`   | dict    | `None`                                                                    | Container shadow options.                                                                                             |
| `label_shadow`       | dict    | `None`                                                                    | Label shadow options.                                                                                                 |
| `callbacks`          | dict    | `{'on_left': 'toggle_label', 'on_middle': 'do_nothing', 'on_right': 'do_nothing'}` | Callbacks for mouse events on the widget.                                                            |

## Label Placeholders

| Placeholder      | Description                                               |
|------------------|-----------------------------------------------------------|
| `{iftar_time}`   | Iftar (Maghrib) time for the configured city.             |
| `{sahur_time}`   | Sahur end (Imsak) time for the configured city.           |
| `{remaining}`    | Time remaining until the next Iftar (e.g. `2h 30m`).     |

> **Note:** Prayer times are fetched from the free [Aladhan API](https://aladhan.com/prayer-times-api). No API key is required.

## Minimal Configuration

```yaml
iftar:
  type: "yasb.iftar.IftarWidget"
  options:
    label: "<span>\uf017</span> Iftar: {iftar_time}"
    label_alt: "Sahur: {sahur_time} | Iftar: {iftar_time} | Remaining: {remaining}"
    city: "Istanbul"
    country: "Turkey"
    update_interval: 3600
```

## Advanced Configuration

```yaml
iftar:
  type: "yasb.iftar.IftarWidget"
  options:
    label: "<span>\uf017</span> Iftar: {iftar_time} ({remaining})"
    label_alt: "<span>\uf017</span> Sahur: {sahur_time} | Iftar: {iftar_time} | Remaining: {remaining}"
    class_name: ""
    city: "Istanbul"
    country: "Turkey"
    calculation_method: 13  # Diyanet İşleri Başkanlığı (Turkey)
    time_format: "24h"       # or "12h"
    update_interval: 3600   # Refresh every hour
    tooltip: true
    animation:
      enabled: true
      type: "fadeInOut"
      duration: 200
    callbacks:
      on_left: "toggle_label"
      on_middle: "do_nothing"
      on_right: "do_nothing"
```

## Calculation Methods

The following calculation method IDs are supported by the Aladhan API:

| ID | Method                                                      |
|----|-------------------------------------------------------------|
| 0  | Shia Ithna-Ansari                                           |
| 1  | University of Islamic Sciences, Karachi                     |
| 2  | Islamic Society of North America (ISNA)                     |
| 3  | Muslim World League (MWL)                                   |
| 4  | Umm al-Qura University, Makkah                              |
| 5  | Egyptian General Authority of Survey                        |
| 7  | Institute of Geophysics, University of Tehran               |
| 8  | Gulf Region                                                 |
| 9  | Kuwait                                                      |
| 10 | Qatar                                                       |
| 11 | Majlis Ugama Islam Singapura, Singapore                     |
| 12 | Union Organization Islamic de France                        |
| 13 | **Diyanet İşleri Başkanlığı, Turkey** *(default)*           |
| 14 | Spiritual Administration of Muslims of Russia               |
| 15 | Moonsighting Committee Worldwide                            |
