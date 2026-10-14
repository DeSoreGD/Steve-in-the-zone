"""Generate only 1.20.1 save metadata; Minecraft generates fresh void chunks.

No source world, UUID, history, player data, region files or game assets required.
Never overwrite an existing save. nbtlib is a setup dependency, not Minecraft data.
"""
from pathlib import Path


def create_demo_world(output: Path, game_mode: str = 'creative') -> None:
    from nbtlib import File, Compound, String, Int, Long, Byte, Short, Float, Double, List
    if output.exists():
        raise FileExistsError("Демо-мир уже существует; автоматический запуск его не заменяет.")
    if game_mode not in ('creative','survival'):
        raise ValueError('Unknown world game mode')
    survival=game_mode=='survival'
    kit = [("minecraft:stone", 64), ("minecraft:dirt", 64), ("minecraft:oak_planks", 64),
           ("minecraft:tnt", 16), ("minecraft:flint_and_steel", 1), ("minecraft:diamond_sword", 1),
           ("minecraft:bow", 1), ("stalkercraft:bloodsucker_spawn_egg", 8), ("minecraft:cooked_beef", 16),
           ("minecraft:arrow", 64), ("minecraft:cobblestone", 64), ("minecraft:stone_slab", 64)]
    if survival:
        kit=[('minecraft:stone_sword',1),('minecraft:stone_pickaxe',1),('minecraft:oak_planks',32),
             ('minecraft:dirt',64),('minecraft:bread',8),('minecraft:torch',8),('minecraft:crafting_table',1)]
    player = Compound({
        "Dimension": String("minecraft:overworld"), "playerGameType": Int(0 if survival else 1),
        "Pos": List[Double]([Double(.5), Double(66), Double(.5)]),
        "Motion": List[Double]([Double(0), Double(0), Double(0)]),
        "Rotation": List[Float]([Float(0), Float(0)]), "FallDistance": Float(0),
        "Health": Float(20), "Air": Short(300), "foodLevel": Int(20),
        "foodSaturationLevel": Float(5), "foodExhaustionLevel": Float(0),
        "XpLevel": Int(0), "XpP": Float(0), "XpTotal": Int(0), "SelectedItemSlot": Int(0),
        "abilities": Compound({"flying": Byte(0 if survival else 1), "mayfly": Byte(0 if survival else 1), "instabuild": Byte(0 if survival else 1),
            "invulnerable": Byte(0 if survival else 1), "mayBuild": Byte(1), "flySpeed": Float(.05), "walkSpeed": Float(.1)}),
        "Inventory": List[Compound]([Compound({"Slot": Byte(i), "id": String(item), "Count": Byte(count)})
                                    for i, (item, count) in enumerate(kit)]),
    })
    armor=[(100,'leather_boots'),(102,'leather_chestplate')] if survival else [(100,'diamond_boots'),(101,'diamond_leggings'),(102,'diamond_chestplate'),(103,'diamond_helmet')]
    for slot,item in armor:
        player['Inventory'].append(Compound({'Slot':Byte(slot),'id':String('minecraft:'+item),'Count':Byte(1)}))
    if survival:player['Tags']=List[String]([String('stalkercraft_campaign_starter_v1')])
    data = Compound({
        "DataVersion": Int(3465), "version": Int(19133),
        "Version": Compound({"Id": Int(3465), "Name": String("1.20.1"), "Snapshot": Byte(0)}),
        "LevelName": String("Stalker mirror"), "GameType": Int(0 if survival else 1), "hardcore": Byte(0),
        "allowCommands": Byte(1), "initialized": Byte(1), "Difficulty": Byte(2), "DifficultyLocked": Byte(0),
        "SpawnX": Int(0), "SpawnY": Int(66), "SpawnZ": Int(0), "SpawnAngle": Float(0),
        "Time": Long(0), "DayTime": Long(6000), "LastPlayed": Long(0),
        "raining": Byte(0), "thundering": Byte(0), "rainTime": Int(0), "thunderTime": Int(0),
        "GameRules": Compound({"doMobSpawning": String("false"), "doWeatherCycle": String("false"),
            "doDaylightCycle": String("false"), "doTraderSpawning": String("false"),
            "doPatrolSpawning": String("false"), "keepInventory": String("true")}),
        "DataPacks": Compound({"Enabled": List[String]([String("vanilla")]), "Disabled": List[String]([])}),
        "enabled_features": List[String]([String("minecraft:vanilla")]),
        "WorldGenSettings": Compound({"seed": Long(0), "generate_features": Byte(0), "bonus_chest": Byte(0),
            "dimensions": Compound({"minecraft:overworld": Compound({"type": String("minecraft:overworld"),
                "generator": Compound({"type": String("minecraft:flat"), "settings": Compound({
                    "biome": String("minecraft:the_void"), "features": Byte(0), "lakes": Byte(0),
                    "layers": List[Compound]([]), "structure_overrides": List[String]([])})})})})}),
        "Player": player,
    })
    # Finish in a sibling staging directory; a failed write leaves no half-world.
    stage = output.with_name(output.name + ".preparing")
    stage.mkdir(parents=True, exist_ok=False)
    try:
        File({"Data": data}, gzipped=True).save(stage / "level.dat")
        stage.rename(output)
    except Exception:
        (stage / "level.dat").unlink(missing_ok=True)
        stage.rmdir()
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    create_demo_world(parser.parse_args().output)
