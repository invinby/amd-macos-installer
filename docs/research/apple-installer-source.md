# Официальный источник macOS installer и локальное хранение

**Проверено:** 2026-10-19 по страницам Apple Support, Apple Software License Agreement для macOS Tahoe 26 и существующей заметке `vm-options.md`.  
**Ничего не скачивалось.** Версия macOS для эксперимента ещё не выбрана, поэтому размер и точный набор файлов надо уточнять после выбора версии.

## Вывод для нашего Windows/AMD хоста

**Официальный массовый workflow получения полного современного macOS installer Apple описывает для совместимого Mac.** Apple предлагает Software Update, App Store или `softwareupdate --fetch-full-installer` в Terminal на Mac; в большинстве случаев Mac, с которого скачивают систему, должен быть совместим с этой версией. Официальное создание bootable installer Apple также выполняется на Mac через `createinstallmedia`.

У Apple есть direct browser download links для некоторых старых выпусков (например, Sierra и старше), но их официальная инструкция всё равно говорит использовать совместимый Mac и далее открыть DMG/PKG на Mac. Это не официальный Windows-инсталлятор и не подтверждённый Apple способ подготовить современную macOS VM на Windows.

Утилита `macrecovery.py`, включённая в OpenCorePkg, может обратиться к Apple Recovery catalog/CDN и получить Recovery-файлы. Это сторонний сценарий сообщества, а не опубликованный Apple Windows installer workflow; Recovery image также не равен полному installer app. Даже если это технически удастся на Windows, это не меняет требования гипервизора и лицензии к размещению macOS-гостя.

Для выбранной VM это означает:

1. Если Mac нет, официальный Apple workflow получения полного installer на Windows не подтверждён. Не закладывать скачивание с зеркала, торрента или непроверенного «готового образа».
2. Если позднее станет доступен совместимый Mac, на нём можно скачать Apple installer и локально подготовить носитель/файлы. Однако по Tahoe SLA право запускать виртуальные экземпляры описано для Apple-branded компьютера, который уже работает под macOS; это не разрешает Windows/AMD-хост только потому, что installer был взят с Apple.
3. Если VM на Windows остаётся только community-техническим экспериментом, зафиксировать это отдельно от официально поддерживаемого и лицензионного пути. Источник Apple сам по себе не делает конфигурацию VM официальной.

## Какие файлы хранить в приватном Git-проекте

### Безопасный состав репозитория

Хранить можно описание процедуры и метаданные, не Apple installer-контент:

- официальные ссылки на Apple Support и применимую лицензию;
- выбранную версию и build number, дату проверки, текстовые инструкции;
- список ожидаемых файлов и их размеры после того, как пользователь скачает их отдельно;
- собственные SHA-256 значения только как метаданные проверки целостности, не сами файлы;
- наши скрипты/настройки, если их отдельные лицензии и содержимое это допускают.

### Не коммитить в Git и не синхронизировать с origin

Для безопасной границы **не помещать** в проект или его Git-историю:

- `Install macOS*.app`, `InstallAssistant.pkg`, `InstallESD.dmg`;
- `BaseSystem.dmg`, `BaseSystem.chunklist`, Recovery image/installer PKG;
- преобразованные `ISO`, `VMDK`, `VDI`, `QCOW2` или архивы этих файлов;
- готовую macOS VM целиком.

Репозиторий «private» всё равно синхронизирует содержимое на удалённый Git-сервис и может дать доступ другим участникам. Текущая SLA Tahoe разрешает одну машинно-читаемую копию Apple Software **только как backup** (с сохранением copyright/proprietary notices) и отдельно запрещает redistribution/sublicensing вне прямо разрешённых случаев. Это не даёт явного разрешения хранить installer/Recovery-контент как общий проектный артефакт или раздавать его команде. Это консервативная инженерная политика по тексту лицензии, не юридическое заключение.

Если сам пользователь временно получает installer для использования в отдельном разрешённом сценарии, хранить его отдельно от Git working tree — например, в локальной папке, которая явно исключена из Git и синхронизации. Перед использованием читать лицензию именно выбранной версии: условия могут отличаться. Не включать личные Apple Account данные, токены или приватные recovery URL в репозиторий.

## Размер и подготовка загрузки

Apple не публикует на приведённых общих страницах постоянный точный размер каждого полного installer. Он зависит от выбранной версии/build и способа загрузки, поэтому цифру в проекте заранее не фиксировать. Для физического bootable installer Apple указывает: 16 GB хватает для большинства прежних выпусков, а 32 GB «more than enough» для любого macOS installer, описанного в статье. Это ёмкость целевого USB, а не гарантия размера скачиваемого комплекта или размера VM.

Для будущего этапа нужно сначала назвать конкретную версию macOS; затем проверить совместимость Mac, который будет источником, и посчитать фактический размер скачанного комплекта. До этого не начинать многогигабайтную загрузку. VM-диск планировать отдельно: размер виртуального диска должен учитывать систему, установочные временные файлы, snapshot/rollback и запас, Apple его не задаёт.

## Официальные процедуры Apple

1. [Apple Support: How to download and install macOS](https://support.apple.com/en-gb/102662) — Software Update, Recovery, Terminal-команда `softwareupdate --fetch-full-installer --full-installer-version`, App Store и браузерные ссылки на старые версии. В статье прямо сказано скачивать с совместимого Mac в большинстве случаев, а для Terminal-команды нужен Mac на macOS Catalina или новее.
2. [Apple Support: Create a bootable installer for macOS](https://support.apple.com/en-ie/101578) — скачать полный installer, затем на Mac запустить встроенный `createinstallmedia`; 32 GB достаточно для любого installer из инструкции, 16 GB — для большинства старых версий.
3. [Apple Support: macOS Recovery на Intel Mac](https://support.apple.com/en-gb/guide/mac-help/mchl338cf9a8/mac) и [на Apple silicon](https://support.apple.com/en-gb/guide/mac-help/mchl82829c17/mac) — встроенный Recovery на Mac для reinstall через интернет; не Windows-загрузчик.
4. [Apple Software License Agreements](https://www.apple.com/legal/sla/) — актуальное соглашение нужно выбирать по версии системы.
5. [Apple macOS Tahoe 26 SLA PDF](https://www.apple.com/legal/sla/docs/macOSTahoe.pdf) — пример условий: заголовок ограничивает использование Apple-branded Systems; п. 2B описывает установки и до двух виртуальных копий на Apple-branded Mac, уже работающем под macOS; п. 2K разрешает одну копию только как backup; п. 2J запрещает redistribute/sublicense вне разрешённых условий.
6. [Acidanthera OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) и [Dortania: Windows installer guide](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/windows-install.html) — где находится `Utilities/macrecovery/` в OpenCorePkg и как community workflow обращается к Apple Recovery downloads. Это не страница Apple Support.

## Практический ответ на вопрос «нужен ли Mac?»

- **Чтобы следовать обычным официальным Apple-инструкциям для полного современного installer — да, нужен совместимый Mac.** Для старых версий Apple даёт ограниченные browser downloads, но инструкция всё равно ориентируется на совместимый Mac.
- **Чтобы технически получить Recovery-файлы через стороннюю community-утилиту на Windows — возможно, но это не Apple-поддерживаемый полный installer workflow.** Не считать скачивание Recovery пакетом macOS, который автоматически установится в любую VM.
- **Чтобы получить официальный Apple VM-сценарий — нужен Apple-branded Mac с macOS по условиям Tahoe SLA.** На текущем Windows/AMD хосте это не меняется от выбора ISO/VMDK/Recovery вместо App Store installer.
