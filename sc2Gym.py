import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer, Human
from sc2.constants import *
from sc2.unit_command import UnitCommand
import random
import neat
from GenProtBot import GenProtBot

class sc2Gym():
    def __init__(self, genomes, config):
        self.genomes = genomes
        self.config = config
    def get_bots(self):
        bots = {}
        for genome_id, genome in self.genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, self.config)
            bot = GenProtBot(genome_id, net)
            bots[genome_id] = bot
        return bots
    def spending_game(self):
        bot_pop = self.get_bots()
        tested_bots = {}
        scores = {}
        while bot_pop:
            opp_ids = random.sample(list(bot_pop), 2)
            for bot_id in opp_ids:
                tested_bots[bot_id] = bot_pop.pop(bot_id)
            bot_a = tested_bots[opp_ids[0]]
            bot_b = tested_bots[opp_ids[1]]
            sc2.run_game(sc2.maps.get("ProximaStationLE"), [
                Bot(Race.Protoss, bot_a),
                Bot(Race.Protoss, bot_b),
            ], realtime=False, game_time_limit=3000)
            a_score = bot_a.score
            b_score = bot_b.score
            #print('---------',self.genomes)
            '''
            for genome_id, genome in self.genomes:
                if genome_id == opp_ids[0]:
                    genome.fitness = a_score.spent_minerals + a_score.spent_vespene + a_score.killed_minerals_army + a_score.killed_minerals_economy + a_score.killed_vespene_army + a_score.killed_vespene_economy
                    print(genome.fitness)
                if genome_id == opp_ids[1]:
                    genome.fitness = b_score.spent_minerals + b_score.spent_vespene + b_score.killed_minerals_army + b_score.killed_minerals_economy + b_score.killed_vespene_army + b_score.killed_vespene_economy
                    print(genome.fitness)
            '''
            scores[opp_ids[0]] = a_score.spent_minerals + a_score.spent_vespene + a_score.killed_minerals_army + a_score.killed_minerals_economy + a_score.killed_vespene_army + a_score.killed_vespene_economy
            scores[opp_ids[1]] = b_score.spent_minerals + b_score.spent_vespene + b_score.killed_minerals_army + b_score.killed_minerals_economy + b_score.killed_vespene_army + b_score.killed_vespene_economy
            print('SCORES', scores[opp_ids[0]], scores[opp_ids[1]])
        return scores


