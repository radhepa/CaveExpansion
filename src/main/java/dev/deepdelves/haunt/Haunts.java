package dev.deepdelves.haunt;

import java.util.Optional;

import dev.deepdelves.block.HauntBlock.Kind;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.skeleton.AbstractSkeleton;
import net.minecraft.world.entity.monster.cubemob.MagmaCube;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;

/**
 * The guardians of the abandoned delves. A delve's template marks where they wait with an invisible haunt
 * block; the first time a player comes within {@link #RANGE} blocks the mark is gone and they rise:
 * <ul>
 *   <li>{@code restless_miner}: two of the buried shift. Not-So-Vanilla Mobs' Lost Miners when that mod is
 *       installed, else zombies in miners' copper helmets with picks.</li>
 *   <li>{@code drowned}: three drowned, one with a trident.</li>
 *   <li>{@code crypt_keeper}: the Ossuary's keeper (NSV's Gravewarden when installed, else a tall armoured
 *       skeleton with a sword and twice a skeleton's health) and two skeletons.</li>
 *   <li>{@code cinder}: two of NSV's Soulpyres when installed, else two magma cubes.</li>
 * </ul>
 * They don't despawn: they are the delve's, until someone deals with them.
 */
public final class Haunts {
    private Haunts() {}

    public static final int RANGE = 14;

    public static void tick(ServerLevel level, BlockPos pos, Kind kind) {
        if (Math.floorMod(level.getGameTime() + pos.asLong(), 10) != 0) return;
        Player p = level.getNearestPlayer(pos.getX() + .5, pos.getY() + .5, pos.getZ() + .5, RANGE, e -> !e.isSpectator());
        if (p == null) return;
        level.setBlock(pos, Blocks.AIR.defaultBlockState(), 3);
        rise(level, pos, kind);
        if (p instanceof ServerPlayer sp) sp.sendOverlayMessage(Component.translatable("haunt.deepdelves." + kind.getSerializedName()));
    }

    /** Puts a haunt's guardians at {@code pos}; returns how many rose. */
    public static int rise(ServerLevel level, BlockPos pos, Kind kind) {
        int risen = 0;
        switch (kind) {
            case RESTLESS_MINER -> {
                for (int i = 0; i < 2; i++) {
                    Mob m = modded(level, "nsvmobs:lost_miner").orElseGet(() -> miner(level));
                    if (spawn(level, m, pos, i)) risen++;
                }
                level.playSound(null, pos, SoundEvents.ZOMBIE_AMBIENT, SoundSource.HOSTILE, 1.2F, .6F);
                level.sendParticles(ParticleTypes.LARGE_SMOKE, pos.getX() + .5, pos.getY() + 1, pos.getZ() + .5, 30, .8, .8, .8, .02);
            }
            case DROWNED -> {
                for (int i = 0; i < 3; i++) {
                    Mob m = EntityTypes.DROWNED.create(level, EntitySpawnReason.STRUCTURE);
                    if (m == null) continue;
                    if (spawn(level, m, pos, i)) {
                        risen++;
                        if (i == 0) equip(m, EquipmentSlot.MAINHAND, new ItemStack(Items.TRIDENT), .1F);
                        if (i == 1) equip(m, EquipmentSlot.OFFHAND, new ItemStack(Items.NAUTILUS_SHELL), 1F);
                    }
                }
                level.playSound(null, pos, SoundEvents.DROWNED_AMBIENT_WATER, SoundSource.HOSTILE, 1.2F, .7F);
                level.sendParticles(ParticleTypes.BUBBLE_COLUMN_UP, pos.getX() + .5, pos.getY() + .5, pos.getZ() + .5, 40, 1, .5, 1, .1);
            }
            case CRYPT_KEEPER -> {
                Mob keeper = modded(level, "nsvmobs:gravewarden").orElseGet(() -> keeper(level));
                if (keeper != null) {
                    keeper.setCustomName(Component.translatable("entity.deepdelves.crypt_keeper"));
                    if (spawn(level, keeper, pos, 0)) risen++;
                }
                for (int i = 1; i < 3; i++) {
                    Mob m = EntityTypes.SKELETON.create(level, EntitySpawnReason.STRUCTURE);
                    if (m != null && spawn(level, m, pos, i)) risen++;
                }
                level.playSound(null, pos, SoundEvents.SKELETON_AMBIENT, SoundSource.HOSTILE, 1.4F, .5F);
                level.sendParticles(ParticleTypes.SOUL, pos.getX() + .5, pos.getY() + 1, pos.getZ() + .5, 30, 1, 1, 1, .02);
            }
            case CINDER -> {
                for (int i = 0; i < 2; i++) {
                    Mob m = modded(level, "nsvmobs:soulpyre").orElseGet(() -> {
                        MagmaCube cube = EntityTypes.MAGMA_CUBE.create(level, EntitySpawnReason.STRUCTURE);
                        if (cube != null) cube.setSize(2, true);
                        return cube;
                    });
                    if (spawn(level, m, pos, i)) risen++;
                }
                level.playSound(null, pos, SoundEvents.BLAZE_AMBIENT, SoundSource.HOSTILE, 1.2F, .6F);
                level.sendParticles(ParticleTypes.FLAME, pos.getX() + .5, pos.getY() + 1, pos.getZ() + .5, 40, 1, .8, 1, .03);
            }
        }
        return risen;
    }

    /** Another mod's mob by id, when that mod is installed. */
    static Optional<Mob> modded(ServerLevel level, String id) {
        return BuiltInRegistries.ENTITY_TYPE.getOptional(Identifier.parse(id))
                .map(type -> type.create(level, EntitySpawnReason.STRUCTURE))
                .filter(e -> e instanceof Mob).map(e -> (Mob) e);
    }

    /** A zombie that was a Guild miner: copper helmet, pick in hand. */
    private static Mob miner(ServerLevel level) {
        Mob z = EntityTypes.ZOMBIE.create(level, EntitySpawnReason.STRUCTURE);
        if (z == null) return null;
        z.setCustomName(Component.translatable("entity.deepdelves.restless_miner"));
        return z;
    }

    private static Mob keeper(ServerLevel level) {
        return EntityTypes.SKELETON.create(level, EntitySpawnReason.STRUCTURE);
    }

    private static boolean spawn(ServerLevel level, Mob m, BlockPos pos, int index) {
        if (m == null) return false;
        int[][] offsets = {{0, 0}, {1, 1}, {-1, 1}, {1, -1}, {-1, -1}};
        int[] o = offsets[index % offsets.length];
        m.snapTo(pos.getX() + .5 + o[0], pos.getY(), pos.getZ() + .5 + o[1], level.getRandom().nextFloat() * 360F, 0F);
        if (!level.noCollision(m)) m.snapTo(pos.getX() + .5, pos.getY(), pos.getZ() + .5, m.getYRot(), 0F);
        m.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), EntitySpawnReason.STRUCTURE, null);
        m.setPersistenceRequired();
        dress(m);
        return level.addFreshEntity(m);
    }

    /** Gear that marks who they were (after finalizeSpawn, which hands out its own). */
    private static void dress(Mob m) {
        String name = m.getCustomName() == null ? "" : m.getCustomName().getString();
        if (m.getType() == EntityTypes.ZOMBIE && m.hasCustomName()) {
            equip(m, EquipmentSlot.HEAD, new ItemStack(Items.COPPER_HELMET), .05F);
            equip(m, EquipmentSlot.MAINHAND, new ItemStack(m.getRandom().nextBoolean() ? Items.IRON_PICKAXE : Items.STONE_PICKAXE), .05F);
        }
        if (m.getType() == EntityTypes.SKELETON && m.hasCustomName() && !name.isEmpty()) {
            equip(m, EquipmentSlot.HEAD, new ItemStack(Items.GOLDEN_HELMET), .1F);
            equip(m, EquipmentSlot.CHEST, new ItemStack(Items.CHAINMAIL_CHESTPLATE), .1F);
            equip(m, EquipmentSlot.LEGS, new ItemStack(Items.CHAINMAIL_LEGGINGS), .1F);
            equip(m, EquipmentSlot.MAINHAND, new ItemStack(Items.IRON_SWORD), .1F);
            var health = m.getAttribute(Attributes.MAX_HEALTH);
            if (health != null) { health.setBaseValue(40.0); m.setHealth(40F); }
            var scale = m.getAttribute(Attributes.SCALE);
            if (scale != null) scale.setBaseValue(1.2);
            if (m instanceof AbstractSkeleton s) s.reassessWeaponGoal();
        }
    }

    private static void equip(Mob m, EquipmentSlot slot, ItemStack stack, float dropChance) {
        m.setItemSlot(slot, stack);
        m.setDropChance(slot, dropChance);
    }
}
