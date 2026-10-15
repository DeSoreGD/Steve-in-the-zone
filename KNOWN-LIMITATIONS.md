# Ограничения 0.4.0-beta.6

- Полное прохождение исходного сюжета, включая ветку отказа О-Сознанию, ещё не подтверждено. В beta возможны ошибки прохождения.
- Стрельба из оружия «Сталкера», защита его костюмов и все пассивные эффекты артефактов пока не перенесены полностью. Для боя и защиты используйте Minecraft-снаряжение.
- Minecraft и «Сталкер» сохраняют два инвентаря, доступные через E. Документы и пси-шлемы остаются в «Вещах Зоны».
- Кровотечение у Стива отключено до появления удобного лечения в основном инвентаре. Начальные 10% накопленной радиации не снимают здоровье; дальнейшее облучение остаётся опасным.
- Бои NPC с Minecraft-мобами экспериментальные: NPC могут замечать существ и стрелять по ним, мобы — выбирать NPC и атаковать. Поиск пути по геометрии Зоны неполон: моб может помнить противника, но стоять без маршрута. Не все виды мобов и ситуации боя подтверждены.
- Поддерживается локальная одиночная игра. Вход Microsoft и сетевой режим не реализованы.
- Основа проекта — «Тень Чернобыля» 1.0006 без сторонних модов. Другие модификации могут быть несовместимы; Minecraft Bedrock Edition не поддерживается.
- Native-отрисовка моделей использует ограниченные буферы геометрии и текстур. Неподдерживаемые модели или сцены, превышающие этот объём, сохраняют запасную отрисовку; она может менять освещение и работать медленнее.
- У рельсов и некоторых других тонких поверхностей возможно мерцание; причина ещё не установлена. Эффект порталов Края отличается от оригинального шейдера.
- Свет Minecraft-факелов пока не передаётся в нативное освещение Зоны; факел в руке также не заменяет фонарь. Установке факела нужна опора из Minecraft-блока. Штатный фонарь «Сталкера» включается клавишей L при его наличии.
- Аварийный проход F9 экспериментальный. Перед его использованием сохранитесь через F7.

[Сообщить об ошибке](https://github.com/DeSoreGD/Steve-in-the-zone/issues/new/choose) · [Какие журналы приложить](REPORT-A-PROBLEM.md)

## English

- A complete story playthrough, including the O-Consciousness refusal branch, remains unverified. Progression bugs may occur in this beta.
- SoC guns, outfit protection and all passive artifact effects are not fully ported. Use Minecraft combat equipment and armor.
- Minecraft and SoC retain separate inventories, accessible through E. Documents and psi helmets stay in Zone items.
- Steve's bleeding is disabled until treatment is available conveniently in the main inventory. The first 10% of accumulated radiation does not drain health; further exposure remains dangerous.
- NPC–Minecraft mob combat is experimental. Native NPCs can spot and shoot creatures; mobs can target and attack NPCs. Navigation over Zone geometry is incomplete: a mob may retain its enemy but stand without a route. Not every mob type or combat situation has been verified.
- Local single-player only; Microsoft sign-in and multiplayer are not implemented.
- Vanilla SoC 1.0006 is the supported base. Other SoC mods may be incompatible; Minecraft Bedrock Edition is unsupported.
- Native model drawing has bounded geometry and texture buffers. Unsupported models or scenes exceeding those buffers retain fallback drawing, which may change lighting and run more slowly.
- Rails and some other thin surfaces may flicker; the cause remains under investigation. End-portal visuals approximate the original shader.
- Minecraft torches do not yet supply light to the Zone's native renderer; holding one does not provide a flashlight. Placement requires Minecraft block support. The native SoC flashlight uses L when available.
- F9 obstacle escape is experimental. Save with F7 before using it.

[Report a problem](https://github.com/DeSoreGD/Steve-in-the-zone/issues/new/choose) · [Useful logs](REPORT-A-PROBLEM.md)
