package dev.deepdelves.worldgen;

import java.util.List;
import java.util.Set;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureProcessor;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate.StructureBlockInfo;

/**
 * Natural blocks in a delve (the rock lining of a room, ore seams, moss, calcite...) only replace solid ground:
 * where the world is already open (a cave, an aquifer, a lava pocket) they are left out, so a delve that breaks
 * into a cave opens onto it instead of walling it up with floating stone. Built blocks and carved air are not
 * touched by this processor.
 */
public final class NaturalProcessor implements StructureProcessor {
    public static final MapCodec<NaturalProcessor> CODEC = BuiltInRegistries.BLOCK.byNameCodec().listOf()
            .fieldOf("blocks").xmap(NaturalProcessor::new, p -> List.copyOf(p.blocks));

    private final Set<Block> blocks;

    public NaturalProcessor(List<Block> blocks) {
        this.blocks = Set.copyOf(blocks);
    }

    @Override
    public StructureBlockInfo processBlock(LevelReader level, BlockPos targetPosition, BlockPos referencePos, BlockPos templateRelativePos,
                                                     StructureBlockInfo processed, StructurePlaceSettings settings) {
        if (!this.blocks.contains(processed.state().getBlock())) return processed;
        return solid(level.getBlockState(processed.pos())) ? processed : null;
    }

    /** Ground a natural block may replace: anything but air, fluids and soft plants. */
    static boolean solid(BlockState state) {
        return !state.isAir() && state.getFluidState().isEmpty() && !state.canBeReplaced();
    }

    @Override
    public MapCodec<? extends StructureProcessor> codec() {
        return CODEC;
    }
}
