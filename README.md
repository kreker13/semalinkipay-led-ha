# semalinkipay-led-ha

> Управление **BLE LED- и неоновой лентами** (MELK / ELK-BLEDOB / ELK-BLEDDM)
> через **Home Assistant** и **Алису (Яндекс Умный дом)** — голосом.
> Один авто-установщик для **Linux** и **Windows**. Подробные инструкции для тех, кто ставит впервые.

**Автор / поддержка / донат:** Telegram **[@cas1noonewin](https://t.me/cas1noonewin)** — `semalinkipay`

![platform](https://img.shields.io/badge/OS-Linux%20%7C%20Windows-blue)
![HA](https://img.shields.io/badge/Home%20Assistant-Core-brightgreen)
![Alice](https://img.shields.io/badge/Voice-Alice%20%2F%20Yandex-red)
![BLE](https://img.shields.io/badge/Control-BLE%20LED%20strips-8A2BE2)
![license](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Что это решает

Дешёвые Bluetooth-ленты (контроллеры MELK/ELK) часто «не слушаются» Алису: ленты
то включаются, то нет, яркость из голоса ломает цвет, в Яндексе плодятся «мёртвые»
дубли. Здесь это починено:

- **Один надёжный BLE-пакет на команду** — без капризных анимаций, которые рвутся на слабом сигнале.
- **Дефолтный цвет + яркость при включении** задаются в одном месте (`template.yaml`).
- **Патч elkbledom**: ELK-ленты больше не «залипают выключенными» (исправлен пропуск пакета питания при оптимистичном состоянии).
- **Ровно две чистые сущности в Яндекс** (`light.neon`, `light.led`) — никаких дублей.
- **Авто-установщик** `install.py` — сам ставит Home Assistant и кладёт все конфиги.

---

## 📦 Что в репозитории

```
semalinkipay-led-ha/
├── install.py                 ← ЗАПУСТИ ЭТО (кроссплатформенный установщик)
├── configs/                   ← шаблоны конфигров HA (без секретов)
│   ├── configuration.yaml
│   ├── template.yaml          ← голосовые «прокладки» light.neon / light.led
│   ├── scripts.yaml
│   ├── automations.yaml
│   └── yandex_smart_home.yaml ← что отдаём Алисе
├── custom_components/
│   └── elkbledom/             ← патченная интеграция BLE-лент (см. ATTRIBUTION.md)
├── docs/
│   └── TROUBLESHOOTING.md     ← «лента не реагирует» и прочие боли
├── ATTRIBUTION.md             ← кто автор upstream-компонентов
├── LICENSE                    ← MIT © semalinkipay
└── README.md
```

---

## 🚀 Быстрый старт (для новичков)

### Шаг 0. Что понадобится
- PC/ноутбук/мини-ПК с **Bluetooth** (или ESPHome-прокси Bluetooth — см. ниже).
- Две (или одна) BLE-ленты MELK/ELK. **MAC-адреса не нужны** — HA сам найдёт ленты.
- Установленный **Python 3.11+** (Linux: обычно уже есть; Windows: поставь с [python.org](https://www.python.org/downloads/), отметь “Add to PATH”).
- Аккаунт **Яндекс** с приложением «Дом с Алисой».

### Шаг 1. Скачать проект
```bash
# Linux / macOS
git clone https://github.com/kreker13/semalinkipay-led-ha.git
cd semalinkipay-led-ha
```
Windows: кнопка **Code → Download ZIP**, распакуй, открой папку в терминале (PowerShell).

### Шаг 2. Запустить установщик
```bash
# Linux / macOS
python3 install.py
```
```powershell
# Windows
py -3 install.py
```
Дальше мастер спросит:
1. **Способ установки** — на Linux выбери `1` (HA Core в venv + сервис), на Windows `1` (Docker).
2. **Папку конфигурации HA** — можно оставить по умолчанию (Enter).
3. Подтверждение — `y`.

Скрипт сам: создаст venv/контейнер, поставит Home Assistant, положит наши конфиги
и **патченный elkbledom**, а `yandex_smart_home` скачает с оригинального репозитория.
Ничто из уже существующего не перезапишет без бэкапа (`.semlinki-backup-…`).

### Шаг 3. Первый запуск Home Assistant
Открой **http://localhost:8123** и пройди onboarding (создай пользователя/дом).

### Шаг 4. Добавить ленты (Bluetooth)
**Настройки → Устройства и сервисы → Добавить интеграцию → «ElkBLEDOM».**
Интеграция увидит MELK*/ELK* поблизости — добавь обе ленты.
Затем приведи их сущности к именам из шаблона:
`light.neon_phys` и `light.led_phys`
(Настройки → Устройства → сущность lights → ✏️ «Изменить entity_id»).

> Нет встроенного Bluetooth? Добавь **ESP32-прокси** (ESPHome `bluetooth_proxy`)
> или USB-адаптер. HA использует активный скан — passive-адаптеры могут не видеть ленты.

### Шаг 5. Подключить Яндекс (Алису)
**Настройки → Устройства и сервисы → «Yandex Smart Home».**
Понадобится **Long-Lived Access Token**: профиль → Безопасность → внизу
«Long-lived access tokens» → создать → скопировать в поле интеграции.
В `yandex_smart_home.yaml` уже настроена отдача ровно `light.neon` и `light.led`.

### Шаг 6. Говорим Алисе
> «Алиса, включи светодиодную ленту» · «Алиса, включи неоновую ленту»
> «Алиса, сделай светодиодную ленту красной»

Готово 🎉. Если «не реагирует» — см. **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**.

---

## 🧰 Ручная установка (если не хочешь install.py)

1. Поставь Home Assistant (Core в venv / Container — по официальной инструкции).
2. Скопируй `custom_components/elkbledom/` → в `<config>/custom_components/elkbledom/`.
3. Скачай `yandex_smart_home` с upstream → в `<config>/custom_components/yandex_smart_home/`.
4. Скопируй файлы из `configs/` в `<config>/` (configuration/template/scripts/automations/yandex_smart_home).
5. Перезапусти HA и выполни шаги 3–6 выше.

> После правки `custom_components` нужен **полный рестарт** HA (не просто «перезагрузка конфигурации»).

---

## ⚙️ Как это работает (кратко)

```
Алиса (Яндекс)
   │  entity_id стабильны
   ▼
light.neon / light.led          ← template-«прокладки» (template.yaml)
   │  одиночные надёжные BLE-команды
   ▼
light.neon_phys / light.led_phys ← патченный elkbledom (custom_components)
   │  BLE GATT
   ▼
 MELK / ELK контроллер ленты
```
Прокладки нужны, чтобы: (а) дать Яндексу стабильные id; (б) ставить дефолтный
цвет/яркость при включении; (в) не отдавать в Яндекс физические сущности и дубли.

**Почему нет анимаций:** на слабом BLE-линке `repeat`-блоки с таймаутами отклоняются
новой HA, а потоковые пакеты теряются → ленты «дёргаются» или не слушаются. Мы
сознательно делаем **по одному пакету на команду** — это стабильно.

---

## 🪟 Windows: важное
Home Assistant **не ставится нативно на Windows**. Правильный путь — **Docker
Desktop** (с WSL2) или HA в WSL2. Установщик в режиме Docker сгенерит
`docker-compose.yml` с `network_mode: host`. Для Bluetooth на Windows через Docker
обычно нужен **внешний BLE-прокси (ESP32/ESPHome)** — прямое BT-«железо» из
контейнера Windows-хоста часто недоступно. Если хочешь именно native HA Core на
Windows — это неофициально и с оговорками; спрашивай в TG.

---

## 🩺 Частые проблемы
Полный разбор — **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**. Топ-3:
| Симптом | Быстрое решение |
|---|---|
| Лента не находится в «Добавить интеграцию» | Включи активный Bluetooth, поднеси ленту, перезапусти HA |
| Алиса говорит «не найдено» | Проверь `yandex_smart_home.yaml` (только `light.neon`/`light.led`) и привязку устройств |
| «Вкл/выкл», а лента молчит | Обесточь контроллер на 10–15 с (залипший ELK) и повтори; проверь `*_phys` id в `template.yaml` |

---

## 🙏 Благодарности
- [@dave-code-ruiz](https://github.com/dave-code-ruiz) — upstream **elkbledom**.
- [@dext0r](https://github.com/dext0r) — **Yandex Smart Home** интеграция.
- Сообщество **Home Assistant**.
Подробности лицензий — **[ATTRIBUTION.md](ATTRIBUTION.md)**.

## 📜 Лицензия
MIT © **semalinkipay** (см. [LICENSE](LICENSE)). Сторонние компоненты сохраняют свои лицензии.

## ☕ Поддержка проекта
Нашёл полезным? Вопросы, идеи, донат — **Telegram [@cas1noonewin](https://t.me/cas1noonewin)**.
Поставь ⭐ репозиторию — так проект станет полезнее для большего числа людей.
