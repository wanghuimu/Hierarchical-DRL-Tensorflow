# -*- coding: utf-8 -*-
import subprocess
import itertools
import os
import utils
import pprint


class Experiment():
        
    def __init__(self, name, paralel):
        self.paralel = paralel
        self.name = name
        self._args_list = []
    
        if name == 'extensions_exp':
            base_args = {'scale'          : 5000,
                        'agent_type'      : 'dqn',
                        'mode'            : 'train',
                        'env_name'        : 'SF-v0',
                        'use_gpu'         : 0,
                        'ez'              : 1,
                        'mines_activated' : 1,
                        'double_q'        : 0,
                        'dueling'         : 0,
                        'pmemory'         : 0}
            hyperparameter_space = {'random_seeds' : list(range(5))}
            # VANILLA
            vanilla_base_args = base_args.copy()
            self.add_params_to_arg_list(vanilla_base_args, hyperparameter_space)
            # DOUBLE Q
            double_q_base_args = base_args.copy()
            double_q_base_args['double_q'] = 1
            self.add_params_to_arg_list(double_q_base_args, hyperparameter_space)
            # DUELING
            dueling_base_args = base_args.copy()
            dueling_base_args['dueling'] = 1
            self.add_params_to_arg_list(dueling_base_args, hyperparameter_space)
            # PRIORITIZE REPLAY MEMORY
            pmemory_base_args = base_args.copy()
            pmemory_base_args['pmemory'] = 1
            self.add_params_to_arg_list(pmemory_base_args, hyperparameter_space)
            # RAINBOW
            rainbow_base_args = base_args.copy()
            rainbow_base_args['double_q'] = 1
            rainbow_base_args['dueling'] = 1
            rainbow_base_args['pmemory'] = 1
            self.add_params_to_arg_list(rainbow_base_args, hyperparameter_space)
        elif name == 'action_repeat_exp':
            base_args = {'scale'          : 5000,
                        'agent_type'      : 'dqn',
                        'mode'            : 'train',
                        'env_name'        : 'SF-v0',
                        'use_gpu'         : 0,
                        'ez'              : 1,
                        'mines_activated' : 1,
                        'double_q'        : 0,
                        'dueling'         : 0,
                        'pmemory'         : 0}
            hyperparameter_space = {'random_seeds'   : list(range(1)),
                                    'action_repeats' : list(range(1, 11))}
            self.add_params_to_arg_list(base_args, hyperparameter_space)
        elif name == 'architectures_exp':
            base_args = {'scale'          : 5000,
                        'agent_type'      : 'dqn',
                        'mode'            : 'train',
                        'env_name'        : 'SF-v0',
                        'use_gpu'         : 0,
                        'ez'              : 1,
                        'mines_activated' : 1,
                        'double_q'        : 0,
                        'dueling'         : 0,
                        'pmemory'         : 0}
            architectures = [[8],
                            [64, 64],
                            [64, 64, 64, 64],
                            [512],
                            [512, 512]]
            hyperparameter_space = {'random_seeds'   : list(range(5)),
                                    'architectures'  : architectures}
            self.add_params_to_arg_list(base_args, hyperparameter_space)
            
        elif name == 'goals_exp':
            base_args = {'scale'          : 15000,
                        'agent_type'      : 'hdqn',
                        'mode'            : 'train',
                        'env_name'        : 'SF-v0',
                        'use_gpu'         : 0,
                        'ez'              : 1,
                        'mines_activated' : 1,
                        'double_q'        : 0,
                        'dueling'         : 0,
                        'pmemory'         : 0}
     
            hyperparameter_space = {'random_seeds'   : list(range(1)),
                                    'goal_groups'    : [1,2,3,4,5,6]}
            self.add_params_to_arg_list(base_args, hyperparameter_space)
            
        elif name == 'toy_problem':
            # toy_problem
            hyperparameter_space = {
                    'agent_types'             : ['dqn', 'hdqn'],
                    'random_seeds'           : list(range(10))
                    }
            base_args = {
                    'agent_type'            : 'dqn',
                    'env_name'              : 'key_mdp-v0',
                    'scale'                 : 100,    
                    'mode'                  : 'train',
                    'display_prob'          : 0.001,
                    'use_gpu'               : 0,
                    'dueling'               : 0,
                    'double_q'              : 0
            }  
        
        
    def add_params_to_arg_list(self, base_args, hyperparameter_space):
        print("Experiment %s:\n%s" % (self.name, pprint.pformat(hyperparameter_space)))
        base_args['paralel'] = self.paralel
        for args in self.get_hyperparameters_iterator(hyperparameter_space,
                                                      base_args):
            
            if 'architecture' in args:
                args['architecture'] = '-'.join([str(l) for l in args['architecture']])
            t = utils.get_timestamp()
            args['experiment_name'] = "%s_%s" % (t, self.name)
            
            self._args_list.append(args)
       
        
    def get_hyperparameters_iterator(self, hyperparameters_space, base_dict):
        lists = []
        for k, hyperparameters in hyperparameters_space.items():
            assert k[-1] == 's', '"%s" must end with "s"' % k
            param_name = k[:-1]
            list_ = [(param_name, v) for v in hyperparameters]
            
            lists.append(list_)
        import random
        configurations = list(itertools.product(*lists))
        random.shuffle(configurations)
        for configuration in configurations:
            yield {**base_dict, **dict(configuration)}
    
    def get_args_list(self):
        return self._args_list
