package dev.deepdelves;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Arrays;
import java.util.OptionalInt;

import dev.deepdelves.resident.Places;
import dev.deepdelves.resident.Role;
import dev.deepdelves.worldgen.CaveSurvey;
import dev.villagefriends.routine.Routine.Block;
import org.junit.jupiter.api.Test;

/** Where delves stand, how rare they are, and who lives in them. */
class DelvesLogicTest {
    private static final int BOTTOM = -20, HEIGHT = 80;

    private static byte[][] rock(int columns) {
        byte[][] out = new byte[columns][HEIGHT];
        for (byte[] c : out) Arrays.fill(c, CaveSurvey.ROCK);
        return out;
    }

    private static void open(byte[] column, int fromY, int toY) {
        for (int y = fromY; y <= toY; y++) column[y - BOTTOM] = CaveSurvey.OPEN;
    }

    @Test
    void solidRockHasNoCaveToTouch() {
        byte[][] columns = rock(13);
        assertTrue(CaveSurvey.pick(columns, BOTTOM, -10, 40, 10, true, 1L).isEmpty(), "seeking caves, solid rock gives nothing");
        assertTrue(CaveSurvey.pick(columns, BOTTOM, -10, 40, 10, false, 1L).isPresent(), "not seeking caves, any height will do");
    }

    @Test
    void floorLandsWhereACaveOpens() {
        byte[][] columns = rock(13);
        open(columns[10], 12, 15);      // a cave beside the outer ring at y 12..15
        open(columns[3], 13, 14);
        OptionalInt floor = CaveSurvey.pick(columns, BOTTOM, -10, 40, 10, true, 7L);
        assertTrue(floor.isPresent());
        int f = floor.getAsInt();
        assertTrue(f + 1 <= 15 && f + 3 >= 12, "walking height touches the cave: floor " + f);
    }

    @Test
    void waterInTheCoreIsRefused() {
        byte[][] columns = rock(13);
        for (int i = 0; i < 13; i++) open(columns[i], 0, 30);
        for (int y = -20; y < 60; y++) columns[0][y - BOTTOM] = CaveSurvey.FLUID;    // a flooded centre column
        assertTrue(CaveSurvey.pick(columns, BOTTOM, -10, 40, 10, true, 3L).isEmpty());
        assertEquals(Integer.MIN_VALUE, CaveSurvey.score(columns, BOTTOM, 5, 10));
    }

    @Test
    void aFloatingFloorScoresBelowATouchingOne() {
        byte[][] columns = rock(13);
        for (int i = 0; i < 13; i++) open(columns[i], 30, 40);    // everything open at 30..40: a void
        open(columns[4], 5, 7);
        open(columns[11], 5, 7);
        assertTrue(CaveSurvey.score(columns, BOTTOM, 4, 10) > CaveSurvey.score(columns, BOTTOM, 31, 5));
    }

    @Test
    void rarityStretchesTheGrid() {
        assertArrayEquals(new int[]{30, 12}, DelvesConfig.scaled(30, 12, 1.0));
        assertArrayEquals(new int[]{60, 24}, DelvesConfig.scaled(30, 12, 2.0));
        int[] dense = DelvesConfig.scaled(30, 12, .25);
        assertTrue(dense[0] > dense[1] && dense[0] >= 4, Arrays.toString(dense));
        assertEquals(1.0, DelvesConfig.clamp(Double.NaN));
        assertEquals(4.0, DelvesConfig.clamp(99));
        assertEquals(.25, DelvesConfig.clamp(0));
    }

    private static void assertArrayEquals(int[] want, int[] got) { assertEquals(Arrays.toString(want), Arrays.toString(got)); }

    @Test
    void rolesComeFromTags() {
        assertEquals(Role.MINER, Role.fromTags(java.util.List.of("other", "deepdelves.resident.miner")));
        assertEquals(Role.CAPTAIN, Role.fromTags(java.util.List.of("deepdelves.resident.captain")));
        assertNull(Role.fromTags(java.util.List.of("villagefriends.dweller.pariah")));
        assertEquals("deepdelves_warden", Role.WARDEN_ARCHER.dwellerRole());
        assertTrue(Role.ours("deepdelves_hermit"));
        assertFalse(Role.ours("veteran"));
        for (Role r : Role.values()) {
            assertNotNull(r.doing(Block.WORK), r + " says what work it does");
            assertFalse(r.personality(42).isBlank());
        }
    }

    @Test
    void theirDayHasNoTavernAndOnlyTheWatchStaysUp() {
        int noon = 6000, ten = 16000, three = 21000;
        assertEquals(Block.LUNCH_HOME, Role.MINER.adjust(Block.LUNCH_TAVERN, Block.LUNCH_TAVERN, noon, false));
        assertEquals(Block.EVENING, Role.HERMIT.adjust(Block.TAVERN, Block.TAVERN, ten, false));
        assertEquals(Block.WORK, Role.MINER.adjust(Block.MARKET, Block.MARKET, noon, false));
        assertEquals(Block.HOBBY, Role.HERMIT.adjust(Block.SOCIAL, Block.SOCIAL, noon, false));
        assertEquals(Block.NIGHT_WATCH, Role.CAPTAIN.adjust(Block.SLEEP, Block.SLEEP, ten, false));
        assertEquals(Block.NIGHT_WATCH, Role.WARDEN_ARCHER.adjust(Block.EVENING, Block.EVENING, ten, true));
        assertEquals(Block.EVENING, Role.WARDEN_ARCHER.adjust(Block.EVENING, Block.EVENING, ten, false));
        assertEquals(Block.SLEEP, Role.MINER.adjust(Block.NIGHT_WATCH, Block.NIGHT_WATCH, three, false));
        assertEquals(Block.WORK, Role.MINER.adjust(Block.STORM, Block.WORK, noon, false), "no weather underground");
    }

    @Test
    void placesAndWays() {
        assertTrue(Places.name("camp", 1).endsWith("Camp"));
        assertTrue(Places.name("post", 1).endsWith("Post"));
        assertTrue(Places.name("hermit", 1).contains("Hollow"));
        assertEquals(Places.name("camp", 77), Places.name("camp", 77), "the same delve keeps its name");
        assertEquals("north", Places.direction(0, -10));
        assertEquals("south-east", Places.direction(10, 10));
        assertEquals("west", Places.direction(-10, 1));
        assertEquals("a short walk", Places.distance(100));
        assertEquals("a long walk", Places.distance(600));
    }
}
