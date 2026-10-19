# Community-сценарии macOS VM на Windows + AMD

**Проверено:** 19 октября 2026 года  
**Хост проекта:** Windows x86-64, AMD Ryzen 7 6800H (по известной конфигурации ноутбука)  
**Ограничение исследования:** проверены публичные репозитории, их wiki/release/issue/discussion и официальные спецификации. OC4VM release ZIP загружен в локальную папку проекта и проверен по upstream SHA-512; исполняемые файлы и VM не запускались.

## Вывод

Да, community-сценарии существуют. Самый подходящий кандидат для нашего VM-first эксперимента — **DrDonk/OC4VM 3.0.1 + VMware Workstation Pro на Windows**, используя AMD template. Это уже не абстрактный AMD-гайд: maintainer заявляет тесты OC4VM на Ryzen-based HP T740 и Workstation Pro 17.6/25H2 для Windows/Linux, а в комплекте поддерживаются AMD и Intel шаблоны. При этом **точный Ryzen 7 6800H отдельно не подтверждён**. Это проект сообщества, а не официальная VMware/Apple поддержка; запуск на non-Apple ПК также не соответствует описанным ограничениям macOS SLA.

QEMU/WHPX как основной путь выбирать не стоит: QEMU официально поддерживает Windows acceleration через WHPX, но сам OC4VM удалил поддержку QEMU в 2025 году, указав проблемы со стабильностью. Классические OSX-KVM инструкции целятся в Linux/KVM, это не то же самое, что Windows + WHPX, и WSL2 не является доказанным путём запуска такого гостя.

## Кандидат: OC4VM 3.0.1 + VMware Workstation

### Что подтверждено upstream

[OC4VM README](https://github.com/DrDonk/OC4VM) говорит, что проект тестировался на Intel Mac mini 2014 и на AMD Ryzen-based HP T740 с macOS Big Sur, Monterey, Ventura, Sonoma, Sequoia и Tahoe. README перечисляет VMware Workstation Pro 17.6 и 25H2 на Windows и Linux. Поставляются отдельные шаблоны AMD/Intel; README просит выбрать по CPU-хосту. Проект создан прежде всего для VMware Fusion на Mac, но прямо допускает VMware Workstation на PC hardware.

Это подтверждается и более свежими community-отчётами:

- [OC4VM Discussion #9](https://github.com/DrDonk/OC4VM/discussions/9): пользователь сообщил, что поставил, загрузил и запустил Sequoia на Ryzen 9 5950X с VMware. Это отдельный AMD desktop-отчёт, но не Windows/6800H.
- [OC4VM wiki](https://github.com/DrDonk/OC4VM/wiki) обновлена maintainer David Parsons 14 июля 2026 года; перечислены протестированные Big Sur–Tahoe. Wiki помечает себя как work in progress.
- [Maintainer Knowledge Base](https://github.com/DrDonk/OC4VM/wiki/Knowledge-Base) сообщает о проблемах Windows Workstation в ULM/Hyper-V monitor mode: производительность ниже, а CPUID masks могут работать ненадёжно. Для Workstation 25H2 maintainer документировал crash macOS VM, позже помеченный исправленным в 25H2u1.

**Предел точности:** README связывает тесты macOS/AMD с Ryzen-based HP T740, а список поддерживаемых гипервизоров включает Workstation Windows и Linux, однако не описывает подробно, какая именно версия Windows и Workstation применялась на этом HP T740. Поэтому это сильное свидетельство совместимости класса AMD + VMware, но не полная матрица точной комбинации «Windows 11 + конкретный мобильный Ryzen + конкретный Workstation build».

### Latest release и состав

По GitHub Releases API на 2026-10-19 latest release — **3.0.1**, опубликован 20 августа 2026 года. Release page показывает, что tag на 15 коммитов позади текущей `main`, то есть это latest release, но не обязательно самый свежий код.

Release assets по API:

| Asset | Размер | Информация проверки |
|---|---:|---|
| `oc4vm-3.0.1.zip` | 277,768,375 байт (~264.8 MiB) | GitHub API digest SHA-256: `143b947e6d538a8b635a9c919e611705b03356964a7cfcbbe96e923e54dc1dbb`; upstream checksum file SHA-512: `f328a8861c823391b5bf7c0c189b5075c24701721e3a096d3d6c45db8c14b5afc2f4947e3639559f43277225b08f6335846be1b34cb0a3e3e3f3cc4771d5b9e1` |
| `oc4vm-3.0.1.sha512` | 146 байт | опубликованная строка SHA-512 для ZIP; её содержимое прочитано без скачивания архива |

Release notes 3.0.1 говорят, что supplied sparse macOS virtual disk увеличен с 128 GB до 500 GB; `opencore.iso`/`opencore.vmdk` увеличены примерно до 50 MB. Эти числа — виртуальная ёмкость/пакетные файлы, а не подтверждение, что ZIP содержит 500 GB данных. Для обновления существующей VM maintainer требует заменить оба OpenCore boot-файла и предупреждает, что снимки/linked clones до обновления сломают загрузку.

По статическому дереву GitHub upstream source tree содержит Windows EXE tools (`cpuid.exe`, `gum.exe`, `macguest.exe`, `macrecovery.exe`, `recoveryOS.exe`, `vmxtool.exe`), OpenCore ISO, `macos.vmdk`, VMware guest tools ISO (`darwin.iso`, `darwinPre15.iso`) и архив AppleHDA.kext. README также перечисляет OpenCore, Lilu, DebugEnhancer, VirtualSMC, RestrictEvents, AMD_Vanilla, VoodooHDA и другие компоненты. Мы не скачивали release ZIP, поэтому **фактическое содержимое и хеши каждого вложенного файла в asset не проверялись**; указанный инвентарь относится к репозиторию/upstream описанию.

Корневой [LICENSE](https://github.com/DrDonk/OC4VM/blob/main/LICENSE) — MIT на код/проект автора. Это не означает, что лицензированы MIT все bundled dependencies. В README присутствует отдельный VMware `darwin.iso`, поэтому у VMware Tools собственные условия. Перед распространением/упаковкой надо отдельно сверить LICENSE/NOTICE каждого компонента и право перераспространения VMware tools. На macOS installer itself release не следует рассчитывать как на включённый образ: README говорит, что для установки нужно отдельно подключить installation media; [recoveryOS](https://github.com/DrDonk/recoveryOS) получает recovery image с серверов Apple.

Первичные сведения: [release 3.0.1](https://github.com/DrDonk/OC4VM/releases/tag/3.0.1), [release API](https://api.github.com/repos/DrDonk/OC4VM/releases/latest), [README](https://github.com/DrDonk/OC4VM), [LICENSE](https://github.com/DrDonk/OC4VM/blob/main/LICENSE), [recoveryOS README](https://github.com/DrDonk/recoveryOS).

### Совпадает ли 6800H с requirements

OC4VM README требует CPU instructions: **AVX, AVX2, F16C, RDRAND**. AMD product page для Ryzen 7 6800H подтверждает 8C/16T, AMD-V, AVX и AVX2, но в опубликованном списке extensions не указывает F16C/RDRAND. Поэтому:

- AVX, AVX2, AMD-V по официальной спецификации AMD соответствуют.
- Для F16C и RDRAND по открытой странице AMD подтверждения не нашлось. Не будем угадывать по семейству: перед запуском надо будет локально проверить, что CPU и гипервизор выставляют оба флага гостю.
- Убедиться, что AMD SVM/AMD-V включён в UEFI и Windows edition/Workstation build совместим с гипервизором.
- Ryzen 7 6800H — x86-64 Rembrandt/Zen 3+, то есть архитектура не требует эмуляции другого ISA; это плюс, но не гарантия guest boot.

Источник: [AMD Ryzen 7 6800H specs](https://www.amd.com/pt/support/downloads/drivers.html/processors/ryzen/ryzen-6000-series/amd-ryzen-7-6800h.html). Требования OC4VM — в его [README](https://github.com/DrDonk/OC4VM).

### Критичные ограничения

1. **Не точная модель:** нет опубликованного теста OC4VM на Ryzen 7 6800H или ASUS ROG Strix G513RM.
2. **VMware support/legal:** Broadcom официально говорит, что macOS guests поддерживаются только в Fusion VMs, а не Workstation; Apple Tahoe SLA ограничивает использование Apple software Apple-branded systems и разрешённые дополнительные VM экземпляры уже работающим macOS на Apple-branded машине. Значит, OC4VM — технический community workaround, не официальный поддерживаемый/лицензированный Windows-host метод. Это не юридическое заключение.
3. **Риск Windows Hyper-V/VBS:** VMware ULM mode на Windows может ухудшать скорость и ломать/ограничивать CPU masks. Для наших целей надо проверить текущий Windows hypervisor state перед тем, как считать неудачную загрузку проблемой OC4VM.
4. **Нет Apple GPU passthrough:** OC4VM прямо предупреждает, что Apple paravirtualized GPU нельзя использовать на non-Apple hardware. VM будет оценкой старта/установки/среды, не тестом Radeon 680M acceleration.
5. **Tahoe:** maintainer пишет, что Tahoe запускается, но без Liquid Glass из-за отсутствия guest GPU; отдельные актуальные дискуссии 2026 года показывают свежие вопросы по graphics и установке. Не обещать гладкий desktop.
6. **Release assets непросмотрены:** ZIP около 265 MiB и содержит/может содержать исполняемые инструменты; проверены только GitHub metadata, upstream source tree и checksum text. До использования потребуется скачать в проектную папку и отдельно провести статический аудит и сверить checksum, если пользователь подтвердит загрузку.
7. **VMware update:** апдейт Workstation переписывает patched файлы Unlocker. OC4VM сам не требует Unlocker; поэтому не надо добавлять его без причины. Старые сторонние VMware гайды на Unlocker могут быть хрупкими на 26H1.
8. **Проектная свежесть:** 3.0.1 — от 20 августа 2026, на момент просмотра main на 15 commits впереди. Следует сверить, не исправляет ли main блокер, прежде чем принимать release как baseline.

## Другие проверенные проекты и пути

### Workstation-гайды под Windows + Ryzen

[macos-vmware-amd](https://github.com/celltoolz/macos-vmware-amd) сообщает об установленной Monterey 12.7.6 VM на Windows 11 Pro, Ryzen-series host, Workstation Pro 17.5.2, 32 GB RAM. Автор также сообщает об установке Ventura, завершающейся kernel panic, и рекомендует Monterey. Однако это маленький отдельный репозиторий с одним Ryzen без точной модели и без maintainer-уровня тестовой матрицы; для нашей базы лучше OC4VM.

[macos-on-vmware-workstation](https://github.com/aesiddiqui/macos-on-vmware-workstation) — свежий и аккуратно помечающий verified/unverified repo. Автор заявляет end-to-end подтверждение Workstation 26H1 на Windows 11 для Ventura, Sequoia и Tahoe в августе 2026, с evidence и FINDINGS. Но указанная host конфигурация — Intel Core Ultra 7 165H, не AMD. Это хороший источник по Workstation 26H1 и ловушкам версии, но не подтверждение AMD-совместимости.

`DrDonk/unlocker` теперь помечен maintainer как завершённый проект; он говорит, что VMware deprecated macOS support, а Unlocker только открывает отключённые функции VMware и не добавляет AMD CPU capability. OC4VM README говорит, что является альтернативой без patching VMware. Для первого эксперимента OC4VM предпочтительнее старого пути с unlocker.

### VirtualBox

[footstep86/macos-guest-virtualbox](https://github.com/footstep86/macos-guest-virtualbox) создаёт старые Catalina/Mojave/High Sierra VMs; README сообщает, что скрипт тестировался в Cygwin и работает на macOS/WSL, а также может работать на Linux. Это подтверждает скрипт-автоматизацию и получение старых установочных файлов, но **не современный macOS guest на Windows AMD и не запуск самого VirtualBox VM внутри WSL2**. Oracle VirtualBox 7.1 документация называет macOS guest experimental/unsupported и предупреждает о panic на non-Intel CPU. Для нашего VM-first теста этот маршрут хуже и устарел.

### QEMU / OSX-KVM / Linux / WSL2

- В OC4VM changelog за 1 июля 2025 написано: **QEMU support removed as problematic and not stable**. Это конкретный свежий maintainer сигнал против QEMU как главного Windows эксперимента.
- QEMU upstream поддерживает WHPX accelerator на x86_64 Windows, но это общий backend hypervisor, не готовая поддерживаемая macOS VM-конфигурация. Не найдено современного upstream project maintainer отчёта, подтверждающего macOS guest на Ryzen 7 6800H через QEMU/WHPX.
- Основной OSX-KVM класс гайдов ориентирован на Linux/KVM (часто с VFIO/GPU passthrough). Его нельзя объявлять Windows/WHPX совместимым только потому, что QEMU запускается на Windows.
- WSL2/Linux scripts встречаются для подготовки ресурсов, но найти точный доказанный маршрут, где macOS guest реально работает внутри WSL2 VM на Windows/Ryzen, не удалось. Рассматривать WSL2 только как shell для утилит — не как host hypervisor.

## Рекомендуемый первый технический эксперимент

**Статический и затем изолированный тест OC4VM на VMware Workstation Pro 25H2u1 или поддерживаемой текущей версии 25H2/17.6, используя AMD template.** Не ставить Unlocker, не использовать готовый macOS диск из неизвестного источника и не подключать физический диск/Windows раздел.

Порядок проверки после отдельного решения о загрузках:

1. Зафиксировать Windows edition/build, Workstation version, доступную RAM/storage и состояние AMD-V/SVM/Hyper-V/VBS. Не менять security настройки вслепую.
2. Убедиться, что CPU/VM реально предоставляет AVX, AVX2, F16C, RDRAND; AMD официально подтверждает пока только AVX/AVX2/AMD-V.
3. Получить только официальный upstream release и checksum text; проверить SHA-512 до распаковки. Сначала проверить состав ZIP/лицензии и EXE/ISO инвентарь статически.
4. Создать пустую VM в отдельной папке, без доступа к настоящим дискам, сетевым шарам и ноутбучному железу. Использовать AMD template и официально полученный recovery/install media.
5. Первый критерий успеха — дойти до recovery/installer и установить гостевую macOS в виртуальный диск. Второй отдельный критерий — стабильный reboot в установленную систему. Не считать VM-дисплей проверкой Radeon 680M.
6. Сохранить точные логи/VMX/версии и сравнить с maintainer issue/discussion. Если fails — записать точную ошибку и не делать из этого вывод о dual boot.

**Почему этот эксперимент — лучший найденный, но не “безопасный готовый инсталлятор”:** проект имеет maintainer docs, выбранный AMD template, upstream checksum и свидетельства AMD Ryzen работы на Workstation Windows/Linux. В release ZIP 3.0.1 90 записей; после распаковки это около 729 MB. В архиве есть OpenCore ISO/VMDK, VMX/NVRAM-шаблоны, `darwin.iso` и вспомогательные Windows/Linux/macOS бинарники. ZIP и SHA-512 файл сохранены локально в `downloads/third-party/oc4vm-3.0.1/`; SHA-512 совпал с опубликованным upstream значением. Проверены имена путей, traversal и symlink-записи; небезопасных путей и symlink-записей не найдено. Payload не содержит Recovery/полный macOS installer; бинарники и VMware Tools ISO отдельно не запускались и их вложенные лицензии не аудированы. Пользовательский Windows host сообщает активный Hypervisor, что может включить Workstation ULM mode; OC4VM maintainer предупреждает о сниженной производительности и ненадёжности CPUID masks в этом режиме. Лицензионные условия Apple и официальный support Broadcom остаются отдельной границей. Поэтому это лучший найденный кандидат для технического feasibility test, но не готовый продукт и не автоматический “зелёный свет” для установки на ноутбук.

## Официальные границы и источники

- [Broadcom: macOS guests only supported in VMware Fusion VMs](https://knowledge.broadcom.com/external/article/315260).
- [Apple Software License Agreements](https://www.apple.com/legal/sla/) и [macOS Tahoe SLA](https://www.apple.com/legal/sla/docs/macOSTahoe.pdf): non-Apple host use не следует называть официально разрешённым.
- [AMD Ryzen 7 6800H specification](https://www.amd.com/pt/support/downloads/drivers.html/processors/ryzen/ryzen-6000-series/amd-ryzen-7-6800h.html): AMD-V, AVX, AVX2 подтверждены.
- [QEMU WHPX docs](https://www.qemu.org/docs/master/system/whpx.html): Windows x86_64 acceleration, не конкретная поддержка macOS guest.
- [Microsoft Hyper-V supported guest list](https://learn.microsoft.com/windows-server/virtualization/hyper-v/supported-windows-guest-operating-systems-for-hyper-v-on-windows): macOS отсутствует среди поддерживаемых гостей.

## Что осталось неясным

- Какие именно Windows/Workstation build использовались для AMD Ryzen HP T740 maintainer test.
- Выставляются ли F16C/RDRAND конкретно на нашей машине и доступны ли они гостю при выбранном режиме Workstation/Hyper-V.
- Лицензии каждого вложенного бинарного/ISO-файла в release ZIP 3.0.1; внешняя MIT-лицензия проекта не считается автоматически лицензией всех включённых компонентов.
- Сработает ли AMD template на мобильном Rembrandt Ryzen 7 6800H под текущей Windows, несмотря на общие Ryzen test reports.
- На дату чтения latest release 3.0.1 не совпадает с latest main; надо сравнить изменения main с tag перед выбором версии.
