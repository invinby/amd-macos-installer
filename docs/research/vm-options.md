# macOS в виртуальной машине на Windows с Ryzen 7 6800H

**Проверено:** 19 октября 2026 года  
**Цель:** выбрать безопасный и технически осмысленный способ проверить загрузочную сборку в VM до экспериментов с dual boot.  
**Границы:** исследованы официальные документы Apple, Microsoft, Oracle, Broadcom/VMware и QEMU. Состояние скачанных файлов и отдельной рабочей VM-копии описано ниже; неподтверждённые исполняемые файлы не запускались.

## Короткий вывод

Для Windows-ПК с Ryzen 7 6800H не обнаружен официальный, поддерживаемый производителями сценарий запуска macOS-гостя. Ограничение не в том, что процессор AMD сам по себе не умеет виртуализацию: процессор Ryzen поддерживает AMD-V, а QEMU способен использовать Windows Hypervisor Platform на x86_64 Windows. Проблема в поддержке гостевой macOS и лицензии Apple: текущая лицензия Tahoe ограничивает использование Apple Software Apple-branded Systems; разрешённые виртуальные экземпляры привязаны к Apple-branded компьютеру, который уже работает под macOS.

Значит, VM на этом Windows-ноутбуке — **экспериментальный community-сценарий**. Мы его уже проверяем с AMD-шаблоном OC4VM и Monterey Recovery. Успешная загрузка проверит конкретную VM-конфигурацию и загрузчик, но не докажет совместимость macOS с настоящей Radeon 680M, Wi-Fi, сном или dual boot на ASUS.

## Сравнение вариантов

| Вариант | Что официально заявлено | Вывод для этого проекта |
|---|---|---|
| Hyper-V | Microsoft поддерживает перечисленные Windows, Linux и FreeBSD гости. macOS в списках поддерживаемых гостей не указана. Hyper-V требует Windows Pro/Enterprise, SLAT, аппаратную виртуализацию и минимум 4 GB RAM; для клиентских Windows Home установка Hyper-V недоступна. | Не подходит как поддерживаемый macOS VM маршрут. Если загрузится по инструкциям сообщества, это неподдерживаемый эксперимент и может потребовать модифицированную идентичность/boot chain. |
| VMware Workstation Pro | Workstation — Windows/Linux desktop hypervisor, но официальная статья Broadcom прямо говорит: macOS guests поддерживаются только в VMware Fusion VM. Fusion — продукт для Mac. | На Windows-host это не официальный путь; обход через правку конфигурации/разблокировщик и стороннюю EFI — community hack. Не брать за основу установщика. |
| Oracle VirtualBox | В User Guide 7.1 macOS-гости названы экспериментальной и неподдерживаемой функцией; комбинации платформ указывают гостевые Windows/Linux/Solaris и не включают macOS. Документация отдельно предупреждает, что Apple ограничивает macOS Apple hardware и не-Intel CPU может приводить к panic. | На Ryzen 6800H практическая пригодность сомнительная; даже если старые сборки удаётся запустить при обходах, это не подтверждённый/поддерживаемый маршрут. |
| QEMU + WHPX | QEMU официально документирует ускорение WHPX для Windows x86_64. Это поддержка ускорителя и виртуализации в целом, а не гостевой macOS. Документация не обещает macOS-гостя на Windows или AMD. | Потенциально самый гибкий экспериментальный стенд, если community-конфигурация вообще стартует. Сложнее настройки, результатов и поддержки не обещано. Не начинать со скачивания готовых сомнительных образов. |
| VMware Fusion / Apple Virtualization Framework | Broadcom описывает macOS-гостей для Fusion; Apple Virtualization Framework и официальный образец macOS VM адресованы Mac (Apple silicon/Intel Mac в зависимости от API/образца). | Это официальная категория VM, но требует Mac, которого нет в роли текущего Windows-хоста. |

## Подробности по гипервизорам

### Hyper-V

Microsoft перечисляет официально поддерживаемых гостей Hyper-V на Windows: Windows, Linux-дистрибутивы и FreeBSD. macOS в этом перечне отсутствует. Microsoft также разделяет поддержку: собственные ОС и интеграционные компоненты поддерживает Microsoft, другие ОС — только если их поставщик сертифицировал Hyper-V.

Для самого Windows-хоста Hyper-V требует Windows 10/11 Pro или Enterprise, 64-битный CPU с SLAT, включённую аппаратную виртуализацию и минимум 4 GB RAM. Для текущей машины ещё неизвестны редакция Windows, объём памяти и состояние AMD-V/SVM в UEFI, поэтому даже возможность включить Hyper-V нужно подтвердить отдельно.

Первичные источники: [Microsoft: поддерживаемые гости Hyper-V](https://learn.microsoft.com/windows-server/virtualization/hyper-v/supported-windows-guest-operating-systems-for-hyper-v-on-windows), [Microsoft: системные требования и установка Hyper-V](https://learn.microsoft.com/windows-server/virtualization/hyper-v/get-started/install-hyper-v?pivots=windows).

### VMware Workstation

У Broadcom есть официальная статья по VMware Tools для macOS-гостей. В ней сказано, что macOS guests supported only in VMware Fusion virtual machines. Это конкретнее, чем догадки по спискам ОС: Fusion — гипервизор для Mac, а Workstation — для Windows/Linux. Поэтому Workstation на Windows не является официальным способом тестировать macOS VM.

Для сравнения, VMware указывает Apple hardware как обязательное условие для macOS VM на vSphere ESXi. Этот источник о vSphere, а не Workstation, поэтому не следует переносить его формулировку как отдельное техническое правило Workstation; для Workstation вывод основан на статье Broadcom о поддерживаемых macOS-гостях в Fusion.

Источники: [Broadcom: VMware Tools в macOS-госте; примечание о поддержке только Fusion](https://knowledge.broadcom.com/external/article/315260), [Broadcom: macOS VM на vSphere только на Apple hardware](https://knowledge.broadcom.com/external/article?legacyId=88698).

### VirtualBox

В актуальном руководстве VirtualBox 7.2 таблица комбинаций x86-64 host/guest не включает macOS среди поддерживаемых гостевых ОС; для x86-64 названы Windows, Windows Server, Solaris и Linux. В предыдущем официальном руководстве Oracle 7.1 (18 ноября 2025 года) есть отдельный раздел macOS Guests: функция обозначена экспериментальной и неподдерживаемой, сказано о лицензионных/технических ограничениях Apple и о вероятном Unsupported CPU panic на не-Intel CPU. Ryzen 7 6800H — AMD, поэтому это предупреждение относится к нашему классу CPU.

Источник: [Oracle VirtualBox 7.1: гостевые ОС и macOS guests](https://docs.oracle.com/en/virtualization/virtualbox/7.1/user/BasicConcepts.html), [Oracle VirtualBox 7.1: поддерживаемые host/guest комбинации](https://docs.oracle.com/en/virtualization/virtualbox/7.1/user/Introduction.html).

### QEMU + WHPX

QEMU поддерживает аппаратное ускорение на x86_64 Windows через Windows Hypervisor Platform (WHPX); для QEMU это backend-ускоритель, а не специальная поддержка macOS. В документации QEMU нет заверения, что macOS-гость на AMD Windows host поддерживается или совместим. Наличие WHPX подтверждает только то, что QEMU может использовать Windows API для ускорения соответствующих виртуальных машин.

Для установки macOS в подобной конфигурации community-проекты обычно добавляют загрузочную прослойку и подмену ожидаемой Apple-машины/виртуального оборудования. Это вывод из отсутствия официальной поддержки и требований Apple, а не документированный рецепт QEMU. Я намеренно не описываю обход лицензии или способы маскировки оборудования как официальное решение.

Источники: [QEMU: WHPX для Windows](https://www.qemu.org/docs/master/system/whpx.html), [QEMU: системная эмуляция и ускорители](https://www.qemu.org/docs/master/system/introduction.html).

## Apple: лицензия и официальный способ VM

На дату проверки страница Apple Software License Agreements показывает macOS 27 и Tahoe как текущие соглашения. В заголовке соглашения macOS Tahoe 26 указано “For use on Apple-branded Systems”. Раздел 2 ограничивает лицензию Apple-branded computer; разрешение на до двух дополнительных экземпляров в VM распространяется на каждый Apple-branded компьютер, которым владеет/управляет пользователь и который уже работает под macOS. Это не даёт основания считать запуск на обычном Windows/AMD ноутбуке официально разрешённым. Это изложение текста лицензии, не юридическое заключение.

Apple Developer Documentation описывает Virtualization framework для Mac и публикует sample для установки/запуска macOS VM на Apple silicon. То есть официальный Apple путь VM — Mac host, а не Windows ПК.

Источники: [Apple: актуальные Software License Agreements](https://www.apple.com/legal/sla/), [Apple: macOS Tahoe 26 SLA PDF](https://www.apple.com/legal/sla/docs/macOSTahoe.pdf), [Apple: Virtualization framework](https://developer.apple.com/documentation/virtualization), [Apple: запуск macOS VM на Apple silicon](https://developer.apple.com/documentation/virtualization/running-macos-in-a-virtual-machine-on-apple-silicon).

## Рекомендация проекту

1. **Не строить проект вокруг обещания “запускаем macOS в VM на твоём Windows-ноуте”.** У такого обещания нет официального основания.
2. Для безопасного первого этапа можно поднять обычную VM с Linux в Hyper-V/VirtualBox/VMware/QEMU и проверить только наши собственные скрипты: сборку EFI-папки, проверку `config.plist`, структуру USB-пакета и документацию. Это не тест macOS.
3. Если цель именно загрузить macOS до dual boot, честно обозначить отдельный эксперимент community-класса и заранее согласовать, что результат не официальный/не гарантирован. Не скачивать случайный “готовый образ macOS” с файлообменников.
4. Если в наличии появится Mac, использовать официальный macOS VM путь на нём для проверки macOS как гостя. При этом и Mac VM всё равно не эмулирует графику/железо целевого ASUS.
5. Для проверки реального железа ASUS всё равно потребуется отдельный live/dual-boot этап; успешная VM-загрузка не является пропуском этого этапа.

## Что пока неизвестно

- Включён ли параметр SVM именно в UEFI и какая функция Windows сейчас подняла гипервизор; WMI показывает аппаратную виртуализацию firmware enabled и `HypervisorPresent=True`, но не объясняет точную конфигурацию.
- Какой конкретный VM-тест выбран; macOS-гость на Windows/AMD официальными документами гипервизоров не подтверждён.
- Какой конкретно community-сценарий (если вообще есть) актуально заводится на Ryzen 6000 mobile в 2026 году; первичные документы гипервизоров этого не подтверждают.
- Будет ли целевой VM-тест оценивать только загрузчик, или пользователь ожидает рабочий графический macOS desktop. Без поддерживаемого виртуального GPU эти результаты сильно отличаются.
- Точный текст лицензии зависит от конкретной версии macOS и способа получения ПО; перед любым использованием нужно читать лицензию именно выбранной версии.

## Снимок текущего Windows-хоста

Проверено локально 2026-10-19 после переноса проекта на Desktop:

- Модель: ASUSTeK ROG Strix G513RM_G513RM.
- ОС: Windows 11 Pro, build 26200, x64.
- Процессор: AMD Ryzen 7 6800H; `VirtualizationFirmwareEnabled=True`.
- Память: 16 GiB.
- Свободно на C: примерно 223.5 GiB из 875.5 GiB.
- `HypervisorPresent=True`: Windows сообщает, что гипервизор уже присутствует. Это не подтверждает macOS-гостя; точная причина/настройка через WMI не установлена.
- Запрос состояния Windows optional feature Hyper-V потребовал повышения прав; администраторский запрос не выполнялся.

В этом снимке не выключались функции безопасности, Hyper-V/VBS, Secure Boot и настройки UEFI. В проект скачаны OC4VM 3.0.1, OpenCorePkg 1.0.8, Monterey Recovery и QEMU Windows installer для преобразования Recovery. VMware Workstation пока не установлен: официальный портал требует вход в аккаунт и принятие условий загрузки. Локальная VM-копия находится в `vm/Monterey12-test/` и исключена из Git; Recovery VMDK уже прикреплён, запуск ждёт Workstation.

## Источники и версии

- Apple, Software License Agreements landing page, проверено 2026-10-19: https://www.apple.com/legal/sla/
- Apple, macOS Tahoe 26 SLA PDF: https://www.apple.com/legal/sla/docs/macOSTahoe.pdf
- Apple Developer, Virtualization framework: https://developer.apple.com/documentation/virtualization
- Apple Developer, macOS VM sample on Apple silicon: https://developer.apple.com/documentation/virtualization/running-macos-in-a-virtual-machine-on-apple-silicon
- Microsoft Learn, Hyper-V supported guests: https://learn.microsoft.com/windows-server/virtualization/hyper-v/supported-windows-guest-operating-systems-for-hyper-v-on-windows
- Microsoft Learn, Hyper-V requirements: https://learn.microsoft.com/windows-server/virtualization/hyper-v/get-started/install-hyper-v?pivots=windows
- Oracle VirtualBox User Guide 7.2, актуальная платформа/гостевые ОС: https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/Introduction.html; User Guide 7.1, 2025-11, явные предупреждения о macOS guests: https://docs.oracle.com/en/virtualization/virtualbox/7.1/user/BasicConcepts.html
- Broadcom KB 315260, macOS guest support in Fusion: https://knowledge.broadcom.com/external/article/315260
- QEMU documentation, WHPX: https://www.qemu.org/docs/master/system/whpx.html
