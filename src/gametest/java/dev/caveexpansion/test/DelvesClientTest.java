package dev.caveexpansion.test;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.Function;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.mojang.datafixers.util.Pair;
import dev.caveexpansion.CaveExpansion;
import dev.caveexpansion.block.DelveBlocks;
import dev.caveexpansion.block.HauntBlock;
import dev.caveexpansion.resident.Residents;
import dev.caveexpansion.talk.DelveTalk;
import dev.caveexpansion.worldgen.Delves;
import dev.villagefriends.TalkWorld;
import dev.villagefriends.homestead.Homesteads;
import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.pools.SinglePoolElement;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;

/**
 * The delves in a real, generated world: each of the eight found the way /locate finds it, its pieces and
 * height checked, its residents (named, settled, talking from our own lines, trading, knowing a rumour), its
 * chests' loot tables, its guardians woken by a survival player, how far it stands from the Plata Clan's
 * hideouts, a screenshot or two from inside (with night vision), and a block dump for the offline cutaway.
 *   gradlew runClientGameTest -PcaveTests=Camp,Seam,... [-PtestHeap=2g] [-PcompatMods=<instance mods>]
 * Seed: -Dcaveexpansion.seed (default "cave expansion").
 */
@SuppressWarnings("UnstableApiUsage")
public class DelvesClientTest implements FabricClientGameTest {
    static final Path OUT = Path.of("delves");
    static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private final Map<String, Object> report = new LinkedHashMap<>();

    static void check(boolean ok, String what) { if (!ok) throw new AssertionError(what); }

    static boolean wanted(String scene) {
        String only = System.getProperty("caveexpansion.tests");
        return only == null || only.isBlank() || List.of(only.toLowerCase(Locale.ROOT).split(",")).contains(scene.toLowerCase(Locale.ROOT));
    }

    static <T> T onServer(TestSingleplayerContext w, Function<ServerLevel, T> fn) {
        return w.getServer().computeOnServer(s -> fn.apply(s.overworld()));
    }

    static ServerPlayer player(TestSingleplayerContext w) { return w.getConnection().getServerPlayer(); }

    static void shoot(ClientGameTestContext ctx, String name) {
        ctx.runOnClient(client -> client.gui.toastManager().clear());
        ctx.takeScreenshot(name);
    }

    static void settle(ClientGameTestContext ctx, TestSingleplayerContext w) {
        try { w.getConnection().waitForChunksRender(); } catch (AssertionError slow) { ctx.waitTicks(40); }
    }

    @Override
    public void runTest(ClientGameTestContext ctx) {
        if (Delves.KEYS.stream().noneMatch(DelvesClientTest::wanted) && !wanted("census")) return;
        JsonObject catalog = catalog();
        ctx.getInput().resizeWindow(1280, 800);
        ctx.runOnClient(client -> {
            client.options.guiScale().set(2);
            client.options.renderDistance().set(5);
            client.options.gamma().set(1.0);
            client.resizeGui();
        });
        String seed = System.getProperty("caveexpansion.seed", "cave expansion");
        try (TestSingleplayerContext w = ctx.worldBuilder().adjustSettings(ui -> {
            var normal = ui.getSettings().worldgenLoadContext().lookupOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.NORMAL);
            ui.setWorldType(new WorldCreationUiState.WorldTypeEntry(normal));
            ui.setGenerateStructures(true);
            ui.setSeed(seed);
        }).create()) {
            settle(ctx, w);
            for (String cmd : List.of("gamemode creative @a", "gamerule advance_time false", "gamerule advance_weather false",
                    "gamerule spawn_mobs false", "time set 6000", "weather clear", "difficulty normal",
                    "effect give @a minecraft:night_vision infinite 0 true")) {
                w.getServer().runCommand(cmd);
            }
            ctx.runOnClient(client -> { if (!client.gui.hud.isHidden()) client.gui.hud.toggle(); });
            fly(w);
            report.put("seed", seed);
            report.put("mods", FabricLoader.getInstance().getAllMods().stream().map(m -> m.getMetadata().getId()).filter(id -> !id.startsWith("fabric")
                    && !id.equals("java") && !id.equals("minecraft") && !id.equals("mixinextras")).sorted().toList());
            int n = 1;
            for (String key : Delves.KEYS) {
                if (!wanted(key)) continue;
                visit(ctx, w, key, catalog.getAsJsonObject(key), n++);
            }
            if (wanted("census")) census(w);
        } finally {
            try {
                Files.createDirectories(OUT);
                Files.writeString(OUT.resolve("report.json"), GSON.toJson(report), StandardCharsets.UTF_8);
            } catch (IOException e) { CaveExpansion.LOG.warn("couldn't write the test report", e); }
        }
    }

    static JsonObject catalog() {
        try (var in = DelvesClientTest.class.getResourceAsStream("/data/caveexpansion/caveexpansion/catalog.json")) {
            check(in != null, "the catalog (tools/delves/build.py) is in the jar");
            return GSON.fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), JsonObject.class);
        } catch (IOException e) { throw new AssertionError(e); }
    }

    static void fly(TestSingleplayerContext w) {
        w.getServer().runCommand("gamemode creative @a");
        onServer(w, level -> {
            ServerPlayer p = player(w);
            p.getAbilities().flying = true;
            p.onUpdateAbilities();
            return null;
        });
    }

    // -- finding a delve -------------------------------------------------------------------------------

    record Site(String key, BlockPos found, StructureStart start, Map<String, List<BoundingBox>> pieces) {
        BoundingBox core() { return this.start.getPieces().getFirst().getBoundingBox(); }
        BoundingBox all() { return this.start.getBoundingBox(); }
    }

    static String template(StructurePiece piece) {
        return piece instanceof PoolElementStructurePiece p && p.getElement() instanceof SinglePoolElement single
                ? single.getTemplateLocation().getPath() : piece.getClass().getSimpleName();
    }

    static Site find(TestSingleplayerContext w, String key) {
        Pair<BlockPos, Holder<Structure>> found = onServer(w, level -> {
            var holder = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).getOrThrow(Delves.key(key));
            return level.getChunkSource().getGenerator().findNearestMapStructure(level, HolderSet.direct(holder), BlockPos.ZERO, 60, false);
        });
        check(found != null, "a " + key + " generates in the world");
        BlockPos at = found.getFirst();
        Site site = onServer(w, level -> {
            ChunkAccess chunk = level.getChunk(at.getX() >> 4, at.getZ() >> 4, ChunkStatus.STRUCTURE_STARTS, true);
            for (var e : chunk.getAllStarts().entrySet()) {
                var id = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).getKey(e.getKey());
                if (id == null || !id.equals(CaveExpansion.id(key)) || !e.getValue().isValid()) continue;
                Map<String, List<BoundingBox>> pieces = new LinkedHashMap<>();
                for (StructurePiece piece : e.getValue().getPieces())
                    pieces.computeIfAbsent(template(piece), k -> new ArrayList<>()).add(piece.getBoundingBox());
                return new Site(key, at, e.getValue(), pieces);
            }
            return null;
        });
        check(site != null, "the " + key + "'s start at " + at);
        CaveExpansion.LOG.info("[delves test] {} at {}: {} pieces {}", key, at, site.start().getPieces().size(), site.pieces().keySet());
        return site;
    }

    // -- one delve -------------------------------------------------------------------------------------

    void visit(ClientGameTestContext ctx, TestSingleplayerContext w, String key, JsonObject info, int n) {
        Site site = find(w, key);
        Map<String, Object> facts = new LinkedHashMap<>();
        report.put(key, facts);
        facts.put("found", List.of(site.found().getX(), site.found().getY(), site.found().getZ()));
        facts.put("pieces", site.pieces().keySet());
        BoundingBox core = site.core();
        String startTemplate = template(site.start().getPieces().getFirst());
        var starts = info.getAsJsonArray("start").asList().stream().map(e -> e.getAsString()).toList();
        check(starts.contains(startTemplate), key + " starts with one of its start pieces: " + startTemplate);
        int minY = info.getAsJsonArray("depth").get(0).getAsInt(), maxY = info.getAsJsonArray("depth").get(1).getAsInt();
        check(core.minY() >= minY - 40 && core.minY() <= maxY + 2, key + " stands in its depth range " + minY + ".." + maxY + ": core " + core);
        facts.put("core", List.of(core.minX(), core.minY(), core.minZ(), core.maxX(), core.maxY(), core.maxZ()));

        // get there and let it load (residents load with their chunks)
        Vec3 target = onServer(w, level -> floorNear(level, core));
        look(ctx, w, target.add(0, 1.6, 0), target.add(3, 0, 3), 60);
        Vec3 eye = onServer(w, level -> roomView(level, core, target));
        look(ctx, w, eye, target, 30);
        shoot(ctx, String.format("delve-%02d-%s-1", n, key));
        Vec3 eye2 = onServer(w, level -> roomView(level, core, target.add((core.maxX() - core.minX()) / 4.0, 0, -(core.maxZ() - core.minZ()) / 4.0)));
        look(ctx, w, eye2, target, 15);
        shoot(ctx, String.format("delve-%02d-%s-2", n, key));

        // loot: every chest/barrel/pot of the delve that is loaded rolls one of our tables
        Map<String, Integer> loot = onServer(w, level -> loot(level, site.all()));
        facts.put("loot", loot);
        check(!loot.isEmpty(), key + " has containers with our loot: " + loot);
        for (String table : loot.keySet()) check(table.startsWith("caveexpansion:chests/" + key + "/") || table.startsWith("caveexpansion:chests/"),
                key + " loot table " + table);

        if (info.get("inhabited").getAsBoolean()) residents(ctx, w, site, info, facts);
        else haunts(ctx, w, site, info, facts);
        compat(w, site, facts);
        dump(w, site);
    }

    void residents(ClientGameTestContext ctx, TestSingleplayerContext w, Site site, JsonObject info, Map<String, Object> facts) {
        int expected = info.getAsJsonArray("start_residents").size();
        ctx.waitTicks(40);
        List<String> found = onServer(w, level -> {
            List<String> out = new ArrayList<>();
            for (Villager v : level.getEntitiesOfClass(Villager.class, AABB.of(site.core()).inflate(24))) {
                var r = Residents.of(v);
                var d = Homesteads.dweller(v);
                check(r != null && d != null && d.role().startsWith("caveexpansion_"), "every villager in a " + site.key() + " is settled as a delve resident: "
                        + v.getName().getString());
                check(v.hasCustomName() && v.getCustomName().getString().contains(d.place()), "nameplate names the place: " + v.getCustomName().getString());
                out.add(r.role() + ":" + BuiltInRegistries.VILLAGER_PROFESSION.getKey(v.getVillagerData().profession().value()) + ":" + v.getCustomName().getString());
            }
            return out;
        });
        facts.put("residents", found);
        check(found.size() >= expected, site.key() + " has its " + expected + " residents: " + found);
        // they talk from our own lines, know a rumour, and miners trade
        List<String> said = onServer(w, level -> {
            List<String> out = new ArrayList<>();
            ServerPlayer p = player(w);
            for (Villager v : level.getEntitiesOfClass(Villager.class, AABB.of(site.core()).inflate(24))) {
                String greet = TalkWorld.line(v, p, "greet");
                String news = TalkWorld.line(v, p, "news");
                check(greet != null && !greet.contains("{"), "a resident greets from our lines: " + greet);
                check(news != null, "and has news");
                var r = Residents.rumor(v, level);
                check(r != null && !r.rumor().isEmpty(), "a rumour was looked for");
                out.add(v.getCustomName().getString() + ": " + greet + " | " + news + " | rumour " + r.rumor() + " " + r.rumorDir() + " " + r.rumorDist());
                if (r.role().equals("miner") || r.role().equals("foreman")) {
                    check(!v.getOffers().isEmpty(), "a miner has trades");
                    check(DelveTalk.line(v, p, "work") != null, "and talks about work");
                }
            }
            return out;
        });
        facts.put("talk", said);
        // up close with one of them
        Vec3 face = onServer(w, level -> level.getEntitiesOfClass(Villager.class, AABB.of(site.core()).inflate(24)).getFirst().getEyePosition());
        look(ctx, w, onServer(w, level -> roomView(level, site.core(), face)), face, 20);
        shoot(ctx, "delve-" + site.key() + "-resident");
    }

    void haunts(ClientGameTestContext ctx, TestSingleplayerContext w, Site site, JsonObject info, Map<String, Object> facts) {
        if (info.getAsJsonArray("haunts").isEmpty()) return;
        BlockPos mark = onServer(w, level -> {
            BoundingBox all = site.all();
            for (BlockPos pos : BlockPos.betweenClosed(all.minX(), all.minY(), all.minZ(), all.maxX(), all.maxY(), all.maxZ()))
                if (level.isLoaded(pos) && level.getBlockState(pos).is(DelveBlocks.HAUNT)) return pos.immutable();
            return null;
        });
        if (mark == null) { facts.put("haunt", "not in the loaded pieces"); return; }
        String kind = onServer(w, level -> level.getBlockState(mark).getValue(HauntBlock.KIND).getSerializedName());
        // a survival player walks up to it
        w.getServer().runCommand(String.format(Locale.ROOT, "tp @a %d %d %d", mark.getX() + 8, mark.getY() + 1, mark.getZ()));
        w.getServer().runCommand("gamemode survival @a");
        ctx.waitTicks(40);
        int risen = onServer(w, level -> level.getEntitiesOfClass(Mob.class, new AABB(mark).inflate(8), m -> m instanceof Enemy && m.isAlive()).size());
        boolean gone = onServer(w, level -> !level.getBlockState(mark).is(DelveBlocks.HAUNT));
        facts.put("haunt", kind + " at " + mark.toShortString() + ": " + risen + " risen");
        check(gone && risen >= 1, "the " + kind + " guardians rise when a player comes near (" + risen + ")");
        Vec3 at = onServer(w, level -> {
            var up = level.getEntitiesOfClass(Mob.class, new AABB(mark).inflate(10), m -> m instanceof Enemy && m.isAlive());
            Vec3 sum = Vec3.ZERO;
            for (Mob m : up) sum = sum.add(m.getEyePosition());
            return up.isEmpty() ? Vec3.atCenterOf(mark) : sum.scale(1.0 / up.size());
        });
        w.getServer().runCommand("gamemode creative @a");
        fly(w);
        w.getServer().runOnServer(s -> {    // hold them still for the picture
            for (Mob m : s.overworld().getEntitiesOfClass(Mob.class, new AABB(mark).inflate(12), m -> m instanceof Enemy)) m.setNoAi(true);
        });
        look(ctx, w, onServer(w, level -> nearView(level, at)), at, 10);
        shoot(ctx, "delve-" + site.key() + "-guardians");
        w.getServer().runOnServer(s -> {
            for (Mob m : s.overworld().getEntitiesOfClass(Mob.class, new AABB(mark).inflate(24), m -> m instanceof Enemy)) m.discard();
        });
    }

    /** How far the delve stands from the Plata Clan's hideouts (and from villages). */
    void compat(TestSingleplayerContext w, Site site, Map<String, Object> facts) {
        if (!FabricLoader.getInstance().isModLoaded("plataclan")) return;
        BlockPos plata = onServer(w, level -> level.findNearestMapStructure(TagKey.create(Registries.STRUCTURE,
                Identifier.fromNamespaceAndPath("plataclan", "hideouts")), site.found(), 3, false));
        if (plata == null) { facts.put("plata", "none near"); return; }
        int chunks = Math.max(Math.abs((plata.getX() >> 4) - (site.found().getX() >> 4)), Math.abs((plata.getZ() >> 4) - (site.found().getZ() >> 4)));
        facts.put("plata", "nearest hideout " + chunks + " chunks away");
        check(chunks >= 3, site.key() + " keeps clear of the Plata Clan: hideout " + chunks + " chunks away");
    }

    // -- how rare they are ---------------------------------------------------------------------------------

    /**
     * Every placement cell of the delves' structure set in a 9 x 9 block of cells round the origin (about 4,300
     * blocks square): how many cells grew a delve, and of which kind.
     */
    void census(TestSingleplayerContext w) {
        Map<String, Object> out = onServer(w, level -> {
            var set = level.registryAccess().lookupOrThrow(Registries.STRUCTURE_SET)
                    .getOrThrow(net.minecraft.resources.ResourceKey.create(Registries.STRUCTURE_SET, CaveExpansion.id("delves"))).value();
            var placement = (dev.caveexpansion.worldgen.DelvePlacement) set.placement();
            int spacing = placement.spacing(), cells = 0, found = 0;
            Map<String, Integer> kinds = new LinkedHashMap<>();
            for (int gx = -4; gx <= 4; gx++) for (int gz = -4; gz <= 4; gz++) {
                cells++;
                var chunk = placement.getPotentialStructureChunk(level.getSeed(), gx * spacing, gz * spacing);
                ChunkAccess c = level.getChunk(chunk.x(), chunk.z(), ChunkStatus.STRUCTURE_STARTS, true);
                for (var e : c.getAllStarts().entrySet()) {
                    var id = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).getKey(e.getKey());
                    if (id == null || !id.getNamespace().equals(CaveExpansion.MOD_ID) || !e.getValue().isValid()) continue;
                    found++;
                    kinds.merge(id.getPath(), 1, Integer::sum);
                }
            }
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("cells", cells);
            m.put("cell_blocks", spacing * 16);
            m.put("delves", found);
            m.put("kinds", kinds);
            m.put("blocks_per_delve", found == 0 ? -1 : (int) Math.round(Math.sqrt((double) cells * spacing * 16 * spacing * 16 / found)));
            return m;
        });
        report.put("census", out);
        CaveExpansion.LOG.info("[delves test] census {}", out);
        check((int) out.get("delves") > 0, "delves generate: " + out);
    }

    // -- looking ----------------------------------------------------------------------------------------

    /** A spot a few blocks from `at` with a clear view of it. */
    static Vec3 nearView(ServerLevel level, Vec3 at) {
        for (double d : new double[]{4.5, 3.5, 6, 2.5}) for (double h : new double[]{1.2, .4, 2.2}) for (int a = 0; a < 360; a += 30) {
            double r = Math.toRadians(a);
            Vec3 eye = at.add(Math.cos(r) * d, h, Math.sin(r) * d);
            BlockPos cell = BlockPos.containing(eye);
            if (!level.getBlockState(cell).getCollisionShape(level, cell).isEmpty() || !level.getFluidState(cell).isEmpty()) continue;
            var hit = level.clip(new ClipContext(eye, at, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, CollisionContext.empty()));
            if (hit.getType() == HitResult.Type.MISS || hit.getLocation().distanceTo(at) < 1.2) return eye;
        }
        return at.add(3, 1, 3);
    }

    static void look(ClientGameTestContext ctx, TestSingleplayerContext w, Vec3 eye, Vec3 at, int ticks) {
        double dx = at.x - eye.x, dy = at.y - eye.y, dz = at.z - eye.z;
        float yaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
        float pitch = (float) -Math.toDegrees(Math.atan2(dy, Math.sqrt(dx * dx + dz * dz)));
        w.getServer().runCommand(String.format(Locale.ROOT, "tp @a %.2f %.2f %.2f %.1f %.1f", eye.x, eye.y - 1.62, eye.z, yaw, pitch));
        ctx.waitTicks(ticks);
        settle(ctx, w);
        ctx.waitTicks(10);
    }

    /** Standing height in the middle of the core piece: the first floor with two blocks of air above it. */
    static Vec3 floorNear(ServerLevel level, BoundingBox core) {
        int cx = (core.minX() + core.maxX()) / 2, cz = (core.minZ() + core.maxZ()) / 2;
        level.getChunk(cx >> 4, cz >> 4);
        for (int r = 0; r <= 6; r++) for (int dx = -r; dx <= r; dx++) for (int dz = -r; dz <= r; dz++) {
            if (Math.max(Math.abs(dx), Math.abs(dz)) != r) continue;
            for (int y = core.minY() + 1; y < core.maxY(); y++) {
                BlockPos p = new BlockPos(cx + dx, y, cz + dz);
                if (stand(level, p)) return Vec3.atBottomCenterOf(p);
            }
        }
        return new Vec3(cx + .5, core.minY() + 2, cz + .5);
    }

    static boolean stand(ServerLevel level, BlockPos p) {
        return level.getBlockState(p).getCollisionShape(level, p).isEmpty() && level.getBlockState(p.above()).getCollisionShape(level, p.above()).isEmpty()
                && level.getFluidState(p).isEmpty() && !level.getBlockState(p.below()).getCollisionShape(level, p.below()).isEmpty();
    }

    /** The open spot in the core piece with the longest clear view of `at` (a camera inside the room). */
    static Vec3 roomView(ServerLevel level, BoundingBox core, Vec3 at) {
        Vec3 best = at.add(0, 2, 0);
        double bestScore = -1;
        for (int x = core.minX() + 1; x < core.maxX(); x += 2) for (int z = core.minZ() + 1; z < core.maxZ(); z += 2)
            for (int y = core.minY() + 1; y < core.maxY(); y += 2) {
                BlockPos cell = new BlockPos(x, y, z);
                BlockState s = level.getBlockState(cell);
                if (!s.getCollisionShape(level, cell).isEmpty() || !s.getFluidState().isEmpty()) continue;
                Vec3 eye = Vec3.atCenterOf(cell);
                double d = eye.distanceTo(at);
                if (d < 4 || d > 22) continue;
                var hit = level.clip(new ClipContext(eye, at, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, CollisionContext.empty()));
                if (hit.getType() != HitResult.Type.MISS && hit.getLocation().distanceTo(at) > 1.2) continue;
                double score = d + (eye.y > at.y + 1 ? 2 : 0);
                if (score > bestScore) { bestScore = score; best = eye; }
            }
        return best;
    }

    static Map<String, Integer> loot(ServerLevel level, BoundingBox all) {
        Map<String, Integer> out = new LinkedHashMap<>();
        for (int cx = all.minX() >> 4; cx <= all.maxX() >> 4; cx++) for (int cz = all.minZ() >> 4; cz <= all.maxZ() >> 4; cz++) {
            if (!level.hasChunk(cx, cz)) continue;
            for (var be : level.getChunk(cx, cz).getBlockEntities().values()) {
                if (!(be instanceof RandomizableContainerBlockEntity c) || c.getLootTable() == null) continue;
                if (!all.isInside(be.getBlockPos())) continue;
                out.merge(c.getLootTable().identifier().toString(), 1, Integer::sum);
            }
        }
        for (Entity e : level.getEntitiesOfClass(Entity.class, AABB.of(all))) {
            if (e instanceof net.minecraft.world.entity.vehicle.minecart.MinecartChest cart && cart.getContainerLootTable() != null)
                out.merge(cart.getContainerLootTable().identifier() + " (cart)", 1, Integer::sum);
        }
        return out;
    }

    /** Plain rock the cutaway leaves out. */
    static final java.util.Set<String> ROCK = java.util.Set.of("minecraft:stone", "minecraft:deepslate", "minecraft:tuff", "minecraft:granite",
            "minecraft:diorite", "minecraft:andesite", "minecraft:dirt", "minecraft:gravel", "minecraft:bedrock", "minecraft:cave_air", "minecraft:air");

    /** Every block of the delve's pieces but plain rock and air (for tools/delves/cutaway.py). */
    static void dump(TestSingleplayerContext w, Site site) {
        Map<String, Object> blocks = onServer(w, level -> {
            Map<String, Object> out = new LinkedHashMap<>();
            BoundingBox all = site.all();
            out.put("origin", List.of(all.minX(), all.minY(), all.minZ()));
            List<Object> cells = new ArrayList<>();
            java.util.Set<Long> seen = new java.util.HashSet<>();
            for (StructurePiece piece : site.start().getPieces()) {
                BoundingBox b = piece.getBoundingBox();
                for (BlockPos p : BlockPos.betweenClosed(b.minX(), b.minY(), b.minZ(), b.maxX(), b.maxY(), b.maxZ())) {
                    if (!level.isLoaded(p) || !seen.add(p.asLong())) continue;
                    BlockState s = level.getBlockState(p);
                    if (ROCK.contains(BuiltInRegistries.BLOCK.getKey(s.getBlock()).toString())) continue;
                    cells.add(List.of(p.getX() - all.minX(), p.getY() - all.minY(), p.getZ() - all.minZ(),
                            s.toString().replace("Block{", "").replace("}", "")));
                }
            }
            out.put("cells", cells);
            return out;
        });
        try {
            Files.createDirectories(OUT);
            Files.writeString(OUT.resolve(site.key() + ".json"), new Gson().toJson(blocks), StandardCharsets.UTF_8);
        } catch (IOException e) { CaveExpansion.LOG.warn("couldn't dump {}", site.key(), e); }
    }
}
