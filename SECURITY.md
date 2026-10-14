# Установщик и безопасность

## Что делает установщик

- Читает выбранные вами файлы «Тени Чернобыля», Minecraft Java Edition и Java, затем создаёт отдельную установку в указанной папке.
- Подготавливает Minecraft 1.20.1 и Fabric. Недостающие компоненты загружает по официальным данным Mojang/Minecraft и Fabric.
- Не переносит аккаунты, токены входа и существующие сохранения. Язык Minecraft берёт из файла настроек выбранной игры.
- Запускает две игровые части: «Сталкер» и фоновый Minecraft. Их прогресс сохраняется совместно.

Это поведение можно проверить в [исходниках подготовки](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/prepare_demo.py), [окне установщика](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/install_demo.py) и [запуске игр](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/demo_launcher.py). Полный исходный архив находится в Releases.

## Проверки файлов

[Результат локальной проверки и точные файлы](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/security/SCAN-RESULTS.json) содержит дату, контрольную сумму проверенного архива и результат Microsoft Defender.

Установщик, приложение и изменённый движок «Сталкера» **не подписаны сертификатом издателя**. Проверка антивирусом и доступные исходники дают информацию для оценки файла, но не являются гарантией отсутствия всех рисков. Независимая проверка готовой сборки ещё не проведена.

Для отдельной публичной проверки можно использовать [VirusTotal](https://docs.virustotal.com/docs/how-it-works). Пока отчёт VirusTotal для этого выпуска не опубликован; ссылка на сервис сама по себе не является результатом проверки.

## Для чего SHA256SUMS.txt

Это необязательный файл с контрольными суммами архивов. Он помогает убедиться, что скачанный файл совпадает с файлом выпуска и не повреждён. Сам по себе он не подтверждает безопасность программы и для установки не требуется.

Если ваш антивирус сообщает об угрозе, не отключайте защиту ради запуска. [Сообщите об этом](https://github.com/DeSoreGD/Steve-in-the-zone/issues/new/choose), приложив название обнаружения и имя файла.

## English

Setup reads the selected game and Java files, creates a separate installation, and obtains missing Minecraft 1.20.1/Fabric components using official metadata. Accounts, login tokens and existing saves are not imported. The relevant source files are linked above.

The [local scan record](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/security/SCAN-RESULTS.json) identifies the exact archive and Microsoft Defender result. The installer, launcher and modified native engine are unsigned. An antivirus result and source availability are evidence for evaluation, not a guarantee of safety; an independent review and VirusTotal report are not currently available.

SHA256SUMS.txt is optional: it checks file identity/integrity, not safety. Do not disable protection to bypass an antivirus detection; report the detection and file name.
