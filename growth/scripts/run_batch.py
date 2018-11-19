from time import time
from growth.sweep.arguments import RunArguments
from growth.sweep.simulation import GrowthSimulation


# ======================== PARSE SCRIPT ARGUMENTS =============================

args = RunArguments(description='Growth simulation arguments.')
path = args['path']
save_history = args['save_history']


# ============================= RUN SCRIPT ====================================


start_time = time()

# run each simulation in batch file
with open(path, 'r') as batch_file:

    # run each simulation
    for path in batch_file.readlines():

        path = path.strip()

        # load simulation
        simulation = GrowthSimulation.load(path)

        # run simulation and comparison
        simulation.run()

        # save simulation
        simulation.save(path, save_history=save_history)


# print runtime to standard out
runtime = time() - start_time
print('\nSIMULATION COMPLETED IN {:0.2f}.\n'.format(runtime))