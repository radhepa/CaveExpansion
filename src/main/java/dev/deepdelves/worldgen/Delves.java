package dev.deepdelves.worldgen;

import java.util.List;

import dev.deepdelves.DeepDelves;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.Structure;

/**
 * The eight delves (data/deepdelves/worldgen, written by tools/delves/build.py) and the worldgen types they use.
 */
public final class Delves {
    private Delves() {}

    /** Every delve, in the order the docs list them. */
    public static final List<String> KEYS = List.of("camp", "seam", "post", "cistern", "hermit", "grotto", "ossuary", "forge");
    public static final TagKey<Structure> ALL = TagKey.create(Registries.STRUCTURE, DeepDelves.id("delves"));
    public static final TagKey<Structure> INHABITED = TagKey.create(Registries.STRUCTURE, DeepDelves.id("inhabited"));

    public static ResourceKey<Structure> key(String delve) {
        return ResourceKey.create(Registries.STRUCTURE, DeepDelves.id(delve));
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
        Registry.register(BuiltInRegistries.STRUCTURE_TYPE, DeepDelves.id("delve"), DelveStructure.TYPE);
        Registry.register(BuiltInRegistries.STRUCTURE_PLACEMENT, DeepDelves.id("spread"), DelvePlacement.CODEC);
        Registry.register(BuiltInRegistries.STRUCTURE_PROCESSOR, DeepDelves.id("natural"), NaturalProcessor.CODEC);
    }
}
