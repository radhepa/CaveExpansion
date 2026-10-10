package dev.caveexpansion;

import dev.caveexpansion.block.DelveBlocks;
import dev.caveexpansion.resident.MinerJob;
import dev.caveexpansion.resident.Residents;
import dev.caveexpansion.talk.DelveTalk;
import dev.caveexpansion.worldgen.Delves;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.Event;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.npc.villager.Villager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Cave Expansion: rare underground places for the Village Friends modpack. See DESIGN.md.
 */
public final class CaveExpansion implements ModInitializer {
    public static final String MOD_ID = "caveexpansion";
    public static final Logger LOG = LoggerFactory.getLogger("Cave Expansion");

    public static Identifier id(String path) { return Identifier.fromNamespaceAndPath(MOD_ID, path); }

    @Override
    public void onInitialize() {
        DelvesConfig.get();
        Delves.register();
        DelveBlocks.register();
        MinerJob.register();
        Residents.register();
        DelveTalk.register();

        // Settle our residents before Village Friends looks at a newly loaded villager, so it never tries to put
        // them in a village.
        Identifier early = id("before_village_friends");
        ServerEntityEvents.ENTITY_LOAD.addPhaseOrdering(early, Event.DEFAULT_PHASE);
        ServerEntityEvents.ENTITY_LOAD.register(early, (entity, level) -> { if (entity instanceof Villager v) Residents.settle(v); });
        ServerEntityEvents.ENTITY_UNLOAD.register((entity, level) -> { if (entity instanceof Villager v) Residents.unloaded(v); });
        ServerTickEvents.END_SERVER_TICK.register(Residents::tick);
        ServerLifecycleEvents.SERVER_STOPPED.register(server -> Residents.clear());

        CreativeModeTabEvents.modifyOutputEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("functional_blocks")))
                .register(out -> out.accept(DelveBlocks.PROSPECTING_TABLE_ITEM));
        LOG.info("Cave Expansion ready (rarity {})", DelvesConfig.get().rarity());
    }
}
