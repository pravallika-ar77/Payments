import random
def uniqueid():
    seed = random.getrandbits(32)
    while True:
       yield seed
       seed += 1


#ids = list(itertools.islice(unique_sequence, 1000))