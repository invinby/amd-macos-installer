# AMD ноутбуки и macOS: обзор готовых решений

Дата проверки: 2026-10-19  
Объект: ASUS ROG Strix G513RM, Ryzen 7 6800H (Rembrandt / Zen 3+), Radeon 680M (RDNA 2 iGPU), RTX 3060 Laptop (Ampere), MediaTek MT7922 / RZ616, Realtek RTL8125 2.5GbE.  
Тип заметки: read-only исследование публичных первичных источников.

## Короткий вывод

Готовые компоненты существуют, но полноценного установщика, который превращает AMD-ноутбук в полнофункциональный Mac, не найдено. Есть генераторы/сборщики OpenCore EFI, помощники для создания installer и kernel patches. Они автоматизируют EFI и носитель, но не создают драйвер неподдерживаемой графики и не устраняют ограничения ноутбучной схемы.

Для Ryzen 6000 mobile есть готовая EFI близкого RedmiBook Pro 2022 с Ryzen 5 6600H / Ryzen 7 6800H. Автор заявляет загрузку и тесты Catalina и Ventura, но прямо указывает, что iGPU не ускоряется, Wi-Fi и Bluetooth отсутствуют, тачпад, яркость и сон проблемные, запуск нестабилен. Автор помечает EFI как несовершенную и почти заброшенную. Это доказательство загрузки на похожем Rembrandt ноутбуке, но не полноценной работы с ускорением.

Для G513RM главный блокер — Radeon 680M: задача NootedRed по RDNA 1/2 iGPU остаётся открытой, с высоким объёмом работ, статусом backlog/blocked и без ETA. Свежие коммиты по Phoenix не доказывают поддержку Rembrandt. RTX 3060 Laptop (Ampere) не поддерживается macOS. Wi-Fi MT7922 не покрыт найденными драйверами macOS. Ethernet может быть полезен, но конкретный драйвер и device ID ещё надо подтвердить.

## Готовые установочные решения

| Проект | Что реально автоматизирует | Ограничения |
|---|---|---|
| [OpCore Simplify](https://github.com/lzhoang2801/OpCore-Simplify) | Проверка отчёта о железе, подбор настроек/ACPI/kexts и генерация стартовой EFI; работает на Windows. Отдельные USB/Recovery workflow относятся к подготовке installer, а не к VM. | Это EFI builder, не драйверогенератор. README перечисляет AMD APU семейства Vega (Ryzen 1000–5000, 7x30), но не Rembrandt 680M. Автор намеренно не форсирует несовместимую GPU ради медленного VESA. |
| [UnPlugged](https://github.com/corpnewt/UnPlugged) | Bash-скрипт для запуска из macOS Recovery и подготовки полного installer. | Не Windows-утилита, не VM-гипервизор и не решение аппаратной совместимости. Для первого VM-этапа не нужен. |
| [OpenCore Auxiliary Tools (OCAT)](https://github.com/ic005k/OCAuxiliaryTools) | GUI для редактирования/проверки config.plist, обновления OpenCore/kexts, генерации EFI-папки из настроенного конфига. | Конфигуратор, не полноценный hardware-aware мастер и не решение для отсутствующего драйвера. Dortania предостерегает от слепой зависимости от configurators. |
| [AMD Vanilla OpenCore patches](https://github.com/AMD-OSX/AMD_Vanilla) | Kernel patches для запуска macOS на AMD CPU, включая Ryzen 17h/19h. | Не GPU-драйвер. Не делает ноутбучные AMD CPUs официально совместимыми по Dortania и не поддерживает автоматически 680M. |
| [HackinOS OpenCore Builder](https://github.com/ihackinOS/OpenCoreBuilder) | Небольшой сторонний проект заявляет GUI-сборку EFI и профили AMD/Intel. | Не найдено убедительного подтверждения поддержки Ryzen 6000 mobile / Rembrandt / G513RM. Нужен отдельный аудит исходников и реального результата. |
| [Dortania OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/) | Подробная ручная документация по OpenCore, EFI и установке. | Не мастер установки; требует знания точного железа и базовой командной строки. |

Ключевые ссылки:

- [Dortania: Hardware Limitations](https://dortania.github.io/OpenCore-Install-Guide/macos-limits.html): AMD laptop CPUs не поддержаны основным гайдом; у AMD есть ограничения функций; большинство laptop dGPU имеют switchable-graphics разводку, несовместимую с macOS.
- [Dortania: AMD Ryzen guide](https://dortania.github.io/OpenCore-Install-Guide/AMD/zen.html): kernel patches, обязательные параметры и ручная адаптация под CPU.
- [Dortania: prerequisites](https://dortania.github.io/OpenCore-Install-Guide/prerequisites.html): нужно знать CPU, GPU, NVMe, Ethernet, WLAN/Bluetooth и иметь базовые навыки терминала.
- [OpCore Simplify README](https://github.com/lzhoang2801/OpCore-Simplify/blob/main/README.md): перечень поддерживаемого железа и разделение EFI build / создания USB.
- [OpCore Simplify issue #644](https://github.com/lzhoang2801/OpCore-Simplify/issues/644): GPU spoofing не даёт acceleration; maintainer говорит, что цель проекта — строить EFI только для совместимого железа.

## CPU и kernel patches

[AMD-OSX/AMD_Vanilla](https://github.com/AMD-OSX/AMD_Vanilla) — reusable компонент. Это бинарные kernel patches для AMD CPU, а не драйвер AMD вообще. Поддерживаются семейства 15h/16h/17h/19h, включая Ryzen; патч числа ядер настраивается под процессор. Нужны свежие OpenCore и соответствующий CPU-info quirk.

Патчи могут решить часть вопроса «дойдёт ли kernel до загрузки на Ryzen», но не обеспечивают графику, сон, питание, ACPI, экран, Wi-Fi и ввод. Dortania перечисляет ограничения AMD macOS: AppleHV-зависимые виртуальные машины, часть Adobe/MKL-программ, 32-bit и нестабильность некоторых приложений.

Вывод: готовые CPU kernel patches существуют; писать собственное ядро с нуля не требуется на старте. Для нашего G513RM наиболее явный пробел — графический драйвер и ноутбучная интеграция.

## Radeon 680M / Rembrandt / NootedRed

- [NootedRed](https://github.com/ChefKissInc/NootedRed) — Lilu plugin/kext для AMD graphics; README называет проект активной исследовательской разработкой и предупреждает о сбоях.
- [Issue #285: Ryzen 7 6800H + 680M Rembrandt](https://github.com/ChefKissInc/NootedRed/issues/285): запрос поддержки закрыт как duplicate общей задачи RDNA iGPU; готового драйвера или подтверждения установки там нет.
- [Issue #92: RDNA 1/2 iGPU support](https://github.com/ChefKissInc/NootedRed/issues/92): на дату проверки остаётся открытой; milestone v2.0.0 без ETA, effort High; в истории указаны blocked (август 2026) и более поздний коммит по Phoenix. Phoenix-коммит не подтверждает поддержку Rembrandt 680M.
- [NootRX](https://github.com/ChefKissInc/NootRX) предназначен для AMD RDNA 2 discrete GPU. Это не поддержка 680M iGPU. Maintainer отдельно объяснял, что RDNA iGPU — самостоятельная большая работа.
- [Dortania AMD GPU Buyers Guide](https://dortania.github.io/GPU-Buyers-Guide/modern-gpus/amd-gpu.html) описывает для NootedRed экспериментальную поддержку Vega APU, не готовую поддержку Rembrandt RDNA 2 iGPU.
- [NootedRed releases](https://github.com/ChefKissInc/NootedRed/releases): текущие релизы/fallback models не являются доказательством ускорения 680M.

Важно разделять ступени:

1. EFI собралась.
2. macOS installer загрузился — возможно, через VESA без Metal.
3. macOS установилась — система может оставаться очень медленной.
4. 680M аппаратно ускоряется — отдельно подтверждённые драйвер, Metal и рабочее отображение.
5. Ноутбук пригоден каждый день — дополнительно проверены экран/яркость, Wi-Fi, аудио, клавиатура, тачпад, сон/пробуждение, батарея, температура и стабильность.

«Дошёл до установщика» не означает «есть драйвер», а EFI-папка не означает совместимый GPU.

## Проброс видеокарты и собственный драйвер (проверено 20 октября 2026)

Снял Hardware ID с этого ноутбука через Windows PnP:

- AMD Radeon 680M: 1002:1681 (Rembrandt / RDNA 2 iGPU).
- NVIDIA RTX 3060 Laptop: 10DE:2520 (Ampere).

Запущенный QEMU сейчас показывает гостю vmware-svga — виртуальный видеоадаптер из аргументов запуска. Это не проброс 680M. Текущая медлительность идёт прежде всего от QEMU TCG: он исполняет CPU-код гостя программно, поэтому настройка видеокарты сама по себе это не исправит.

### Что даёт каждый маршрут

| Маршрут | Что он может дать | Что ему мешает здесь |
| --- | --- | --- |
| QEMU WHPX | Ускорение CPU-виртуализации на Windows | Предыдущая попытка завершилась Unexpected VP exit code 4; это надо отдельно отлаживать. WHPX не пробрасывает Radeon и не даёт macOS-драйвер. |
| PCI passthrough 680M | Доступ гостя к физическому устройству в некоторых гипервизорах/ОС-хостах | Не решает отсутствие рабочего macOS-драйвера для Rembrandt. Для Windows + WHPX готовый поддерживаемый маршрут passthrough не установлен. |
| VMware SVGA / виртуальная 3D-графика | Может ускорить только то, что поддерживают гипервизор и guest-драйвер | Не тождественно Radeon 680M/Metal. Нельзя считать рабочим ускорением macOS, пока в госте не подтверждены framebuffer, QE/Metal и нагрузочный тест. |
| Загрузить драйвер в macOS | Единственный путь к нативному ускорению этой iGPU | Готового драйвера для 680M не найдено; нужен полноценный порт графического стека. |

### Состояние готовых компонентов

- NootedRed issue #92 (https://github.com/ChefKissInc/NootedRed/issues/92) остаётся открытой задачей поддержки RDNA 1/2 iGPU; в актуальной карточке указаны высокий объём работ и заблокированный статус. Issue #285 (https://github.com/ChefKissInc/NootedRed/issues/285) прямо посвящена Ryzen 7 6800H / Radeon 680M и закрыта как дубль этой общей задачи.
- NootRX (https://github.com/ChefKissInc/NootRX) — проект для дискретных RDNA 2 карт; его нельзя просто подключить как драйвер 680M.
- Найден MetalGPUDrivers (https://github.com/winkleplex10-bit/MetalGPUDrivers), небольшой исследовательский репозиторий. Его README сообщает, что начат отдельный контроллер для другой RDNA 2 APU (Raphael 1002:164E), но пока нет GFX-командного кольца, AIR→gfx1036 и QE/Metal; целевая ОС проекта — macOS 26. Это не готовый драйвер 680M. У репозитория в README лицензия помечена TBD, поэтому код нельзя переносить в наш проект до выяснения прав.

### Реальный план по 680M

Сначала добиваем проверяемый VM-экран, отдельно пробуем разобраться с WHPX и снимаем гостевой профиль видеоустройства. Для настоящего драйвера нужен отдельный проект и стенд на самом ноутбуке; VM с vmware-svga его не проверит. Этапы собственного порта: получить логи/PCI и VBIOS/ATOM сведения → запустить устройство и firmware/PSP → вывести простой framebuffer → поднять управление питанием и дисплейным блоком Rembrandt → только затем исследовать IOAccelerator/Metal и командную очередь. «Картинка через framebuffer» ещё не означает аппаратное ускорение Metal.

RTX 3060 проблему не закрывает: это отдельное NVIDIA Ampere устройство, а macOS-драйвера для него нет; плюс на ноутбуке надо отдельно установить физическую схему дисплейного MUX. Для QEMU первым разумным ускорением остаётся починить CPU backend WHPX, а не передавать неподдерживаемую GPU.

## NVIDIA RTX 3060 и дисплейная схема

[Dortania NVIDIA GPU Buyers Guide](https://dortania.github.io/GPU-Buyers-Guide/modern-gpus/nvidia-gpu.html) относит RTX 3060 / Ampere к неподдерживаемым macOS GPU: драйверов не было даже для High Sierra. [Hardware Limitations](https://dortania.github.io/OpenCore-Install-Guide/macos-limits.html) предупреждает, что большинство laptop dGPU подключены через switchable graphics/Optimus и не пригодны для внутренней матрицы macOS.

Для G513RM RTX 3060 нельзя считать обходом отсутствия 680M-драйвера. Её, вероятно, придётся отключать. Точный маршрут сигнала матрицы, MUX/Advanced Optimus и внешних HDMI/USB-C выходов надо проверить для конкретной комплектации.

## Сеть и прочая периферия

- Wi-Fi/BT инвентаря — MediaTek MT7922 / RZ616. В [Dortania Wireless Buyers Guide: unsupported chipsets](https://dortania.github.io/Wireless-Buyers-Guide/unsupported.html) MT7922 не указана. [OpenIntelWireless/itlwm](https://github.com/OpenIntelWireless/itlwm) — драйвер Intel, не MediaTek. Первичный macOS-kext с подтверждённой поддержкой MT7922/RZ616 в поиске не найден.
- Проводная сеть — Realtek 2.5GbE. Она может быть полезнее Wi-Fi для установки, но в этом исследовании не подтверждены точный chip/device ID и конкретный совместимый драйвер.
- Клавиатура, I2C/HID тачпад, аудиокодек, камера, яркость, сон, USB mapping, батарея и power management требуют отдельных device ID/ACPI исследований. Одного имени G513RM недостаточно из-за вариаций комплектаций.

## Готовая EFI для близкого Ryzen 6000 ноутбука

[copws/RedmiBookPro2022-Ryzen-Hackintosh-EFI](https://github.com/copws/RedmiBookPro2022-Ryzen-Hackintosh-EFI) — самый прямой найденный Rembrandt пример. Автор указывает Ryzen 5 6600H / Ryzen 7 6800H, OpenCore 0.9.4 и тесты Catalina 10.15 и Ventura 13.6.

Автор перечисляет неработающими большую часть функций iGPU, Wi-Fi, Bluetooth, тачпад, яркость, микрофон, iCloud; сон неизвестен/проблемный, есть случайные kernel panic и клавиатурные сбои. Автор пишет, что EFI крайне несовершенна, почти забросил её и не рекомендует для основной системы. Это исследовательский артефакт по загрузке на похожем CPU, не переносимая EFI для ASUS и не решение ускорения.

В targeted GitHub/Dortania поиске готовая подтверждённая EFI именно для ASUS ROG Strix G513RM с отчётом об ускоренной 680M не обнаружена. Похожая спецификация не делает EFI переносимой: ACPI/USB, разводка дисплея, WLAN, аудио, тачпад и BIOS отличаются. Найденные community обсуждения G513RM описывают незавершённые попытки, но не доказанный полный результат.

## Рекомендации для плана проекта

1. Первым экспериментом воспроизвести доступную Rembrandt EFI или минимальную загрузку на отдельном диске/USB, не трогая Windows.
2. Первый milestone назвать честно: сбор аппаратного отчёта и воспроизводимая EFI/загрузка, не «полноценный macOS».
3. Вести матрицу статусов: обнаружено → EFI собралась → installer загрузился → установка завершена → драйвер/ускорение → sleep/resume → повседневная стабильность.
4. Отдельно изучить исходники/задачу NootedRed по RDNA iGPU до решения писать собственный драйвер. Это reverse engineering, не обычный kext glue.
5. Сравнить будущий wizard с OpCore Simplify, UnPlugged и OCAT; использовать существующие части там, где они закрывают задачу, а свой продуктовый слой строить вокруг понятного отчёта, совместимости и безопасного сценария для новичка.
6. До переноса сторонних EFI/kext/source проверить лицензии. NootedRed использует ChefKiss Open Knowledge License; README содержит ограничения, в том числе на использование для AI training/development. Не копировать чужие бинарники/EFI автоматически.

## Охват и неизвестные места

Проверены на 2026-10-19: Dortania OpenCore Install Guide, Hardware Limitations, AMD guide, GPU Buyers Guide и Wireless Buyers Guide; GitHub README/issues/projects AMD_Vanilla, ChefKissInc/NootedRed, ChefKissInc/NootRX, lzhoang2801/OpCore-Simplify, corpnewt/UnPlugged, OCAuxiliaryTools, HackinOS OpenCoreBuilder и RedmiBookPro2022 EFI; targeted searches по G513RM, 6800H, 680M, Rembrandt, OpenCore и macOS. Искались wizard/installer/EFI builder, kernel patches, GPU kext и конкретные laptop EFI.

Это не доказывает, что не существует закрытых, удалённых, неиндексируемых или неанглоязычных EFI. Охват — открытые индексируемые источники, не каждый форум, видео, Telegram или Discord. Не выполнены: бинарный аудит всех EFI; запуск macOS на G513RM; проверка NootedRed на реальном железе; измерение Metal/ускорения; разбор ACPI/DSDT и схемы платы; точная идентификация Ethernet/аудио/панели/MUX по live hardware report; физические тесты сна, USB, температуры и батареи; юридическая экспертиза лицензий. Формулировка «готовой EFI нигде нет» ограничена именно охваченным поиском.

## Источники

1. [Dortania OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/)
2. [Dortania Hardware Limitations](https://dortania.github.io/OpenCore-Install-Guide/macos-limits.html)
3. [Dortania AMD Ryzen guide](https://dortania.github.io/OpenCore-Install-Guide/AMD/zen.html)
4. [Dortania NVIDIA GPU Buyers Guide](https://dortania.github.io/GPU-Buyers-Guide/modern-gpus/nvidia-gpu.html)
5. [Dortania Wireless Buyers Guide](https://dortania.github.io/Wireless-Buyers-Guide/unsupported.html)
6. [AMD-OSX/AMD_Vanilla](https://github.com/AMD-OSX/AMD_Vanilla)
7. [ChefKissInc/NootedRed](https://github.com/ChefKissInc/NootedRed)
8. [NootedRed issue #92: RDNA iGPU support](https://github.com/ChefKissInc/NootedRed/issues/92)
9. [NootedRed issue #285: Ryzen 7 6800H / 680M](https://github.com/ChefKissInc/NootedRed/issues/285)
10. [ChefKissInc/NootRX](https://github.com/ChefKissInc/NootRX)
11. [lzhoang2801/OpCore-Simplify](https://github.com/lzhoang2801/OpCore-Simplify)
12. [OpCore Simplify issue #644: unsupported GPU/VESA](https://github.com/lzhoang2801/OpCore-Simplify/issues/644)
13. [corpnewt/UnPlugged](https://github.com/corpnewt/UnPlugged)
14. [ic005k/OCAuxiliaryTools](https://github.com/ic005k/OCAuxiliaryTools)
15. [ihackinOS/OpenCoreBuilder](https://github.com/ihackinOS/OpenCoreBuilder)
16. [copws/RedmiBookPro2022-Ryzen-Hackintosh-EFI](https://github.com/copws/RedmiBookPro2022-Ryzen-Hackintosh-EFI)
17. [OpenIntelWireless/itlwm](https://github.com/OpenIntelWireless/itlwm)
18. [ASUS G513RM support page](https://www.asus.com/us/supportonly/g513rm/helpdesk_service_guide/)

19. [MetalGPUDrivers README: незавершённый Raphael RDNA2 iGPU прототип](https://github.com/winkleplex10-bit/MetalGPUDrivers)
