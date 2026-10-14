# Steve in the Zone

Build, craft and fight as Steve inside **S.T.A.L.K.E.R.: Shadow of Chernobyl**. NPCs, dialogue and quests come from SoC; tools, armor, crafting and blocks come from Minecraft.

Version **0.4.0-beta.1**. A full story playthrough has not been confirmed. [Known limitations](KNOWN-LIMITATIONS.md).

## Requirements

| Component | Requirement |
|---|---|
| Windows | Windows 10 or 11, 64-bit |
| S.T.A.L.K.E.R. | **Shadow of Chernobyl 1.0006**, without other mods |
| Minecraft | Installed **Java Edition**. The project uses **1.20.1**; setup prepares that version and Fabric automatically. Bedrock Edition is unsupported |
| Java | 64-bit Java. **Java 21** is recommended for a new setup; an existing compatible Java 17+ found by setup can also be used |
| Internet and disk space | Internet access for component downloads and room for a separate copy of the game files |

The base games are not included. Setup creates a separate project installation and preserves your original games and saves.

### Why Java is needed

Minecraft Java Edition runs on Java. This project needs it for the Minecraft part even though you play in the S.T.A.L.K.E.R. window.

If setup finds compatible Java, there is no need to download it again. Otherwise, open the [Microsoft OpenJDK page](https://learn.microsoft.com/en-us/java/openjdk/download#openjdk-21), choose **OpenJDK 21 → Windows → x64 → msi**, and install it. Select **`javaw.exe`** from its **`bin`** folder in the setup Java field. Microsoft OpenJDK is usually installed under `C:\Program Files\Microsoft` in a folder beginning with `jdk-21`.

## Installation

1. Download **`Steve-in-the-Zone-0.4.0-beta.1-Windows-x64.zip`** from [Releases](https://github.com/DeSoreGD/Steve-in-the-zone/releases). The `sources` archive is for developers.
2. Extract the **entire archive** and run **`InstallSteveInTheZone.exe`**. Keep the EXE, `_internal` and `payload` together.
3. Choose the setup language and fill in the fields using the table below.
4. Click **Install** and wait for it to finish. Setup prepares Minecraft 1.20.1 and Fabric automatically; no manual Minecraft mod installation is needed.
5. Open **`app\SteveInTheZone.exe`** inside the new **`Steve in the Zone`** folder, select **Survival**, then **Launch game**.

| Setup field | What to select |
|---|---|
| SoC 1.0006 folder | The installed Shadow of Chernobyl root folder containing `gamedata.db…` files |
| Installed Minecraft folder | The Java Edition data folder, usually **`%APPDATA%\.minecraft`**. Press Win + R and enter this path to open it. Other launchers may use a different folder |
| Java | If discovery fails, select the compatible Java **`bin\javaw.exe`** described above |
| New game folder | A folder where setup will create a separate **`Steve in the Zone`** directory, for example `D:\Games` |

Play in the S.T.A.L.K.E.R. window. Minecraft runs in the background. The first launch starts a new campaign; later launches resume the latest joint save.

## Controls

| Key | Action |
|---|---|
| WASD / Space | Move / jump |
| Left / right mouse | Attack and mine / use an item and place a block |
| Wheel / 1–9 | Select a hotbar item |
| E | Inventory; Zone items and Zone tasks open SoC items, PDA and quests |
| G | Talk, pick up and interact with doors or mechanisms |
| F5 | Third-person view |
| F6 | Survival / Creative |
| F7 / F8 | Save / load both parts of the game |
| Esc | Close the screen or open the menu |
| F9 / Shift + F9 | Experimental obstacle escape / return to its starting point |

To exit, close the S.T.A.L.K.E.R. window and wait for saving. Do not terminate background Minecraft separately: progress is saved jointly by both games. Close both games before moving the entire **`Steve in the Zone`** folder.

## Getting started

Talk to Sidorovich and follow the original quests. If a character refuses to talk, select an empty hotbar slot and remove offhand weapons. Swords, axes and bows count as weapons.

Flash drives, documents, keys and psi helmets are in **E → Zone items**. Psi helmet protection follows the original story conditions while it is in that inventory. Use **E → Zone tasks** for the map and quests.

Buy Minecraft equipment and materials with rubles from Sidorovich and other original traders: open normal trade and select **Minecraft**. Stock up on food, arrows and materials before laboratories. SoC trees cannot be mined as Minecraft trees.

Save with **F7** before travelling to another area. If you are stuck, check the PDA task first; F9 does not complete story conditions.

## Problems and security

[Report an issue](https://github.com/DeSoreGD/Steve-in-the-zone/issues/new/choose) · [Useful logs](REPORT-A-PROBLEM.md) · [What setup does](SECURITY.md)
