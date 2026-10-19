# Что скачано внутрь проекта

Все бинарные архивы и системные образы лежат под `downloads/`. Эта папка добавлена в `.gitignore`: большие бинарники не попадут в GitHub. Ссылки, версии и контрольные суммы записываем в этот файл.

## OC4VM 3.0.1

- Источник: [официальный GitHub release](https://github.com/DrDonk/OC4VM/releases/tag/3.0.1).
- Папка: `downloads/third-party/oc4vm-3.0.1/`.
- Архив: `oc4vm-3.0.1.zip`, 277,768,375 байт.
- SHA-512 по upstream manifest: `f328a8861c823391b5bf7c0c189b5075c24701721e3a096d3d6c45db8c14b5afc2f4947e3639559f43277225b08f6335846be1b34cb0a3e3e3f3cc4771d5b9e1` — совпал.
- Упаковка содержит 90 записей, после распаковки около 729 MB. Пути проверены на `..`, абсолютные пути и symlink; проблем не обнаружено.
- Есть AMD/Intel OpenCore-диски и шаблоны VM, `darwin.iso` и вспомогательные бинарники. Содержимое не запускалось; лицензии вложенных компонентов отдельно не проверены.
- Локальная распаковка: `downloads/third-party/oc4vm-3.0.1/extracted/`.
- В AMD-шаблоне `macos.vmx` указана `ulm.disableMitigations = "TRUE"`. Эта настройка отключает side-channel mitigations для VM; Broadcom связывает такие меры с защитой от атак вроде Spectre/Meltdown и описывает их отключение как компромисс ради производительности на Windows-хосте с VBS. Для базового опыта не переносить эту строку из готового шаблона; сначала проверять запуск на отдельной копии с защитами по умолчанию. См. [Broadcom KB 315649](https://knowledge.broadcom.com/external/article/315649/vms-with-side-channel-mitigations-enable.html).

## OpenCorePkg 1.0.8

- Источник: [официальный GitHub release](https://github.com/acidanthera/OpenCorePkg/releases/tag/1.0.8).
- Архив: `downloads/third-party/opencorepkg-1.0.8/OpenCore-1.0.8-RELEASE.zip`, 10,544,084 байт.
- SHA-256: `2011e8b7216ecb2645d97ea710df965947edd406846e92050b9bc4190be6d27b` — совпал.
- Распакован в `downloads/third-party/opencorepkg-1.0.8/extracted/`. Проверен исходник `Utilities/macrecovery/macrecovery.py`: скачивает из Apple CDN в заданную папку и сверяет образ по chunklist; запускали вручную после проверки параметров.

## macOS Monterey Recovery

- Выгружен напрямую с Apple CDN утилитой `macrecovery.py` из OpenCorePkg после проверки её исходника.
- Папка: `downloads/macos/Monterey-12-Recovery-2026-10-19/`.
- Файлы: `BaseSystem.dmg` (653,691,436 байт) и `BaseSystem.chunklist` (2,560 байт).
- Chunklist verification: `Image verification complete!`.
- SHA-256 BaseSystem.dmg: `79314D33B881C896C1AFBCFF929FF798B33489C6C4362DC1B20AAED1B6831119`.
- SHA-256 BaseSystem.chunklist: `7FF09B6DA279E30BBA9971AD2F3A98431213B508BF8BE860EF53126824C38908`.
- Это Recovery-среда, не полный установщик. При загрузке гостя установщик получает остальные файлы с серверов Apple.


## QEMU for Windows 11.1.0 (conversion dependency)

- Источник: [страница загрузок QEMU](https://www.qemu.org/download/#windows) направляет на официально упомянутые Windows builds Stefan Weil.
- Установщик: `downloads/third-party/qemu-windows-11.1.0/qemu-w64-setup-20260811.exe`, 206,615,928 байт.
- SHA-512: `5BCF9EED634E8575A37B74F445AF41A2FE4106DA512D0C30C368301D4C105037FDFAB40A5287367A28A957624CDDEBBC8C07E16C88AB6634F554CDF3D16BF543` — совпал с manifest рядом.
- SHA-256: `F98A8AEB5F7FAEA9765B6DEE28316C266CD179D80354A2FED8E50176F9A2E59F` — независимо совпал с manifest пакета WinGet `SoftwareFreedomConservancy.QEMU`.
- Authenticode подпись показывает издателя Universität Mannheim, но срок сертификата закончился в 2023; Windows status `UnknownError`. Установщик пока не запускался. Сборка нужна только для qemu-img, чтобы подготовить Recovery VMDK.
## Пока не скачано

- VMware Workstation installer: пока не скачан. Официальный Broadcom download перенаправляет на вход, требует принять условия загрузки и иногда отдельную Trade Compliance проверку.
- Полный macOS installer и рабочая VM пока отсутствуют.

Системные образы и созданные VM не коммитить в Git.
