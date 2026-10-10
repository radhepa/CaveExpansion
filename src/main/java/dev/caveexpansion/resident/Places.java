package dev.caveexpansion.resident;

import java.util.List;

/** The names of the lived-in delves: the same for everyone who lives there, different from delve to delve. Pure. */
public final class Places {
    private Places() {}

    static final List<String> CAMPS = List.of("Copperdeep Camp", "Greyvein Camp", "Tallowstone Camp", "Ironhollow Camp", "Brightseam Camp",
            "Coalmouth Camp", "Redrock Camp", "Lodestar Camp", "Deepcut Camp", "Bellrock Camp", "Gritwater Camp", "Slatefall Camp",
            "Hammerhole Camp", "Old Pick Camp", "Lanternreach Camp", "Flintback Camp", "Cinderseam Camp", "Mossprop Camp");
    static final List<String> POSTS = List.of("Ironreach Post", "Blackstair Post", "Gloomgate Post", "Stonewatch Post", "Hollowmarch Post",
            "Lowfire Post", "Cinderhold Post", "Graywall Post", "Deepford Post", "Shadewatch Post", "Rookhold Post", "Lanternguard Post",
            "Underbridge Post", "Coldkeep Post");
    static final List<String> HOLLOWS = List.of("Old Moss Hollow", "Capwood Hollow", "Glowcap Hollow", "Dimmering Hollow", "Puffball Hollow",
            "Stillwater Hollow", "Rootdeep Hollow", "Velvetcap Hollow", "Lantern Moss Hollow", "Quiet Hollow", "Sporefall Hollow", "Dewdrip Hollow");

    /** The name of a delve of this kind ("camp", "post", "hermit"), picked by its seed. */
    public static String name(String delve, long seed) {
        List<String> names = switch (delve) {
            case "post" -> POSTS;
            case "hermit" -> HOLLOWS;
            default -> CAMPS;
        };
        return names.get((int) Math.floorMod(Role.mix(seed), (long) names.size()));
    }

    /** "north-east", "south"... from (dx, dz), x east and z south. */
    public static String direction(double dx, double dz) {
        String[] names = {"east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"};
        double angle = Math.toDegrees(Math.atan2(dz, dx));
        int i = (int) Math.floorMod(Math.round(angle / 45.0), 8L);
        return names[i];
    }

    /** How far, as a delver would put it. */
    public static String distance(double blocks) {
        if (blocks < 160) return "a short walk";
        if (blocks < 400) return "a few hundred paces";
        if (blocks < 800) return "a long walk";
        if (blocks < 1400) return "most of a day's crawl";
        return "further than most go";
    }
}
