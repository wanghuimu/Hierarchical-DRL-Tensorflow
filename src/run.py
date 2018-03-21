import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from collections import namedtuple
import time



from hDQN_keras import hDQN



import utils



def one_hot(state):
	vector = np.zeros(6)
	vector[state-1] = 1.0
	return np.expand_dims(vector, axis=0)


#env = StochasticMDPEnv()
try:
	env = utils.get_env('stochastic_mdp-v0')
	utils.info("Env created")
except:
	env.reset()
	utils.info("Env reset")	
def hRun():
	t0 = time.time()
	total_episodes = 1000
	
	ActorExperience = namedtuple("ActorExperience", ["state", "goal", "action", "reward", "next_state", "done"])
	MetaExperience = namedtuple("MetaExperience", ["state", "goal", "reward", "next_state", "done"])	
	
	agent = hDQN()
	info = {}
	info['visits'] = np.zeros((6, total_episodes))
	info['Fs'] = []
	anneal_factor = (1.0 - 0.1) / total_episodes
	utils.info("Annealing factor: " + str(anneal_factor))
	
	for episode in range(total_episodes):
		#Episodes
		utils.info("\n\n### EPISODE "+ str(episode) + "###")
		state = env.reset()
		info['visits'][state-1][episode] += 1
		done = False
		while not done:
			#Goals
			goal = agent.select_goal(one_hot(state))
			agent.goal_selected[goal-1] += 1
			utils.info("New Goal: "+ str(goal) + "\nState-Actions:")
	
			total_external_reward = 0
			initial_state = state #TODO make sure is copying teh value not ref
			goal_reached = False
			while not done and not goal_reached:
				#Actions
				action = agent.select_move(one_hot(state), one_hot(goal), goal)
				#action = 1
				next_state, external_reward, done, _ = env.step(action)
				utils.info(str((state,action,next_state,done)) + "; ")
				
				info['visits'][next_state-1][episode] += 1
				intrinsic_reward = agent.criticize(goal, next_state)
				goal_reached = next_state == goal
				if goal_reached:
					agent.goal_success[goal-1] += 1
					utils.info("Goal reached!! ")
				if next_state == 6:
					utils.info("S6 reached!! ")
				exp = ActorExperience(one_hot(state), one_hot(goal), action, intrinsic_reward, one_hot(next_state), done)
				agent.store(exp, meta = False)
				agent.update(meta = False)
				agent.update(meta = True)
				total_external_reward += external_reward
				state = next_state
			info['Fs'].append(total_external_reward)
			exp = MetaExperience(one_hot(initial_state), one_hot(goal), total_external_reward, one_hot(next_state), done)
			
			agent.store(exp, meta=True)
			
			#Annealing 
			agent.meta_epsilon -= anneal_factor
			avg_success_rate = agent.goal_success[goal-1] / agent.goal_selected[goal-1]
			
			if(avg_success_rate == 0 or avg_success_rate == 1):
				agent.actor_epsilon[goal-1] -= anneal_factor
			else:
				agent.actor_epsilon[goal-1] = 1 - avg_success_rate	
			if(agent.actor_epsilon[goal-1] < 0.1):
				agent.actor_epsilon[goal-1] = 0.1
			utils.info("meta_epsilon: " + str(agent.meta_epsilon))
			utils.info("actor_epsilon " + str(goal) + ": " + str(agent.actor_epsilon[goal-1]))
	
	utils.info("Elapsed time",time.time() - t0)
	groupby = int(.01 * total_episodes)
	grouped_visits = np.array_split(info['visits'], groupby, axis = 1)
	x = range(len(grouped_visits))
	plt.figure()
	for i in range(2,6):
		means, stds = zip(*[(gp[i].mean(), gp[i].std()) for gp in grouped_visits])
		means, stds = np.array(means), np.array(stds)
		plt.plot(means, label = "S" + str(i+1))
		plt.fill_between(x, means - stds, means + stds, alpha = .3)
	plt.ylim([0,3])
	plt.legend()
	plt.xlabel("Episode (*" + str(groupby) +")")
	plt.show()


