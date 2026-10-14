# Steve in the Zone — 0.4.0-beta.1

Minecraft building, crafting and combat inside S.T.A.L.K.E.R.: Shadow of Chernobyl. Minecraft runs in the background; play in the S.T.A.L.K.E.R. window.

**First playable beta.** It combines Minecraft equipment and building with the original SoC single-player campaign. A complete connected Survival playthrough and the O-Consciousness refusal branch remain unverified. See KNOWN-LIMITATIONS.md and REPORT-A-PROBLEM.md for limitations and bug reports.

## Installation

Requirements: Windows 10/11 x64, your own Shadow of Chernobyl 1.0006 installation, installed Minecraft, and Java 17+ x64. The archive does not contain either game, Java, accounts or somebody else's saves. Internet access is needed to prepare missing Minecraft components.

1. Extract the entire ZIP into a normal folder. Keep the EXE, `_internal` and `payload` together; do not run it inside the ZIP.
2. Run `InstallSteveInTheZone.exe` and choose English or Russian.
3. Select the SoC folder containing `gamedata.db*`, the Minecraft folder containing `assets`, `libraries`, `versions`, and a new installation folder. If Java is not found, select `javaw.exe` from an x64 Java 17+ installation.
4. Wait for setup to finish. Open `app/SteveInTheZone.exe` in the created folder, select Survival, then Launch game.

The original installations and saves are preserved. Components are copied to a separate installation. The first game launch creates a fresh Minecraft world and native campaign. A joint first Survival launch and resume after folder relocation passed in a separate installation on this computer. Later launches restore the latest complete paired checkpoint.

Application language is independent of the games. Minecraft keeps the language selected in the source installation; Zone dialogue uses the SoC language. Accounts are not imported. This currently uses a local single-player profile with the selected name; Microsoft sign-in and multiplayer are not implemented.

## Controls

| Key | Action |
|---|---|
| WASD / Space | Move / jump |
| Left / right mouse | Minecraft attack and mining / use and place block |
| Wheel / 1–9 | Hotbar selection |
| E | Minecraft inventory; Zone items and Zone tasks buttons open the original SoC menus |
| G | Talk, operate story switches, doors and other native interactions |
| F5 | Third-person camera |
| F6 | Creative / Survival |
| F7 / F8 | Paired quicksave / quickload |
| F9 | Pass through obstacles; press again to restore the previous mode on clear ground |
| Shift + F9 | In rescue mode, return to its starting point |
| Esc | Close current screen; SoC menu, graphics and sound |

Do not close the hidden Minecraft process separately. Close the SoC window and wait for the pair to save. Settings → New world backs up both parts to `backups` and starts a new campaign. Close both games before moving the entire installation folder.

## Story interactions

Some characters refuse to talk to an armed player. Before pressing G, select an empty hotbar slot and remove weapons from your offhand: swords, axes, bows, crossbows and tridents count as weapons. If the NPC is still taking part in an original scene or fight, wait for it to finish.

Flash drives, documents, keys, the decoder and psi helmets remain in the real SoC inventory: E → Zone items. They do not become Minecraft items. Psi helmet protection uses the original story condition of having the helmet in this inventory; no Minecraft armor slot is needed. Open E → Zone tasks for the original PDA, tasks and map markers.

Save the pair with F7 before entering a laboratory or another area. After an original level transition or scripted relocation, wait for the joint loading process to finish. If a passage appears blocked, check the PDA task first: F9 helps escape an obstacle but does not complete story conditions.

## Equipment and supplies

Survival starts with stone tools, planks, dirt, bread, torches and a crafting table. Minecraft supplies use the original rubles and merchants: Sidorovich, Barkeep, Sakharov, Petrenko and the Freedom trader, when their normal trade window is available. Select Minecraft in the native trade window. Food, a bow, arrows and materials are available early; Sidorovich's iron unlocks after the first mission, and later traders' diamonds unlock after the X18 documents. Zone trees cannot be harvested.

Stock up on food, arrows, blocks and spare tools before leaving a base. No new trader was added inside the late laboratories or the power plant. Iron armor, a shield and a bow are useful for later areas; diamond armor is an expensive optional upgrade, not a free Survival starting set.

Minecraft armor provides physical and radiation protection. Native medicine, documents and the story psi helmet remain in Zone items. Native guns and outfit protection have not been fully ported; they do not replace Minecraft combat equipment.

For an error report, keep `minecraft/demo-minecraft.log`, `minecraft/demo-minecraft-error.log` and the latest log in `soc/_appdata_steve/logs`. Do not share account files or launch arguments containing tokens.
