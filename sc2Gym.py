import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer, Human
from sc2.constants import *
from sc2.unit_command import UnitCommand
import random
import neat
import GenProtBot

class sc2Gym():
    def __init__(self, genomes, config):
        self.genomes = genomes
        self.config = config
    def get_bots():
        bots = {}
        for genome_id, genome in self.genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            bot = GenProtBot(genome_id, net)
            bots[genome_id] = bot
        return bots
    def spendingGame():
        bot_pop = get_bots()
        tested_bots = {}
        while bot_pop:
            opp_ids = random.sample(list(bot_pop), 2)
            for bot_id in opp_ids:
                tested_bots[bot_id] = bot_pop.pop(bot_id)
            bot_a = tested_bots[opp_ids[0]]
            bot_b = tested_bots[opp_ids[1]]
            sc2.run_game(sc2.maps.get("ProximaStationLE"), [
                Bot(Race.Protoss, bot_a),
                Bot(Race.Protoss, bot_b),
            ], realtime=False)
            a_score = bot_a.score
            b_score = bot_b.score
            self.genomes[opp_ids[0]].fitness = a_score.spent_minerals() + a_score.spent_vespene() + a_score.killed_minerals_army() + a_score.killed_minerals_economy()
            self.genomes[opp_ids[1]].fitness = b_score.spent_minerals() + b_score.spent_vespene() + b_score.killed_minerals_army() + b_score.killed_minerals_economy()
        return self.genomes


