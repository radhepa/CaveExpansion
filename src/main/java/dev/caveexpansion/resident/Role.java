package dev.caveexpansion.resident;

import java.util.List;
import java.util.Locale;

import dev.villagefriends.routine.Routine.Block;

/**
 * Who lives in a delve: the camp's miners and their foreman, the Deepwatch's wardens (knights and archers) and
 * their captain, and the hermit. A delve's template tags each of them ({@code caveexpansion.resident.<id>}); this
 * gives the role its job, its talk, its words for what it is doing, and its day. Pure.
 */
public enum Role {
    MINER("miner", "miner", "caveexpansion:miner", 2, 18),
    FOREMAN("foreman", "foreman", "caveexpansion:miner", 4, 18),
    WARDEN_KNIGHT("warden_knight", "warden", "villagefriends:knight", 2, 20),
    WARDEN_ARCHER("warden_archer", "warden", "villagefriends:archer", 2, 20),
    CAPTAIN("captain", "captain", "villagefriends:knight", 4, 20),
    HERMIT("hermit", "hermit", "minecraft:cleric", 3, 12);

    public static final String TAG = "caveexpansion.resident.";
    public static final String DWELLER_PREFIX = "caveexpansion_";

    private final String id, talk, profession;
    private final int level, tether;

    Role(String id, String talk, String profession, int level, int tether) {
        this.id = id; this.talk = talk; this.profession = profession; this.level = level; this.tether = tether;
    }

    public String id() { return this.id; }
    /** Which lines they speak (data/caveexpansion/talk): miner, foreman, warden, captain or hermit. */
    public String talk() { return this.talk; }
    public String profession() { return this.profession; }
    public int level() { return this.level; }
    /** How far they stray from the middle of their delve before heading back. */
    public int tether() { return this.tether; }
    /** The role Village Friends keeps in their dweller record. */
    public String dwellerRole() { return DWELLER_PREFIX + this.talk; }
    public boolean guard() { return this == WARDEN_KNIGHT || this == WARDEN_ARCHER || this == CAPTAIN; }

    public static Role byId(String id) {
        for (Role r : values()) if (r.id.equals(id)) return r;
        return null;
    }

    /** The role an entity's tags give it, or null. */
    public static Role fromTags(java.util.Collection<String> tags) {
        for (String tag : tags) if (tag.startsWith(TAG)) { Role r = byId(tag.substring(TAG.length())); if (r != null) return r; }
        return null;
    }

    /** True for a Village Friends dweller role that is one of ours. */
    public static boolean ours(String dwellerRole) { return dwellerRole != null && dwellerRole.startsWith(DWELLER_PREFIX); }

    /** The personality that fits the life (Village Friends personalities: it sets hobby, values and body language too). */
    public String personality(long seed) {
        List<String> options = switch (this) {
            case MINER -> List.of("steadfast", "adventurous", "pragmatic", "warmhearted", "curious");
            case FOREMAN -> List.of("meticulous", "steadfast");
            case WARDEN_KNIGHT, WARDEN_ARCHER -> List.of("protective", "steadfast", "pragmatic");
            case CAPTAIN -> List.of("steadfast", "protective");
            case HERMIT -> List.of("curious", "imaginative");
        };
        return options.get((int) Math.floorMod(mix(seed), (long) options.size()));
    }

    /** Their nameplate: "Brannoc Hale of Copperdeep Camp", "Captain Ysolde Varn of Ironreach Post"... */
    public String label(String name, String place) {
        return switch (this) {
            case MINER -> name + " of " + place;
            case FOREMAN -> "Foreman " + name + " of " + place;
            case WARDEN_KNIGHT, WARDEN_ARCHER -> "Warden " + name + " of " + place;
            case CAPTAIN -> "Captain " + name + " of " + place;
            case HERMIT -> name + ", the Hermit of " + place;
        };
    }

    /**
     * Their day, down here: no tavern, bell or market, and no weather. Meals are eaten in the delve; hours a villager
     * would spend among neighbours go to the work of the place (or, for the hermit, their own pursuits). Wardens who
     * keep the watch ({@code watch}) and the captain keep it until midnight; everyone else sleeps at night.
     */
    public Block adjust(Block block, Block scheduled, int time, boolean watch) {
        int t = Math.floorMod(time, 24000);
        boolean keepsWatch = this == CAPTAIN || (this == WARDEN_KNIGHT || this == WARDEN_ARCHER) && watch;
        // 20:30 to midnight in Village Friends' clock (0 = 06:00)
        if (keepsWatch && t >= 14500 && t < 18000) return Block.NIGHT_WATCH;
        Block b = switch (block) {
            case SHELTER, STORM, SNOWED_IN, RAIN_WALK, SNOW_PLAY -> scheduled == null || scheduled == block ? Block.WORK : scheduled;
            default -> block;
        };
        return switch (b) {
            case LUNCH, LUNCH_TAVERN -> Block.LUNCH_HOME;
            case SUPPER_TAVERN -> Block.SUPPER;
            case TAVERN, PERFORM -> Block.EVENING;
            case SOCIAL, MARKET, LESSONS, PARTY, PLAY, PRAYER -> this == HERMIT ? Block.HOBBY : Block.WORK;
            case NIGHT_WATCH -> keepsWatch ? Block.NIGHT_WATCH : Block.SLEEP;
            case DEFEND -> Block.WORK;
            case SHELTER, STORM, SNOWED_IN, RAIN_WALK, SNOW_PLAY -> Block.WORK;
            default -> b;
        };
    }

    /** What they're doing, as their conversation window shows it; null to keep Village Friends' own words. */
    public String doing(Block block) {
        return switch (this) {
            case MINER -> switch (block) {
                case WORK -> "Working the face"; case HOBBY -> "Sorting ore"; case EVENING -> "By the cookfire";
                case LUNCH_HOME, SUPPER, BREAKFAST -> "Eating with the crew"; default -> null; };
            case FOREMAN -> switch (block) {
                case WORK -> "Keeping the Ore Ledger"; case HOBBY -> "Checking the props"; case EVENING -> "Going over the tallies";
                case LUNCH_HOME, SUPPER, BREAKFAST -> "Eating with the crew"; default -> null; };
            case WARDEN_KNIGHT, WARDEN_ARCHER -> switch (block) {
                case WORK -> "Drilling at the post"; case HOBBY -> "Mending kit"; case EVENING -> "Off watch";
                case NIGHT_WATCH -> "Keeping the watch on the road"; case LUNCH_HOME, SUPPER, BREAKFAST -> "At mess"; default -> null; };
            case CAPTAIN -> switch (block) {
                case WORK -> "Inspecting the post"; case HOBBY -> "Reading the Watch Log"; case EVENING -> "Writing the Watch Log";
                case NIGHT_WATCH -> "Watching the Deepgate"; case LUNCH_HOME, SUPPER, BREAKFAST -> "At mess"; default -> null; };
            case HERMIT -> switch (block) {
                case WORK -> "Tending the mushrooms"; case HOBBY -> "Brewing"; case EVENING -> "Listening to the stone";
                case LUNCH_HOME, SUPPER, BREAKFAST -> "Eating mushroom stew"; default -> null; };
        };
    }

    /** "Lives at" line for their About page. */
    public String about(String place) {
        return switch (this) {
            case MINER, FOREMAN -> "\nLives at: " + place + " (a Delvers' Guild camp, deep underground)";
            case WARDEN_KNIGHT, WARDEN_ARCHER, CAPTAIN -> "\nPosted at: " + place + " (the Deepwatch, deep underground)";
            case HERMIT -> "\nLives at: " + place + " (alone, deep underground)";
        };
    }

    public String lower() { return this.id.toLowerCase(Locale.ROOT); }

    static long mix(long seed) {
        long z = seed * 0x9E3779B97F4A7C15L;
        z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
        return z ^ (z >>> 31);
    }
}
