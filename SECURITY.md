# Что делает установщик

Установщик читает выбранные вами файлы «Тени Чернобыля», Minecraft Java Edition и Java. Затем создаёт отдельную установку в указанной папке; исходные игры и сохранения остаются на месте.

Недостающие компоненты Minecraft 1.20.1 и Fabric загружаются по официальным данным Mojang/Minecraft и Fabric. Аккаунты, токены входа и существующие сохранения не переносятся. Из настроек выбранного Minecraft используется язык игры.

После установки приложение запускает «Сталкер» и фоновый Minecraft. Прогресс сохраняется совместно в двух играх.

Код можно посмотреть здесь:

- [Подготовка файлов и загрузка компонентов](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/prepare_demo.py)
- [Окно установщика](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/install_demo.py)
- [Запуск и закрытие игр](https://github.com/DeSoreGD/Steve-in-the-zone/blob/main/launcher/demo_launcher.py)

Установщик, приложение запуска и изменённый движок пока не подписаны сертификатом издателя. Полные исходники доступны отдельным архивом в Releases.

## English

Setup reads the selected SoC, Minecraft Java Edition and Java files, then creates a separate installation. The original games and saves remain in place. Missing Minecraft 1.20.1/Fabric components are obtained using official metadata. Accounts, login tokens and existing saves are not imported; the Minecraft language setting is used.

The application starts S.T.A.L.K.E.R. and background Minecraft, with joint saves. The relevant source files are linked above; full sources are available in Releases. The installer, launcher and modified native engine are currently unsigned.
