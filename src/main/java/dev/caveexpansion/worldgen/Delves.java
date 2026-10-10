package dev.caveexpansion.worldgen;

import java.util.List;

import dev.caveexpansion.CaveExpansion;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.Structure;

/**
 * The eight delves (data/caveexpansion/worldgen, written by tools/delves/build.py) and the worldgen types they use.
 */
public final class Delves {
    private Delves() {}

    /** Every delve, in the order the docs list them. */
    public static final List<String> KEYS = List.of("camp", "seam", "post", "cistern", "hermit", "grotto", "ossuary", "forge");
    public static final TagKey<Structure> ALL = TagKey.create(Registries.STRUCTURE, CaveExpansion.id("delves"));
    public static final TagKey<Structure> INHABITED = TagKey.create(Registries.STRUCTURE, CaveExpansion.id("inhabited"));

    public static ResourceKey<Structure> key(String delve) {
        return ResourceKey.create(Registries.STRUCTURE, CaveExpansion.id(delve));
    }

    /** What residents call a delve when they tell you about it (it includes its article). */
    public static String describe(String delve) {
        return switch (delve) {
            case "camp" -> "a Delvers' camp";
            case "seam" -> "the old buried seam, the camp the roof came down on";
            case "post" -> "a Deepwatch post";
            case "cistern" -> "a drowned cistern of the Old Delvers";
            case "hermit" -> "a hollow where some old hermit grows mushrooms";
            case "grotto" -> "a cavern that glitters like the inside of a geode";
            case "ossuary" -> "the Old Delvers' bone-halls";
            case "forge" -> "an old forge-hall of the Old Delvers, down by the lava";
            default -> "something strange";
        };
    }

    public static void register() {
        Registry.register(BuiltInRegistries.STRUCTURE_TYPE, CaveExpansion.id("delve"), DelveStructure.TYPE);
        Registry.register(BuiltInRegistries.STRUCTURE_PLACEMENT, CaveExpansion.id("spread"), DelvePlacement.CODEC);
        Registry.register(BuiltInRegistries.STRUCTURE_PROCESSOR, CaveExpansion.id("natural"), NaturalProcessor.CODEC);
    }
}
