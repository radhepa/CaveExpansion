package dev.caveexpansion.worldgen;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.OptionalInt;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.caveexpansion.CaveExpansion;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.QuartPos;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.NoiseColumn;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.PoolElementStructurePiece;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePiecesBuilder;
import net.minecraft.world.level.levelgen.structure.pools.JigsawPlacement;
import net.minecraft.world.level.levelgen.structure.pools.SinglePoolElement;
import net.minecraft.world.level.levelgen.structure.pools.StructureTemplatePool;
import net.minecraft.world.level.levelgen.structure.pools.alias.PoolAliasLookup;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;
import net.minecraft.world.level.levelgen.structure.templatesystem.LiquidSettings;

/**
 * A delve: a jigsaw structure set into the rock somewhere in its depth range.
 *
 * <p>Before it grows it samples the world's noise around the chunk ({@link CaveSurvey}) and picks a floor
 * height that touches a cave and has no water or lava in its core. The start piece's anchor jigsaw (a floor
 * block in its main room) is put at that height. Once the pieces are assembled every one of them must keep
 * {@code cover} blocks of ground above it: an exposed piece at the end of a branch is dropped, and a delve whose
 * core would break the surface (or the sea floor) is not built here at all. Never in the Deep Dark.
 */
public final class DelveStructure extends Structure {
    public record Depth(int minY, int maxY) {
        public static final Codec<Depth> CODEC = RecordCodecBuilder.create(i -> i.group(
                Codec.intRange(-64, 320).fieldOf("min_y").forGetter(Depth::minY),
                Codec.intRange(-64, 320).fieldOf("max_y").forGetter(Depth::maxY)).apply(i, Depth::new));
    }

    public static final Identifier ANCHOR = CaveExpansion.id("anchor");

    public static final MapCodec<DelveStructure> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            settingsCodec(i),
            StructureTemplatePool.CODEC.fieldOf("start_pool").forGetter(s -> s.startPool),
            Codec.intRange(0, 20).fieldOf("size").forGetter(s -> s.size),
            JigsawStructure.MaxDistance.CODEC.fieldOf("max_distance_from_center").forGetter(s -> s.maxDistance),
            Depth.CODEC.fieldOf("depth").forGetter(s -> s.depth),
            Codec.intRange(0, 64).optionalFieldOf("cover", 10).forGetter(s -> s.cover),
            Codec.BOOL.optionalFieldOf("seek_caves", true).forGetter(s -> s.seekCaves),
            Codec.intRange(2, 32).optionalFieldOf("clearance", 10).forGetter(s -> s.clearance),
            Identifier.CODEC.optionalFieldOf("require").forGetter(s -> s.require),
            Codec.floatRange(0F, 1F).optionalFieldOf("chance", 1F).forGetter(s -> s.chance)
    ).apply(i, DelveStructure::new));
    public static final StructureType<DelveStructure> TYPE = () -> CODEC;

    /** Sampled columns: the centre, an inner ring (radius 8) and an outer ring (radius 16). */
    private static final int[][] SAMPLES = {{0, 0}, {8, 0}, {-8, 0}, {0, 8}, {0, -8}, {6, 6}, {-6, 6}, {6, -6}, {-6, -6},
            {16, 0}, {-16, 0}, {0, 16}, {0, -16}};
    /** No piece may reach down into the bedrock layers. */
    private static final int FLOOR_LIMIT = -58;

    private final Holder<StructureTemplatePool> startPool;
    private final int size;
    private final JigsawStructure.MaxDistance maxDistance;
    private final Depth depth;
    private final int cover;
    private final boolean seekCaves;
    private final int clearance;
    private final Optional<Identifier> require;
    /**
     * How often this delve takes a spot the structure set offers it. The set falls through to another delve when one
     * can't stand somewhere, which evens the kinds out; a chance below 1 keeps the rarest kinds rare.
     */
    private final float chance;

    public DelveStructure(StructureSettings settings, Holder<StructureTemplatePool> startPool, int size, JigsawStructure.MaxDistance maxDistance,
                          Depth depth, int cover, boolean seekCaves, int clearance, Optional<Identifier> require, float chance) {
        super(settings);
        this.startPool = startPool;
        this.size = size;
        this.maxDistance = maxDistance;
        this.depth = depth;
        this.cover = cover;
        this.seekCaves = seekCaves;
        this.clearance = clearance;
        this.require = require;
        this.chance = chance;
    }

    @Override public StructureType<?> type() { return TYPE; }

    public Depth depth() { return this.depth; }

    private static int surface(GenerationContext c, int x, int z) {
        return c.chunkGenerator().getFirstOccupiedHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, c.heightAccessor(), c.randomState());
    }

    private static int floor(GenerationContext c, int x, int z) {
        return c.chunkGenerator().getFirstOccupiedHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, c.heightAccessor(), c.randomState());
    }

    /** The lowest solid ground over (x, z): the sea floor under water, the land elsewhere. */
    private static int ground(GenerationContext c, int x, int z) {
        return Math.min(surface(c, x, z), floor(c, x, z));
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext context) {
        if (this.chance < 1F && context.random().nextFloat() >= this.chance) return Optional.empty();
        int cx = context.chunkPos().getMiddleBlockX(), cz = context.chunkPos().getMiddleBlockZ();
        int ground = Integer.MAX_VALUE;
        for (int[] s : SAMPLES) ground = Math.min(ground, ground(context, cx + s[0], cz + s[1]));
        int top = Math.min(this.depth.maxY(), ground - this.cover - this.clearance);
        if (top < this.depth.minY()) return Optional.empty();

        int bottom = this.depth.minY() - 2, height = top + this.clearance + 2 - bottom;
        byte[][] columns = new byte[SAMPLES.length][];
        for (int i = 0; i < SAMPLES.length; i++) columns[i] = column(context, cx + SAMPLES[i][0], cz + SAMPLES[i][1], bottom, height);
        OptionalInt picked = CaveSurvey.pick(columns, bottom, this.depth.minY(), top, this.clearance, this.seekCaves, context.random().nextLong());
        if (picked.isEmpty()) return Optional.empty();
        int floorY = picked.getAsInt();

        var biome = context.biomeResolver().getNoiseBiome(QuartPos.fromBlock(cx), QuartPos.fromBlock(floorY + 1), QuartPos.fromBlock(cz));
        if (biome.is(Biomes.DEEP_DARK) || !context.validBiome().test(biome)) return Optional.empty();

        // The anchor is a floor block; JigsawPlacement sets a start piece one below the position it's given.
        BlockPos start = new BlockPos(cx, floorY + 1, cz);
        Optional<GenerationStub> stub = JigsawPlacement.addPieces(context, this.startPool, Optional.of(ANCHOR), this.size, start, false,
                Optional.empty(), this.maxDistance, PoolAliasLookup.EMPTY, JigsawStructure.DEFAULT_DIMENSION_PADDING,
                LiquidSettings.IGNORE_WATERLOGGING);
        if (stub.isEmpty()) return Optional.empty();
        List<StructurePiece> pieces = stub.get().getPiecesBuilder().build().pieces();
        List<StructurePiece> kept = this.buried(context, pieces);
        if (kept == null) return Optional.empty();
        return Optional.of(new GenerationStub(stub.get().position(), (StructurePiecesBuilder builder) -> kept.forEach(builder::addPiece)));
    }

    /** One column of the world's noise between {@code bottom} and {@code bottom + height}, as {@link CaveSurvey} cell kinds. */
    private static byte[] column(GenerationContext c, int x, int z, int bottom, int height) {
        NoiseColumn noise = c.chunkGenerator().getBaseColumn(x, z, c.heightAccessor(), c.randomState());
        byte[] out = new byte[height];
        for (int i = 0; i < height; i++) {
            BlockState state = noise.getBlock(bottom + i);
            if (state.isAir()) out[i] = CaveSurvey.OPEN;
            else if (!state.getFluidState().isEmpty()) out[i] = CaveSurvey.FLUID;
            else out[i] = CaveSurvey.ROCK;
        }
        return out;
    }

    /**
     * The pieces that stay under enough ground, or null if a piece the delve can't do without would show (or the
     * required piece never fitted).
     */
    private List<StructurePiece> buried(GenerationContext c, List<StructurePiece> pieces) {
        List<StructurePiece> out = new ArrayList<>(pieces.size());
        boolean found = this.require.isEmpty();
        for (int i = 0; i < pieces.size(); i++) {
            StructurePiece piece = pieces.get(i);
            boolean required = this.required(piece);
            found |= required;
            if (this.covered(c, piece.getBoundingBox()) && piece.getBoundingBox().minY() >= FLOOR_LIMIT) { out.add(piece); continue; }
            boolean leaf = piece instanceof PoolElementStructurePiece p && p.getJunctions().size() <= 1;
            if (i == 0 || !leaf || required) return null;
        }
        return found ? out : null;
    }

    private boolean required(StructurePiece piece) {
        return this.require.isPresent() && piece instanceof PoolElementStructurePiece p && p.getElement() instanceof SinglePoolElement single
                && single.getTemplateLocation().equals(this.require.get());
    }

    private boolean covered(GenerationContext c, BoundingBox box) {
        for (int x : axis(box.minX(), box.maxX())) for (int z : axis(box.minZ(), box.maxZ())) {
            if (ground(c, x, z) - box.maxY() < this.cover) return false;
        }
        return true;
    }

    private static int[] axis(int min, int max) {
        int span = max - min, n = Math.max(2, Math.min(4, span / 8 + 1));
        int[] values = new int[n];
        for (int i = 0; i < n; i++) values[i] = min + span * i / (n - 1);
        return Arrays.stream(values).distinct().toArray();
    }
}
