# Готовые компоненты для первого VM-эксперимента

**Проверено:** 2026-10-19 по README, исходникам, лицензиям и страницам релизов самих проектов; для общих ограничений — документации Dortania, Apple и выбранных гипервизоров.  
**Хост, о котором идёт речь:** Windows на AMD Ryzen 7 6800H (Rembrandt / Zen 3+).  
**Границы:** ничего не скачивалось, не запускалось и не устанавливалось. Эта заметка проверяет, что из готового полезно именно на подготовительном этапе VM. Она не обещает, что macOS-гость на обычном AMD/Windows-ПК официально поддерживается.

## Короткий ответ

Для сборки загрузочной EFI полезен **OpenCorePkg**; для запуска ядра macOS на AMD CPU могут понадобиться **AMD Vanilla patches**. Но это не готовый комплект «запусти macOS в Windows VM»: совместимость гостевой macOS отдельно ограничена гипервизором, виртуальным UEFI/устройствами и лицензией macOS. Успешный запуск в VM не проверит настоящую Radeon 680M.

**OpCore Simplify** может автоматически собрать стартовую EFI по аппаратному отчёту, однако опубликованная таблица графики перечисляет AMD Vega APU (Ryzen 1xxx–5xxx и 7x30), не Rembrandt 680M. Поэтому не надо считать его генератором подходящей EFI для 6800H/680M. **OCAT** — удобный редактор `config.plist`, но не мастер совместимости. **UnPlugged** из исходного исследования был перепутан с инструментом для Windows: официальный [corpnewt/UnPlugged](https://github.com/corpnewt/UnPlugged) — Bash-скрипт для сборки/запуска полного installer из уже загруженного macOS Recovery, не Windows-программа и не VM-гипервизор.

## Компоненты

| Компонент | Что делает на деле | Ryzen 7 6800H и VM | Лицензия / официальный источник | Вердикт для первого этапа |
|---|---|---|---|---|
| **OpenCorePkg** | UEFI-загрузчик и набор утилит. Сам macOS не содержит, VM не создаёт и железную совместимость не добавляет. | Подходит как загрузочный слой, если выбранный гипервизор умеет стартовать UEFI-загрузчик. EFI должна соответствовать устройствам, которые VM показывает гостю. | BSD-3-Clause. [Официальный репозиторий](https://github.com/acidanthera/OpenCorePkg); [официальные релизы](https://github.com/acidanthera/OpenCorePkg/releases/latest). | Базовый кандидат для будущей EFI. Не скачивать, пока не выбрали гипервизор и виртуальные устройства. Для безопасной ссылки — только страница официальных релизов Acidanthera, не перепакованные архивы из видео/файлообменников. |
| **AMD Vanilla patches** | Набор бинарных патчей ядра macOS для AMD CPU в конфигурации OpenCore. В README указаны семейства 15h/16h/17h/19h и необходимость OpenCore с `ProvideCurrentCpuInfo`; число физических ядер настраивается отдельно. | Семейство 19h покрывает AMD Zen-процессоры, куда относится 6800H. Это **не подтверждение** загрузки macOS-гостя на Ryzen 6800H в конкретной VM. Если VM скрывает/подменяет модель CPU, вывод зависит от того, какой CPU видит гость. Патчи не дают драйвер 680M и не добавляют графическое ускорение. | В публичном репозитории [не обнаружен отдельный LICENSE-файл](https://github.com/AMD-OSX/AMD_Vanilla). Не считать лицензию автоматически разрешительной; до включения кода в наш продукт нужно уточнить лицензионные права у авторов/истории исходников. [Официальный исходный репозиторий и README](https://github.com/AMD-OSX/AMD_Vanilla). | Технически применимый CPU-компонент, если VM действительно предъявляет AMD CPU и используется совместимая связка OpenCore/macOS. Сначала изучить patch set и условия; ничего не скачивать вслепую. |
| **OpCore Simplify** | GUI/скрипт, который по hardware report помогает выбрать настройки и собрать OpenCore EFI; при сборке получает OpenCore и kext-зависимости. Сам по себе macOS не устанавливает и отсутствующие драйверы не пишет. | README принимает Ryzen/Threadripper CPU через AMD Vanilla, но перечисляет для AMD APU семейство Vega (Ryzen 1xxx–5xxx, 7x30), а не Radeon 680M / Rembrandt. Для VM его аппаратный отчёт описывал бы виртуальную машину, а не настоящий ASUS. Значит, он не закрывает ни совместимость с 680M, ни неподдерживаемость Windows-host/macOS-guest. | BSD-3-Clause. [Официальный репозиторий/README](https://github.com/lzhoang2801/OpCore-Simplify). На странице [Releases](https://github.com/lzhoang2801/OpCore-Simplify/releases) сейчас нет опубликованных релизов; сборку получают из исходника, который не надо запускать до отдельного решения. | Полезен позже для сравнения генерации EFI, но **не брать как готовую VM-сборку для 6800H**. Сейчас не запускать. |
| **OCAT (OCAuxiliaryTools)** | Кроссплатформенный GUI для редактирования и проверки OpenCore `config.plist`, обновления и миграции структуры конфига, управления версиями OpenCore/kexts и резервных копий EFI. | Может помочь просматривать и править VM-конфиг вручную; не анализирует гипервизор так, чтобы гарантировать запуск macOS, не генерирует AMD-графический драйвер и не превращает произвольный конфиг в совместимый. | MIT. [Официальный репозиторий](https://github.com/ic005k/OCAuxiliaryTools); [официальный latest release](https://github.com/ic005k/OCAuxiliaryTools/releases/latest). README связывает «получить свежий OpenCore» с обновлением самого OCAT; релизы OCAT публикуются редко, поэтому версию следует сверять перед использованием. | Не обязателен на первом пробном старте. Пригодится для ручного просмотра/изменения готового конфига, если понадобится. |
| **UnPlugged (corpnewt)** | Скрипт на Bash, который в macOS Recovery собирает/запускает офлайн-установщик из уже подготовленных файлов; ориентирован на реальный установочный носитель и целевой том. | Требует macOS Recovery и тома/носителя. Не является Windows-утилитой для создания VM и не создаёт OpenCore EFI. Для проверки VM до решения о способе установки не нужен. | У репозитория только README и скрипт; отдельная лицензия на странице не указана. [Официальный репозиторий](https://github.com/corpnewt/UnPlugged). [В исходном `landscape.md` ссылка `lzhoang2801/UnPlugged` некорректна и возвращает 404](https://github.com/lzhoang2801/UnPlugged). | Не скачивать сейчас. Вернуться к нему только если решим делать физический USB installer и подтвердим подходящий сценарий. |
| **`macrecovery.py` из OpenCorePkg** | Утилита в официальном архиве OpenCore для получения файлов Apple macOS Recovery; не формирует готовую EFI, не включает сами файлы macOS в OpenCore и не ставит их в VM автоматически. | Может быть частью будущего процесса получения Recovery image, если гипервизор/VM-схема поддерживает такой загрузочный образ. Это отдельный этап после выбора VM. | Файл поставляется в репозитории OpenCorePkg; см. BSD-3-Clause в корне проекта. [Windows/Recovery руководство Dortania](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/windows-install.html) объясняет путь получения Recovery из `Utilities/macrecovery/`; [официальный OpenCorePkg](https://github.com/acidanthera/OpenCorePkg). Данные macOS лицензируются отдельно Apple. | Не запускать и не загружать крупные файлы сейчас. Сначала определиться, что VM и способ загрузки вообще остаются осмысленным экспериментом. |

## Что это означает для VM-эксперимента

1. **Слой загрузки:** OpenCore — единственный из перечисленных компонентов, который непосредственно нужен как UEFI boot manager для EFI-эксперимента. AMD Vanilla patches могут быть необходимы, если macOS guest видит AMD CPU. Точное сочетание определяется выбранной VM-конфигурацией, не фактом, что хост называется Ryzen 7 6800H.
2. **Сборка EFI:** OpCore Simplify может быть исследовательской опцией, но её опубликованный список iGPU не включает 680M. Не обещать, что генерация EFI для физического hardware report будет соответствовать виртуальному железу.
3. **Редактирование:** OCAT — вторичный GUI-инструмент после появления конкретного `config.plist`; для первого запуска он не обязателен.
4. **Образ установщика:** UnPlugged — не средство установки macOS в Windows VM. `macrecovery.py` относится к получению Recovery-файлов, но загружать их пока рано.
5. **GPU:** VM обычно показывает гостю виртуальный адаптер, а не Radeon 680M с полноценной поддержкой macOS. Поэтому VM может проверить только загрузку гостя и часть виртуальных устройств, не драйвер Rembrandt и не реальное ускорение 680M.
6. **Поддержка и лицензия:** Dortania прямо относит AMD laptop CPUs к неподдерживаемым своим гайдом и указывает ограничения AMD-функций; документация гипервизора, рассмотренная в [vm-options.md](vm-options.md), также не подтверждает официальный macOS-гость на обычном Windows/AMD-хосте. Условия лицензии macOS описаны там же. Поэтому VM-попытка — отдельный эксперимент с ограниченной доказательной ценностью, а не знак, что dual boot на ASUS готов.

## Что оставить на потом

- **Не качать готовый образ macOS или готовую чужую EFI** с файлообменников/видео. Официальная ссылка на Recovery-процедуру дана выше; скачивание выполнять только после проверки применимости и законного способа использования выбранной версии macOS.
- **Не скачивать пока OpenCore/OCAT/OpCore Simplify/kexts.** Эти программы меняются, их версии надо выбирать под конкретную VM и выбранный OpenCore. У OpCore Simplify сборка из исходника может сама скачивать дополнительные исполняемые/драйверные зависимости.
- **Не применять UnPlugged к VM.** Он касается отдельного офлайн-installer workflow в Recovery, а не виртуального UEFI.
- Перед любой загрузкой позже записать конкретную версию, официальный release URL, контрольную сумму/подпись (если опубликована), лицензию и список файлов. Никаких бинарников не коммитить в Git.

## Первичные источники

- [Acidanthera OpenCorePkg — repository, README, BSD-3-Clause](https://github.com/acidanthera/OpenCorePkg)
- [Acidanthera OpenCorePkg — official releases](https://github.com/acidanthera/OpenCorePkg/releases/latest)
- [AMD-OSX AMD_Vanilla — README and patches](https://github.com/AMD-OSX/AMD_Vanilla)
- [Dortania OpenCore Install Guide — Ryzen and Threadripper (17h/19h)](https://dortania.github.io/OpenCore-Install-Guide/AMD/zen.html)
- [Dortania OpenCore Install Guide — hardware/AMD/VM limitations](https://dortania.github.io/OpenCore-Install-Guide/macos-limits.html)
- [lzhoang2801 OpCore-Simplify — repository, README, BSD-3-Clause](https://github.com/lzhoang2801/OpCore-Simplify)
- [lzhoang2801 OpCore-Simplify — Releases page](https://github.com/lzhoang2801/OpCore-Simplify/releases)
- [ic005k OCAuxiliaryTools — repository, README, MIT](https://github.com/ic005k/OCAuxiliaryTools)
- [ic005k OCAuxiliaryTools — official latest release](https://github.com/ic005k/OCAuxiliaryTools/releases/latest)
- [corpnewt UnPlugged — repository and usage README](https://github.com/corpnewt/UnPlugged)
- [Dortania — Windows installer/Recovery overview](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/windows-install.html)
- [Apple Software License Agreements](https://www.apple.com/legal/sla/)

## Поправки к `landscape.md`

- В таблице `landscape.md` UnPlugged был описан как Windows-создатель macOS USB. README найденного оригинального проекта говорит обратное: это Bash-скрипт для полного installer в macOS Recovery. Ссылка `lzhoang2801/UnPlugged` ведёт на 404; официальный найденный upstream — `corpnewt/UnPlugged`.
- License для AMD_Vanilla нельзя называть MIT по косвенным данным: GitHub показывает репозиторий без отдельного `LICENSE`. Необходимо прояснить право повторного распространения патчей, если проект захочет включать их в свой продукт.
- OpenCore/AMD Vanilla/OCAT/OpCore Simplify/UnPlugged не являются гипервизором. Их нельзя описывать как готовый способ установить macOS на Windows VM.
