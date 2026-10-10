package dev.deepdelves.worldgen;

import java.util.OptionalInt;
import java.util.SplittableRandom;

/**
 * Where in its depth range a delve should stand, from a few sampled columns of the world's noise (rock, the
 * open air of noise caves, aquifer water and lava). Pure and unit-tested; {@link DelveStructure} samples.
 *
 * <p>A delve is meant to be <i>found</i>: by someone caving, so it should break into a cave somewhere, and by
 * someone strip-mining, so most of it should sit in rock. The best floor is one where some of the sampled
 * columns are open at walking height (it touches caves) but not all of them (it doesn't float in a void), and
 * where no water or lava sits in the core, where a flood would ruin the place.
 */
public final class CaveSurvey {
    public static final byte ROCK = 0, OPEN = 1, FLUID = 2;
    /** How many of the first columns are the core (the centre and the inner ring): no fluid allowed there. */
    public static final int CORE = 9;

    private CaveSurvey() {}

    /**
     * The floor height to build on, or empty when nothing fits.
     *
     * @param columns  cell kinds per sampled column, index 0 = height {@code bottom}; the first {@link #CORE} are the core
     * @param bottom   the height of index 0 in every column
     * @param minFloor lowest allowed floor (the anchor floor block)
     * @param maxFloor highest allowed floor
     * @param clearance how far above the floor the core must be dry
     * @param seekCaves when true, a floor that touches no cave at all is not taken
     * @param seed      breaks ties between equally good floors
     */
    public static OptionalInt pick(byte[][] columns, int bottom, int minFloor, int maxFloor, int clearance, boolean seekCaves,
                                   long seed) {
        SplittableRandom random = new SplittableRandom(seed);
        int best = Integer.MIN_VALUE, bestFloor = 0;
        for (int floor = minFloor; floor <= maxFloor; floor++) {
            int score = score(columns, bottom, floor, clearance);
            if (score == Integer.MIN_VALUE) continue;
            if (seekCaves && score < 10) continue;
            score += random.nextInt(4);
            if (score > best) { best = score; bestFloor = floor; }
        }
        return best == Integer.MIN_VALUE ? OptionalInt.empty() : OptionalInt.of(bestFloor);
    }

    /** How good a floor is (higher is better), or {@code Integer.MIN_VALUE} when the core would be wet. */
    public static int score(byte[][] columns, int bottom, int floor, int clearance) {
        for (int i = 0; i < Math.min(CORE, columns.length); i++) {
            for (int y = floor - 1; y <= floor + clearance; y++) if (at(columns[i], bottom, y) == FLUID) return Integer.MIN_VALUE;
        }
        int open = 0;
        for (byte[] column : columns) {
            if (at(column, bottom, floor + 1) == OPEN || at(column, bottom, floor + 2) == OPEN || at(column, bottom, floor + 3) == OPEN) open++;
        }
        // touching caves is good, up to about half the samples; a floor open on every side floats in a void
        int score = Math.min(open, 6) * 10;
        if (open > columns.length * 3 / 4) score -= (open - columns.length * 3 / 4) * 12;
        return score;
    }

    private static byte at(byte[] column, int bottom, int y) {
        int i = y - bottom;
        return i < 0 || i >= column.length ? ROCK : column[i];
    }
}
