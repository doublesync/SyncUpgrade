from core import (
    offsets, 
    ConvertToGameValue,
    BitLengthToByteLength
)

# Write bytes to memory at a specific address
def WriteBinaryBytes(game, address, length, value):
    """
    Write bytes to memory at a specific address - only used for attributes because they are the only values that are written as bytes/binary
    while others are written as integers or strings.

    :param game: The game memory writer instance.
    :param address: The memory address to write to.
    :param length: The value to write as bits.
    :param value: The value in 0-255 (8-bit) range to write to memory.
    """
    num_bytes = BitLengthToByteLength(length)
    game.memory.write_bytes(address, value, num_bytes)