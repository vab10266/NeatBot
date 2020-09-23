import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer, Human
from sc2.constants import *
from sc2.unit_command import UnitCommand
import random

class GenProtBot(sc2.BotAI):
    def __init__(self, bot_id, main_net):
        self.id = bot_id
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50
        self.main_net = main_net
        self.last_chosen = 0
        self.base_attacked = False
        self.funcs = [self.build_econ(), self.build_army(), self.attack(), self.defend(), self.research(), self.expand_supply()]
        self.upgrades = {'gw':0, 'gd':0, 's':0, 'aw':0, 'ad':0}


    async def build_econ(self):
        #build probes
        if (len(self.units(NEXUS)) * 16) > len(self.units(PROBE)) and len(self.units(PROBE)) < self.MAX_WORKERS:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        #build assimilators
        for nexus in self.units(NEXUS).ready:
            vespenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vespene in vespenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                    worker = self.select_build_worker(vespene.position)
                    if worker is None:
                        break
                    await self.do(worker.build(ASSIMILATOR, vespene))
        #build nexus
        if self.units(NEXUS).amount < (self.iteration / self.ITERATIONS_PER_MINUTE) and self.can_afford(NEXUS):
            await self.expand_now()
    async def build_army(self):
        #buildings
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)

            elif len(self.units(GATEWAY)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    if (len(self.units(GATEWAY).ready.noqueue) == 0 or len(self.units(GATEWAY)) == 0):
                        await self.build(GATEWAY, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        if (len(self.units(STARGATE).ready.noqueue) == 0 or len(self.units(STARGATE)) == 0):
                            await self.build(STARGATE, near=pylon)
        en_start = self.enemy_start_locations[0]
        clo_nex = self.units(NEXUS).closest_to(en_start).position

        for gate in self.units(GATEWAY):
            await self.do(UnitCommand(RALLY_BUILDING, gate, clo_nex))
        #units
        for gw in self.units(GATEWAY).ready.noqueue:
            if not self.units(STALKER).amount > self.units(VOIDRAY).amount + 5:
                if self.can_afford(STALKER) and self.supply_left > 0:
                    await self.do(gw.train(STALKER))

        for sg in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(sg.train(VOIDRAY))
    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]
    async def attack(self):
        en_start = self.enemy_start_locations[0]
        clo_nex = self.units(NEXUS).closest_to(en_start).position

        aggressive_units = (STALKER, VOIDRAY)
        for UNIT in aggressive_units:
            for s in self.units(UNIT).idle:
                await self.do(s.attack(self.find_target(self.state)))
    async def defend(self):
        aggressive_units = (STALKER, VOIDRAY)
        for UNIT in aggressive_units:
            if len(self.known_enemy_units) > 0:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))
            else:
                for s in self.units(UNIT).idle:
                    await self.do(s.move(clo_nex))
    async def research(self):
        #need forge
        if len(self.units(FORGE)) == 0 and not self.already_pending(FORGE) and self.can_afford(FORGE):
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    await self.build(FORGE, near=nexuses.first)
        #shields and ground 1
        elif (self.upgrades['s'] == 0 or self.upgrades['gw'] == 0 or self.upgrades['gd'] == 0) and self.units(FORGE).ready.exists:
            if self.upgrades['s'] == 0 and self.can_afford(PROTOSSSHIELDSLEVEL1):
                self.units(FORGE).research(PROTOSSSHIELDSLEVEL1)
                self.upgrades['s'] = 1
            elif self.upgrades['gw'] == 0 and self.can_afford(PROTOSSGROUNDWEAPONSLEVEL1):
                self.units(FORGE).research(PROTOSSGROUNDWEAPONSLEVEL1)
                self.upgrades['gw'] = 1
            elif self.upgrades['gd'] == 0 and self.can_afford(PROTOSSGROUNDARMORSLEVEL1):
                self.units(FORGE).research(PROTOSSGROUNDARMORSLEVEL1)
                self.upgrades['gd'] = 1
        #need cyber core
        elif len(self.units(CYBERNETICSCORE)) == 0 and len(self.units(GATEWAY).ready) != 0 and not self.already_pending(CYBERNETICSCORE) and self.can_afford(CYBERNETICSCORE):
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    await self.build(CYBERNETICSCORE, near=nexuses.first)
        #air 1
        elif (self.upgrades['aw'] == 0 or self.upgrades['ad'] == 0) and self.units(CYBERNETICSCORE).ready.exists:
            if self.upgrades['aw'] == 0 and self.can_afford(PROTOSSAIRWEAPONSLEVEL1):
                self.units(FORGE).research(PROTOSSAIRWEAPONSLEVEL1)
                self.upgrades['aw'] = 1
            elif self.upgrades['ad'] == 0 and self.can_afford(PROTOSSAIRARMORSLEVEL1):
                self.units(FORGE).research(PROTOSSAIRARMORSLEVEL1)
                self.upgrades['ad'] = 1
        #need fleet beacon
        elif len(self.units(FLEETBEACON)) == 0 and len(self.units(STARGATE).ready) != 0 and not self.already_pending(FLEETBEACON) and self.can_afford(FLEETBEACON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                await self.build(FLEETBEACON, near=nexuses.first)
        #air 2
        elif (self.upgrades['aw'] == 1 or self.upgrades['ad'] == 1) and self.units(CYBERNETICSCORE).ready.exists and self.units(FLEETBEACON).ready.exists:
            if self.upgrades['aw'] == 1 and self.can_afford(PROTOSSAIRWEAPONSLEVEL2):
                self.units(FORGE).research(PROTOSSAIRWEAPONSLEVEL2)
                self.upgrades['aw'] = 2
            elif self.upgrades['ad'] == 1 and self.can_afford(PROTOSSAIRARMORSLEVEL2):
                self.units(FORGE).research(PROTOSSAIRARMORSLEVEL2)
                self.upgrades['ad'] = 2
        #need twilight council
        elif len(self.units(TWILIGHTCOUNCIL)) == 0 and len(self.units(CYBERNETICSCORE).ready) != 0 and not self.already_pending(TWILIGHTCOUNCIL) and self.can_afford(TWILIGHTCOUNCIL):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                await self.build(TWILIGHTCOUNCIL, near=nexuses.first)
        #shields and ground 2
        elif (self.upgrades['s'] == 1 or self.upgrades['gw'] == 1 or self.upgrades['gd'] == 1) and self.units(FORGE).ready.exists and self.units(TWILIGHTCOUNCIL).ready.exists:
            if self.upgrades['s'] == 1 and self.can_afford(PROTOSSSHIELDSLEVEL2):
                self.units(FORGE).research(PROTOSSSHIELDSLEVEL2)
                self.upgrades['s'] = 2
            elif self.upgrades['gw'] == 1 and self.can_afford(PROTOSSGROUNDWEAPONSLEVEL2):
                self.units(FORGE).research(PROTOSSGROUNDWEAPONSLEVEL2)
                self.upgrades['gw'] = 2
            elif self.upgrades['gd'] == 1 and self.can_afford(PROTOSSGROUNDARMORSLEVEL2):
                self.units(FORGE).research(PROTOSSGROUNDARMORSLEVEL2)
                self.upgrades['gd'] = 2
        #air 3
        elif (self.upgrades['aw'] == 2 or self.upgrades['ad'] == 2) and self.units(CYBERNETICSCORE).ready.exists and self.units(FLEETBEACON).ready.exists:
            if self.upgrades['aw'] == 2:
                self.units(FORGE).research(PROTOSSAIRWEAPONSLEVEL3)
                self.upgrades['aw'] = 3
            elif self.upgrades['ad'] == 2:
                self.units(FORGE).research(PROTOSSAIRARMORSLEVEL3)
                self.upgrades['ad'] = 3
        #shields and ground 3
        elif (self.upgrades['s'] == 2 or self.upgrades['gw'] == 2 or self.upgrades['gd'] == 2) and self.units(FORGE).ready.exists and self.units(TWILIGHTCOUNCIL).ready.exists:
            if self.upgrades['s'] == 2 and self.can_afford(PROTOSSSHIELDSLEVEL3):
                self.units(FORGE).research(PROTOSSSHIELDSLEVEL3)
                self.upgrades['s'] = 3
            elif self.upgrades['gw'] == 2 and self.can_afford(PROTOSSGROUNDWEAPONSLEVEL3):
                self.units(FORGE).research(PROTOSSGROUNDWEAPONSLEVEL3)
                self.upgrades['gw'] = 3
            elif self.upgrades['gd'] == 2 and self.can_afford(PROTOSSGROUNDARMORSLEVEL3):
                self.units(FORGE).research(PROTOSSGROUNDARMORSLEVEL3)
                self.upgrades['gd'] = 3
    async def expand_supply(self):
        if not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

    async def on_step(self, iteration):
        self.iteration = iteration
        self.score = self.state.score
        await self.distribute_workers()
        #set base_attacked
        self.base_attacked = False
        en_units = self.known_enemy_units
        if len(en_units) > 0:
            for nex in self.units(NEXUS):
                if en_units.closest_distance_to(nex.position) <= nex.radar_range:
                    self.base_attacked = True
                    break
        #run nn
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
        #choice
        await self.funcs[self.last_chosen]



