from os import getcwd
from argparse import ArgumentParser, ArgumentTypeError


# ======================== ARGUMENT TYPE CASTING ==============================

def str2bool(arg):
     """ Convert <arg> to boolean. """
     if arg.lower() in ('yes', 'true', 't', 'y', '1'):
          return True
     elif arg.lower() in ('no', 'false', 'f', 'n', '0'):
          return False
     else:
          raise ArgumentTypeError('Boolean value expected.')


# ======================== ARGUMENT PARSING ===================================


class RunArguments(ArgumentParser):
     """ Argument handler for run scripts. """

     def __init__(self, **kwargs):
          super().__init__(**kwargs)
          self.add_arguments()
          self.parse()

     def __getitem__(self, key):
          """ Returns <key> argument value. """
          return self.args[key]

     def add_arguments(self):
          """ Add arguments. """

          # add position argument for path
          self.add_argument(
               'path',
               nargs='?',
               default=getcwd())

          # add keyword argument for saving history
          self.add_argument(
               '-s', '--save_history',
               help='Save growth history.',
               type=str2bool,
               default=False,
               required=False)

     def parse(self):
          """ Parse arguments. """
          self.args = vars(self.parse_args())


class SweepArguments(RunArguments):
     """ Argument handler for parameter sweeps. """

     def add_arguments(self):
          """ Add arguments. """

          super().add_arguments()

          # add keyword argument for sweep density
          self.add_argument('-d', '--density',
                              help='Parameter range density.',
                              type=int,
                              default=6,
                              required=False)

          # add keyword argument for sweep density
          self.add_argument('-b', '--batch_size',
                              help='Replicates per parameter set.',
                              type=int,
                              default=1,
                              required=False)

          # add keyword argument for sweep density
          self.add_argument('-dr', '--division_rate',
                              help='Division rate.',
                              type=float,
                              default=0.1,
                              required=False)

          # add keyword argument for recombination duration
          self.add_argument('-rd', '--recombination_duration',
                              help='Duration of recombination period.',
                              type=int,
                              default=4,
                              required=False)

          # add keyword argument for sweep density
          self.add_argument('-p', '--population',
                              help='Final population.',
                              type=int,
                              default=11,
                              required=False)

          # add keyword argument for estimated run time
          self.add_argument('-w', '--walltime',
                              help='Estimated run time.',
                              type=int,
                              default=10,
                              required=False)

          # add keyword argument for number of cores
          self.add_argument('-c', '--cores',
                              help='Number of cores.',
                              type=int,
                              default=1,
                              required=False)

          # add keyword argument for memory usage
          self.add_argument('-m', '--memory',
                              help='Memory usage.',
                              type=int,
                              default=4,
                              required=False)

          # add keyword argument for project allocation
          self.add_argument('-A', '--allocation',
                              help='Project allocation.',
                              type=str,
                              default='p30653',
                              required=False)
