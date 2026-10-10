package dev.deepdelves.resident;

import java.util.Set;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableSet;
import dev.deepdelves.DeepDelves;
import dev.deepdelves.block.DelveBlocks;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import net.fabricmc.fabric.api.object.builder.v1.world.poi.PoiHelper;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.entity.npc.villager.VillagerProfession;
import net.minecraft.world.item.trading.TradeSet;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The miner: a Delvers' Guild profession whose job site is the prospecting table. Trades (five levels, in
 * data/deepdelves/villager_trade/miner) buy the ores you dig and sell what a delver needs: torches, ladders,
 * lanterns, rails, TNT, a copper helmet, picks, and a survey map to the nearest other delve.
 */
public final class MinerJob {
    private MinerJob() {}

    public static final ResourceKey<VillagerProfession> MINER = ResourceKey.create(Registries.VILLAGER_PROFESSION, DeepDelves.id("miner"));
    public static final ResourceKey<PoiType> POI = ResourceKey.create(Registries.POINT_OF_INTEREST_TYPE, DeepDelves.id("miner"));

    public static void register() {
        Set<BlockState> states = DelveBlocks.PROSPECTING_TABLE.getStateDefinition().getPossibleStates().stream().collect(Collectors.toSet());
        PoiHelper.register(DeepDelves.id("miner"), 1, 1, states);
        var trades = new Int2ObjectOpenHashMap<ResourceKey<TradeSet>>();
        for (int level = 1; level <= 5; level++) trades.put(level, ResourceKey.create(Registries.TRADE_SET, DeepDelves.id("miner/level_" + level)));
        Registry.register(BuiltInRegistries.VILLAGER_PROFESSION, MINER, new VillagerProfession(
                Component.translatable("entity.deepdelves.villager.miner"), holder -> holder.is(POI), holder -> holder.is(POI),
                ImmutableSet.of(), ImmutableSet.of(), SoundEvents.VILLAGER_WORK_TOOLSMITH, trades));
    }
}
