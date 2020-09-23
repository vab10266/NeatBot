import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer, Human
from sc2.constants import *
from sc2.unit_command import UnitCommand
import random

class GenZergBot(sc2.BotAI):
    def __init__(self, main_net):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50
        self.main_net = main_net
        self.last_chosen = 0
        self.base_attacked = False
        self.funcs = {0:self.build_econ(), 1:self.build_army(), 2:self.attack(), 3:self.defend(), 4:self.research(), 5:self.expand_supply()}
    async def build_econ(self):
    async def build_army(self):
    async def attack(self):
    async def defend(self):
    async def research(self):
    async def expand_supply(self):

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        #TODO set base_attacked
        input_arr = (self.time, self.minerals, self.vespene, len(self.workers),
            self.supply_used-len(self.workers), self.supply_left,
            self.last_chosen, self.base_attacked)
        output_arr = net.activate(input_arr)
        #softmax
        total = sum(output_arr)
        for i in output_arr:
            output_arr[i] /= total
        #argmax
        f = lambda i: output_arr[i]
        self.last_chosen = max(range(len(output_arr)), key=f)
        await self.funcs[self.last_chosen]



