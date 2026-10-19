# Что скачано внутрь проекта

Все бинарные архивы и системные образы лежат под `downloads/`. Эта папка добавлена в `.gitignore`: большие бинарники не попадут в GitHub. Ссылки, версии и контрольные суммы записываем в этот файл.

## OC4VM 3.0.1

- Источник: [официальный GitHub release](https://github.com/DrDonk/OC4VM/releases/tag/3.0.1).
- Папка: `downloads/third-party/oc4vm-3.0.1/`.
- Архив: `oc4vm-3.0.1.zip`, 277,768,375 байт.
- SHA-512 по upstream manifest: `f328a8861c823391b5bf7c0c189b5075c24701721e3a096d3d6c45db8c14b5afc2f4947e3639559f43277225b08f6335846be1b34cb0a3e3e3f3cc4771d5b9e1` — совпал.
- Упаковка содержит 90 записей, после распаковки около 729 MB. Записи путей проверены на `..`, абсолютные пути и symlink; проблем не обнаружено.
- В архиве есть AMD/Intel OpenCore диски и шаблоны VM, `darwin.iso` и вспомогательные Windows/Linux/macOS бинарники.
- Локальная распаковка: `downloads/third-party/oc4vm-3.0.1/extracted/`.
- Содержимое не запускалось. Вложенные сторонние компоненты и лицензии `darwin.iso` отдельно не проверены.

## Пока не скачано

- VMware Workstation installer: официальный Broadcom download требует пользователя Support Portal и подтверждения download terms.
- macOS Recovery: версию выбрали для первого эксперимента — Monterey 12.7.6; скачивание с Apple CDN ещё не запускалось.
- Полный macOS installer/готовый VM: в проекте отсутствуют.

Системные образы и созданные VM не коммитить в Git. Политика лицензии macOS и технический статус community VM описаны в `PLAN.md` и `docs/research/`.
