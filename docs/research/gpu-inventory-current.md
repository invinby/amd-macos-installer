# Текущий инвентарь GPU

Дата проверки: 21 октября 2026 года. Источник — Windows на ASUS ROG Strix G513RM. Сбор только читает сведения об устройствах; серийные номера не запрашивались.

## Что Windows видит

| Устройство | PCI ID | Путь подключения | Состояние |
|---|---|---|---|
| AMD Radeon Graphics (встроенная в Ryzen 7 6800H) | `1002:1681`, subsystem `1043:1B7C`, revision `C8` | `PCIROOT(0)#PCI(0801)#PCI(0000)`; ACPI: `PCI0/GP17/VGA_` | OK |
| NVIDIA GeForce RTX 3060 Laptop GPU | `10DE:2520`, subsystem `1043:1B7C`, revision `A1` | `PCIROOT(0)#PCI(0101)#PCI(0000)`; ACPI: `PCI0/GPP0/PEGP` | OK |

Windows также сообщает модель процессора `AMD Ryzen 7 6800H with Radeon Graphics`, BIOS `G513RM.327` от 16 февраля 2023 года и модель системы `ROG Strix G513RM_G513RM`.

**Что это доказывает:** Windows на этом ноутбуке находит два отдельных PCI-устройства AMD и NVIDIA, а AMD-устройство находится под ACPI-узлом `GP17/VGA_`.

**Чего это не доказывает:** это ещё не снимок регистров/прошивок, не схема проводки встроенной панели и не подтверждение, что macOS умеет управлять Radeon 680M или использовать Metal. Следующие данные надо собирать отдельно в Linux и macOS; виртуальная машина для проверки настоящей Radeon не подходит.

## Как повторить сбор

Открыть PowerShell в Windows и выполнить команды ниже. Они читают перечисление устройств и версию BIOS; уникальные серийные номера не запрашиваются.

```powershell
$gpus = Get-PnpDevice -Class Display
foreach ($gpu in $gpus) {
  $gpu | Format-List FriendlyName,Status,InstanceId
  Get-PnpDeviceProperty -InstanceId $gpu.InstanceId -KeyName 'DEVPKEY_Device_HardwareIds','DEVPKEY_Device_LocationPaths','DEVPKEY_Device_Parent','DEVPKEY_Device_BusReportedDeviceDesc' |
    Format-List KeyName,Data
}
Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name
Get-CimInstance Win32_BIOS | Select-Object Manufacturer,SMBIOSBIOSVersion,ReleaseDate
Get-CimInstance Win32_ComputerSystemProduct | Select-Object Vendor,Name
```

## Следующий сбор данных

1. С Linux live USB, не устанавливая систему и не меняя внутренний диск, сохранить вывод `lspci -nnk -d 1002:` и подходящие строки `dmesg` про `amdgpu`, прошивки, Display Core/DCN и SMU.
2. Записать, какие блоки Radeon обнаружены и какие имена/версии прошивок Linux сообщает. Сами закрытые бинарные прошивки не копировать в репозиторий.
3. Выяснить по документации ноутбука и ACPI, к какому GPU подключены встроенная панель и внешние видеовыходы.
4. Перед первым macOS-драйверным прототипом получить отдельный безопасный способ видеть и отлаживать систему, если 680M пока не выдаёт изображение: например, загрузка без графического входа с доступом по Ethernet/SSH. Сначала проверить, что такой сценарий возможен для выбранной macOS.

Приёмка каждого этапа остаётся раздельной: обнаружение устройства → базовое изображение → выполнение GPU-команд → Metal → сон, питание и стабильность. Рабочий экран сам по себе не равен аппаратному ускорению.
