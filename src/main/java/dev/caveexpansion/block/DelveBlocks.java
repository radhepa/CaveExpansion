package dev.caveexpansion.block;

import java.util.Set;
import java.util.function.Function;

import dev.caveexpansion.CaveExpansion;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;

/** The miner's prospecting table and the invisible mark where a delve's guardians wait. */
public final class DelveBlocks {
    private DelveBlocks() {}

    public static final ProspectingTableBlock PROSPECTING_TABLE = register("prospecting_table", ProspectingTableBlock::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2.5F).sound(SoundType.WOOD).noOcclusion().ignitedByLava());
    public static final HauntBlock HAUNT = register("haunt", HauntBlock::new, BlockBehaviour.Properties.of()
            .noCollision().noOcclusion().noLootTable().strength(-1.0F, 3600000.0F).replaceable().noTerrainParticles()
            .pushReaction(PushReaction.POPPED));

    public static final BlockEntityType<HauntBlockEntity> HAUNT_ENTITY = Registry.register(BuiltInRegistries.BLOCK_ENTITY_TYPE,
            CaveExpansion.id("haunt"), new BlockEntityType<>(HauntBlockEntity::new, Set.of(HAUNT)));

    public static final Item PROSPECTING_TABLE_ITEM = Registry.register(BuiltInRegistries.ITEM, CaveExpansion.id("prospecting_table"),
            new BlockItem(PROSPECTING_TABLE, new Item.Properties().setId(ResourceKey.create(Registries.ITEM, CaveExpansion.id("prospecting_table")))
                    .useBlockDescriptionPrefix()));

    private static <B extends Block> B register(String id, Function<BlockBehaviour.Properties, B> factory, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = ResourceKey.create(Registries.BLOCK, CaveExpansion.id(id));
        return Registry.register(BuiltInRegistries.BLOCK, key, factory.apply(props.setId(key)));
    }

    public static void register() {}
}
