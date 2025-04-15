from dribble.memory import offsets


class ReplacePlayer(object):
    """
    Replace one player with another within the game memory.

    :param game: The game object containing memory and offsets.
    :param old_player: The player object to be replaced.
    :param new_player: The player object to replace with.
    :return: None
    """

    def __init__(self, game, old_player, new_player):
        self.game = game
        self.old_player = old_player
        self.new_player = new_player

    def run(self):
        if self.new_player == True:
            new_player_data = self.game.memory.read_bytes(
                self.new_player.address, offsets["Base"]["Player Offset Length"]
            )
            self.game.memory.write_bytes(
                self.old_player.address,
                new_player_data,
                offsets["Base"]["Player Offset Length"],
            )
