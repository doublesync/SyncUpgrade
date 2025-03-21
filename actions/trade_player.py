from core import offsets

class TradePlayer(object):
    """
    Trade two players for each other within the game memory.
    
    :param player1: The first player object.
    :param player2: The second player object.
    :return: None
    """
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def run(self, game):
        player1_data = game.memory.read_bytes(self.player1.address, game.offsets["Base"]["Player Offset Length"])
        player2_data = game.memory.read_bytes(self.player2.address, game.offsets["Base"]["Player Offset Length"])
        game.memory.write_bytes(self.player1.address, player2_data, game.offsets["Base"]["Player Offset Length"])
        game.memory.write_bytes(self.player2.address, player1_data, game.offsets["Base"]["Player Offset Length"])