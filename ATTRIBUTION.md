# Attribution / ATTRIBUTION

This project is a **ready-to-install configuration + installer** built and
maintained by **semalinkipay** (Telegram: [@cas1noonewin](https://t.me/cas1noonewin)).
It does NOT reinvent the underlying integrations — it wires together proven
open-source components and patches one of them for reliability.

## Third-party components (keep their own licenses & authors)

### yandex_smart_home (Yandex Smart Home / Alice)
- Upstream: https://github.com/dext0r/yandex_smart_home
- Docs: https://docs.yaha-cloud.ru/
- Author: **@dext0r**
- Version used/tested: **1.1.3**
- The installer downloads it **from upstream** (we do not redistribute its code).

### elkbledom (BLE LED strip integration)
- Upstream: https://github.com/dave-code-ruiz/elkbledom
- Author: **@dave-code-ruiz**
- Version used/tested: **1.6.5**
- **We ship a patched copy** in `custom_components/elkbledom/`. The patch fixes
  an issue where ELK-BLEDOB/ELK-BLEDDM controllers could ignore the power-on
  packet (optimistic state skipped sending it), which made strips look
  "completely unresponsive". The patch is local to `light.py::async_turn_on`.
  All original copyright and license terms of elkbledom still apply to that
  component. If you use it, please also star/support the upstream author.

## Home Assistant
- https://www.home-assistant.io (Apache-2.0). Installed via pip/Docker by the
  installer; not redistributed here.

## Trademark note
Yandex, Alice (Алиса) are trademarks of their respective owners. This project is
not affiliated with or endorsed by Yandex.
