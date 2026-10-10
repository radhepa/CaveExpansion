package dev.caveexpansion.block;

import dev.caveexpansion.haunt.Haunts;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jspecify.annotations.Nullable;

/**
 * An invisible mark in an abandoned delve: where its guardians wait. The first time a player comes within
 * {@link Haunts#RANGE} blocks they rise there (see {@link Haunts}) and the mark is gone.
 */
public class HauntBlock extends BaseEntityBlock {
    public enum Kind implements StringRepresentable {
        RESTLESS_MINER("restless_miner"), DROWNED("drowned"), CRYPT_KEEPER("crypt_keeper"), CINDER("cinder");
        private final String id;
        Kind(String id) { this.id = id; }
        @Override public String getSerializedName() { return this.id; }
    }

    public static final EnumProperty<Kind> KIND = EnumProperty.create("kind", Kind.class);

    public HauntBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(KIND, Kind.RESTLESS_MINER));
    }

    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) { builder.add(KIND); }
    @Override protected RenderShape getRenderShape(BlockState state) { return RenderShape.INVISIBLE; }
    @Override protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return Shapes.empty(); }
    @Override protected boolean propagatesSkylightDown(BlockState state) { return true; }

    @Override
    public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new HauntBlockEntity(pos, state); }

    @Override
    public <T extends BlockEntity> @Nullable BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        if (level.isClientSide() || type != DelveBlocks.HAUNT_ENTITY) return null;
        return (l, p, s, be) -> Haunts.tick((ServerLevel) l, p, s.getValue(KIND));
    }
}
