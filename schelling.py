import matplotlib.pyplot as plt
import itertools
import random
import copy


class Schelling:

    def __init__(self, width, height, empty_ratio, similarity_threshold, n_iterations, races=2):
        self.width = width
        self.height = height
        if 0 < races <= 4:
            self.races = races
        self.empty_ratio = empty_ratio
        self.similarity_threshold = similarity_threshold
        self.n_iterations = n_iterations

    # metoda tworząca i przygotowująca obszar symulacji (definicja komórek i automatów)
    def __populate(self):
        self.empty_houses = []
        self.agents = {}

        self.all_houses = list(itertools.product(range(self.width), range(self.height)))
        random.shuffle(self.all_houses)

        self.n_empty = int(self.empty_ratio * len(self.all_houses))

        self.empty_houses = self.all_houses[:self.n_empty]
        self.remaining_houses = self.all_houses[self.n_empty:]

        houses_by_race = [self.remaining_houses[i::self.races] for i in range(self.races)]
        for i in range(self.races):
            self.agents = dict(
                self.agents.items() |
                dict(zip(houses_by_race[i], [i + 1] * len(houses_by_race[i]))).items()
            )

    def __evaluate(self, x, y):
        race = self.agents[(x, y)]
        evaluation = {'similar': 0, 'different': 0}

        if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
            if self.agents[(x - 1, y - 1)] == race:
                evaluation['similar'] += 1
            else:
                evaluation['different'] += 1
        if y > 0 and (x, y - 1) not in self.empty_houses:
            if self.agents[(x, y - 1)] == race:
                evaluation['similar'] += 1
            else:
                evaluation['different'] += 1
        if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
            if self.agents[(x + 1, y - 1)] == race:
                evaluation['similar'] += 1
            else:
                evaluation['different'] += 1
        if x > 0 and (x - 1, y) not in self.empty_houses:
            if self.agents[(x - 1, y)] == race:
                evaluation['similar'] += 1
            else:
                evaluation['different'] += 1
        if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
            if self.agents[(x + 1, y)] == race:
                evaluation['similar'] += 1
            else:
                evaluation['different'] += 1
        if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
            if self.agents[(x - 1, y + 1)] == race:
                evaluation['similar'] += 1
            else:
                evaluation['different'] += 1
        if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
            if self.agents[(x, y + 1)] == race:
                evaluation['similar'] += 1
            else:
                evaluation['different'] += 1
        if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
            if self.agents[(x + 1, y + 1)] == race:
                evaluation['similar'] += 1
            else:
                evaluation['different'] += 1
        return evaluation

    # metoda określająca bierzący stan automatu komórkowego
    def __is_satisfied(self, x, y):

        evaluation = self.__evaluate(x, y)
        if (evaluation['similar'] + evaluation['different']) == 0:
            return False
        else:
            return float(evaluation['similar']) / (
                    evaluation['similar'] + evaluation['different']) < self.similarity_threshold

    # metoda iterująca symulację
    def __update(self):
        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            moves = 0
            for agent in self.old_agents:
                if self.__is_satisfied(agent[0], agent[1]):
                    self.__move_to_empty(agent[0], agent[1])
                    moves += 1
            print('Iteracja: %d. Liczba przemieszczeń: %d' % (i + 1, moves))
            if moves == 0:
                break

    # metoda relokująca automat do losowej wolnej komórki
    def __move_to_empty(self, x, y):
        agent_race = self.agents[(x, y)]
        empty_house = random.choice(self.empty_houses)
        self.agents[empty_house] = agent_race
        del self.agents[(x, y)]
        self.empty_houses.remove(empty_house)
        self.empty_houses.append((x, y))

    def __plot(self, initial=False):

        fig, ax = plt.subplots()
        agent_colors = {1: 'b', 2: 'r', 3: 'g', 4: 'c'}
        for agent in self.agents:
            ax.scatter(agent[0] + 0.5, agent[1] + 0.5, color=agent_colors[self.agents[agent]], alpha=.6)
        label_final = 'Model segregacji rasowej Schellinga: %d rasy, próg satysfakcji: %d%%' \
                      % (self.races, self.similarity_threshold * 100)
        label_init = 'Model segregacji rasowej Schellinga: %d rasy: stan początkowy' % self.races
        title = label_init if initial else label_final
        file_init = 'schelling_%d_%d_initial.png' % (self.races, self.similarity_threshold * 100)
        file_final = 'schelling_%d_%d_final.png' % (self.races, self.similarity_threshold * 100)
        file_name = file_init if initial else file_final
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig(file_name)

    # metoda przeprowadzająca kalkulacje
    def __calculate_similarity(self):
        similarity = []
        for agent in self.agents:
            evaluation = self.__evaluate(agent[0], agent[1])
            similar = evaluation['similar']
            different = evaluation['different']

            try:
                similarity.append(float(similar) / (similar + different))
            except (ValueError, IndexError, ZeroDivisionError, Exception):
                similarity.append(1)
        return sum(similarity) / len(similarity)

    # fasada przebiegu symulacji
    def perform_simulation(self):
        self.__populate()
        self.__plot(initial=True)
        self.__update()
        self.__plot()

    # statyczna metoda kalkulacji
    @staticmethod
    def perform_calculations():
        similarity_threshold_ratio = {}
        for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
            schelling = Schelling(50, 50, 0.3, i, 500, 2)
            schelling.__populate()
            schelling.__update()
            similarity_threshold_ratio[i] = schelling.__calculate_similarity()

        fig, ax = plt.subplots()
        plt.plot(similarity_threshold_ratio.keys(), similarity_threshold_ratio.values(), 'ro')
        ax.set_title('Próg zadowolenia vs. stopień segregacji', fontsize=15, fontweight='bold')
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1.1])
        ax.set_xlabel("Minimalny próg podobieństwa")
        ax.set_ylabel("Średni poziom segregacji rasowej")
        plt.savefig('schelling_segregation.png')

def main():

    schelling_1 = Schelling(50, 50, 0.3, 0.3, 500, 2)
    schelling_1.perform_simulation()

    schelling_2 = Schelling(50, 50, 0.3, 0.5, 500, 2)
    schelling_2.perform_simulation()

    schelling_3 = Schelling(50, 50, 0.3, 0.8, 500, 2)
    schelling_3.perform_simulation()

    Schelling.perform_calculations()


if __name__ == "__main__":
    main()
