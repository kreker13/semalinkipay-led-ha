#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
#  semalinkipay-led-ha  —  кроссплатформенный авто-установщик стека
#  Home Assistant + elkbledom (patched) + yandex_smart_home + готовые конфиги.
#
#  Запуск:
#     Linux/macOS:  python3 install.py
#     Windows:      py -3 install.py     (или python install.py)
#
#  Скрипт НЕДАСТРУКТИВЕН: существующие файлы бэкапит в .semlinki-backup-<ts>.
#  Всё ставится в выбранную тобой папку конфигурации Home Assistant.
#
#  Автор/поддержка/донат: semalinkipay — Telegram @cas1noonewin
# =============================================================================
import os
import sys
import shutil
import subprocess
import datetime
import textwrap

BANNER = r"""
  ____                                  _ _   _       _
 / ___|  ___ _ __ ___  _ __  _   (_)_ __(_| | (_) __ _| |__
 \___ \ / _ \ '_ ` _ \| '_ \| | | | | '__| | |/ |/ _` | '_ \
  ___) |  __/ | | | | | |_) | |_| | | |  | |   | (_| | |_) |
 |____/ \___|_| |_| |_| .__/ \__,_|_|_|  |_|_|\_|\__,_|_.__/
                      |_|   BLE LED strips + Alice (Yandex)
                         installer by semalinkipay
                         Telegram: @cas1noonewin (вопросы/донат)
"""

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_CONFIGS = os.path.join(THIS_DIR, "configs")
REPO_ELKDOM = os.path.join(THIS_DIR, "custom_components", "elkbledom")
YANDEX_REPO = "https://github.com/dext0r/yandex_smart_home.git"
YANDEX_TAG = "1.1.3"

MIN_PY = (3, 11)


def hi():
    print(BANNER)


def ask(prompt, default=None, confirm=False):
    if confirm:
        s = input(f"{prompt} [y/N]: ").strip().lower()
        return s in ("y", "yes", "д", "да")
    s = input(f"{prompt}" + (f" [{default}]: " if default is not None else ": ")).strip()
    return s or (default if default is not None else "")


def run(cmd, shell=False, check=True, cwd=None, env=None):
    print(f"    $ {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    return subprocess.run(cmd, shell=shell, check=check, cwd=cwd, env=env)


def backup(path):
    if not os.path.exists(path):
        return
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = f"{path}.semlinki-backup-{ts}"
    shutil.move(path, dst)
    print(f"    ! существовавшее сохранено: {os.path.basename(dst)}")


def default_config_dir():
    home = os.path.expanduser("~")
    if os.name == "nt":
        return os.path.join(home, "homeassistant")
    # Linux/macOS: типичный путь HA Core
    return os.path.join(home, ".homeassistant")


def detect_os():
    if os.name == "nt":
        return "Windows"
    if sys.platform == "darwin":
        return "macOS"
    return "Linux"


def preflight():
    print("\n== 1) Проверка окружения ==")
    v = sys.version_info
    print(f"    Python {v.major}.{v.minor}.{v.micro} · ОС: {detect_os()}")
    if (v.major, v.minor) < MIN_PY:
        sys.exit(f"    Нужно Python {MIN_PY[0]}.{MIN_PY[1]}+. Обнови Python и повтори.")
    print(f"    Папка репозитория: {THIS_DIR}")
    for p in (REPO_CONFIGS, REPO_ELKDOM):
        if not os.path.isdir(p):
            sys.exit(f"    Не нашёл обязательную папку {p}. Запускай install.py из корня репо.")


def choose_method():
    print("\n== 2) Как ставим Home Assistant? ==")
    osw = detect_os()
    if osw == "Windows":
        print("    Windows: HA Core нативно не поддерживается. Рекомендуем Docker Desktop (WSL2).")
        print("      1) Docker (рекомендуется на Windows)")
        print("      2) Всё равно HA Core в venv (неофициально, на свой страх) — см. README")
        return "docker" if ask("    Выбор", default="1") in ("1", "docker") else "core"
    print("      1) HA Core в виртуальном окружении + сервис (рекомендуется на Linux)")
    print("      2) Docker (удобно, если уже есть Docker)")
    return "core" if ask("    Выбор", default="1") in ("1", "core") else "docker"


def pick_config_dir():
    print("\n== 3) Папка конфигурации Home Assistant ==")
    d = default_config_dir()
    got = ask("    Путь к config-папке HA", default=d)
    d = os.path.abspath(os.path.expanduser(got))
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(d, "custom_components"), exist_ok=True)
    print(f"    Готово: {d}")
    return d


def install_custom_components(cfg_dir):
    print("\n== 4) Кладём custom-компоненты ==")
    cc = os.path.join(cfg_dir, "custom_components")

    # 4a. патченный elkbledom (из нашего репо)
    dst = os.path.join(cc, "elkbledom")
    if os.path.isdir(dst):
        backup(dst)
    shutil.copytree(REPO_ELKDOM, dst)
    print("    elkbledom (патченный semalinkipay) → готов")

    # 4b. yandex_smart_home — тянем с UPSTREAM (не перевыкладываем чужой код)
    ydst = os.path.join(cc, "yandex_smart_home")
    if os.path.isdir(ydst):
        print("    yandex_smart_home уже есть — пропускаю обновление.")
        return
    if not shutil.which("git"):
        print("    ! git не найден — скачай yandex_smart_home вручную (см. README, шаг «Интеграции»).")
        return
    print("    Клонирую yandex_smart_home с upstream…")
    tmp = os.path.join(cfg_dir, ".semlinki-tmp-ysh")
    try:
        run(["git", "clone", "--depth", "1", "--branch", YANDEX_TAG, YANDEX_REPO, tmp], check=True)
        src = os.path.join(tmp, "custom_components", "yandex_smart_home")
        if not os.path.isdir(src):
            # у upstream layout может отличаться — ищем домен
            for root, dirs, _ in os.walk(tmp):
                if "yandex_smart_home" in dirs:
                    src = os.path.join(root, "yandex_smart_home")
                    break
        shutil.copytree(src, ydst)
        print("    yandex_smart_home → готов")
    except subprocess.CalledProcessError:
        print(f"    ! Не удалось склонировать тег {YANDEX_TAG}. Скачай вручную (см. README).")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def install_configs(cfg_dir):
    print("\n== 5) Кладём готовые конфиги (шаблоны) ==")
    for name in ("configuration.yaml", "template.yaml", "scripts.yaml",
                 "automations.yaml", "yandex_smart_home.yaml"):
        src = os.path.join(REPO_CONFIGS, name)
        dst = os.path.join(cfg_dir, name)
        if os.path.exists(dst):
            ans = ask(f"    {name} уже существует — перезаписать?", default="n", confirm=True)
            if not ans:
                print("      сохраняю твоё, пропускаю.")
                continue
            backup(dst)
        shutil.copy2(src, dst)
        print(f"    {name} → ok")
    print("\n    ВАЖНО: в template.yaml лежат два placeholder-id (light.neon_phys /")
    print("    light.led_phys). После старта HA добавь ленты в UI и приведи их")
    print("    entity_id к этим значениям (или поправь template.yaml).")


def make_venv_and_run_core(cfg_dir):
    print("\n== 6) Установка HA Core (venv) ==")
    venv_dir = os.path.join(cfg_dir, ".venv")
    if not os.path.isdir(venv_dir):
        run([sys.executable, "-m", "venv", venv_dir])
    py = os.path.join(venv_dir, "bin", "python") if os.name != "nt" \
        else os.path.join(venv_dir, "Scripts", "python.exe")
    print("    Ставлю homeassistant (pip)… может занять время.")
    run([py, "-m", "pip", "install", "--upgrade", "pip"])
    run([py, "-m", "pip", "install", "homeassistant"])
    systemd = write_systemd_unit(py, cfg_dir) if detect_os() == "Linux" else None
    print("\n== ГОТОВО ==")
    print(f"    Запуск вручную:  {py} -m homeassistant --config {cfg_dir}")
    if systemd:
        print(f"    Как сервис:      systemctl --user start home-assistant")
        print(f"                   (unit: {systemd})")
    print_next_steps(cfg_dir)


def write_systemd_unit(py, cfg_dir):
    print("    Пишу systemd-user unit…")
    units = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(units, exist_ok=True)
    path = os.path.join(units, "home-assistant.service")
    content = textwrap.dedent(f"""\
        [Unit]
        Description=Home Assistant (semlinki-led-ha)
        After=network-online.target bluetooth.service

        [Service]
        ExecStart={py} -m homeassistant --config {cfg_dir}
        Restart=on-failure
        RestartSec=5

        [Install]
        WantedBy=default.target
    """)
    if os.path.exists(path):
        backup(path)
    with open(path, "w") as f:
        f.write(content)
    try:
        run(["systemctl", "--user", "daemon-reload"], check=False)
        run(["systemctl", "--user", "enable", "home-assistant"], check=False)
    except Exception:
        pass
    return path


def make_docker_compose(cfg_dir):
    print("\n== 6) Установка через Docker ==")
    if not shutil.which("docker"):
        print("    ! docker не найден в PATH. Установи Docker Desktop (Windows) или Docker (Linux),")
        print("      затем повтори:  python3 install.py  (режим Docker).")
        print_next_steps(cfg_dir)
        return
    compose = os.path.join(cfg_dir, "docker-compose.yml")
    if os.path.exists(compose):
        backup(compose)
    with open(compose, "w") as f:
        f.write(textwrap.dedent(f"""\
            services:
              homeassistant:
                container_name: homeassistant
                image: "ghcr.io/home-assistant/home-assistant:stable"
                volumes:
                  - {cfg_dir}:/config
                  - /etc/localtime:/etc/localtime:ro
                restart: unless-stopped
                privileged: true
                network_mode: host
        """))
    print(f"    docker-compose.yml → {compose}")
    print("    Поднимаю контейнер…")
    try:
        run(["docker", "compose", "up", "-d"], cwd=cfg_dir, check=True)
    except subprocess.CalledProcessError:
        print("    ! Не вышло. Проверь, что Docker запущен. Затем: docker compose up -d")
    print_next_steps(cfg_dir)


def print_next_steps(cfg_dir):
    print("\n" + "=" * 60)
    print("  ЧТО ДАЛЬШЕ (ручные шаги в интерфейсе Home Assistant):")
    print("=" * 60)
    print("  1) Открой http://localhost:8123 и пройди onboarding.")
    print("  2) Настройки → Устройства и сервисы → Добавить:")
    print("       • интеграция «ElkBLEDOM» сама найдёт ленты MELK*/ELK* по Bluetooth;")
    print("         включи Bluetooth-адаптер и держи ленту рядом.")
    print("       • интеграция «Yandex Smart Home» — попросит Long-Lived Access Token")
    print("         (профиль → Безопасность → Long-lived access token).")
    print("  3) Добавь ленты и приведи их entity_id к light.neon_phys / light.led_phys")
    print("     (или поправь template.yaml). НЕ меняй light.neon / light.led.")
    print("  4) В приложении «Умный дом с Алисой» привяжи устройства к Yandex.")
    print("  5) Скажи: «Алиса, включи светодиодную ленту».")
    print("-" * 60)
    print("  Вопросы и донат → Telegram @cas1noonewin · semalinkipay")
    print("  Config-папка:", cfg_dir)
    print("=" * 60)


def main():
    hi()
    try:
        preflight()
        method = choose_method()
        cfg = pick_config_dir()
        if not ask("\nПродолжить установку?", default="y", confirm=True):
            print("    Отменено пользователем."); return
        install_custom_components(cfg)
        install_configs(cfg)
        if method == "docker":
            make_docker_compose(cfg)
        else:
            make_venv_and_run_core(cfg)
    except KeyboardInterrupt:
        print("\n    Прервано. Ничего страшного — перезапусти install.py.")
    except subprocess.CalledProcessError as e:
        print(f"\n    Ошибка команды ({e}). Скроллингом выше видно какую. См. README/troubleshooting.")
        print("    Вопросы: Telegram @cas1noonewin")


if __name__ == "__main__":
    main()
