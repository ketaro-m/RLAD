import sys
import matplotlib.pyplot as plt
import threading
import time
import datetime

import numpy as np
import random
from collections import namedtuple, deque
from Car import *
from env import Env #later uncomment

import torch
import torch.nn.functional as F
import torch.optim as optim

from dqn_model import QNet

BUFFER_SIZE = int(1e5)  # replay buffer size
BATCH_SIZE = 64         # minibatch size, or how many samples taken the replay buffer for experience replay
GAMMA = 0.995            # discount factor
TAU = 1e-3              # for soft update of target parameters
LR = 0.1               # learning rate
UPDATE_EVERY = 4        # how often to update the network

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class DQNAgent():

    """Interacts with and learns form environment."""
    def __init__(self, state_size, action_size, seed):
        """Initialize an Agent object.
        
        Params
        =======
            state_size (int): dimension of each state
            action_size (int): dimension of each action
            seed (int): random seed
        """
        
        self.state_size = state_size
        self.action_size = action_size
        self.seed = seed
        
        
        #Q- Network
        self.qnetwork_local = QNet(state_size, action_size, seed).to(device)
        self.qnetwork_target = QNet(state_size, action_size, seed).to(device)
        
        self.optimizer = optim.Adam(self.qnetwork_local.parameters(),lr=LR)
        
        # Replay memory 
        self.memory = ReplayBuffer(action_size, BUFFER_SIZE, BATCH_SIZE, seed)
        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step = 0
        
    def step(self, state, action, reward, next_step, done):
        # Save experience in replay memory
        state = np.append(state, [0] * (self.state_size - len(state)))
        next_step = np.append(next_step, [0] * (self.state_size - len(next_step)))
        self.memory.add(state, action, reward, next_step, done)

        # Learn every UPDATE_EVERY time steps.
        self.t_step = (self.t_step+1) % UPDATE_EVERY
        if self.t_step == 0:
            # If enough samples are available in memory, get radom subset and learn

            if len(self.memory)>BATCH_SIZE:
                experience = self.memory.sample()
                self.learn(experience, GAMMA)

    def act(self, state, eps = 0):
        """Returns action for given state as per current policy
        Params
        =======
            state (array_like): current state
            eps (float): epsilon, for epsilon-greedy action selection
        """
        state = np.append(state, [0] * (self.state_size - len(state)))
        state = torch.from_numpy(state).float().unsqueeze(0).to(device)
        self.qnetwork_local.eval() # change to the eval mode
        with torch.no_grad():
            action_values = self.qnetwork_local(state)
        self.qnetwork_local.train() # change to the train mode

        #Epsilon -greedy action selction
        if random.random() > eps:
            return np.argmax(action_values.cpu().data.numpy()), action_values.cpu().data.numpy()[0]
        else:
            return random.choice(np.arange(self.action_size)), action_values.cpu().data.numpy()[0]
            
    def learn(self, experiences, gamma):
        """Update value parameters using given batch of experience tuples.
        Params
        =======
            experiences (Tuple[torch.Variable]): tuple of (s, a, r, s', done) tuples
            gamma (float): discount factor
        """
        states, actions, rewards, next_states, dones = experiences
        ## TODO: compute and minimize the loss
        criterion = torch.nn.MSELoss()
        self.qnetwork_local.train()
        self.qnetwork_target.eval()

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken. These are the actions which would've been taken
        # for each batch state according to qnetwork_local
        # size(predicted_targets) = (batch_size, 1) 
        predicted_targets = self.qnetwork_local(states).gather(1,actions)

        with torch.no_grad():
            labels_next = self.qnetwork_target(next_states).detach().max(1)[0].unsqueeze(1)


        # .detach() ->  Returns a new Tensor, detached from the current graph.
        labels = rewards + (gamma* labels_next*(1-dones))
        
        loss = criterion(predicted_targets,labels).to(device)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # ------------------- update target network ------------------- #
        self.soft_update(self.qnetwork_local,self.qnetwork_target,TAU)
            
    def soft_update(self, local_model, target_model, tau):
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        Params
        =======
            local model (PyTorch model): weights will be copied from
            target model (PyTorch model): weights will be copied to
            tau (float): interpolation parameter
        """
        for target_param, local_param in zip(target_model.parameters(),
                                            local_model.parameters()):
            target_param.data.copy_(tau*local_param.data + (1-tau)*target_param.data)


class ReplayBuffer():
    """Fixed -size buffe to store experience tuples."""

    def __init__(self, action_size, buffer_size, batch_size, seed):
        """Initialize a ReplayBuffer object.
        
        Params
        ======
            action_size (int): dimension of each action
            buffer_size (int): maximum size of buffer
            batch_size (int): size of each training batch
            seed (int): random seed
        """
        
        self.action_size = action_size
        self.memory = deque(maxlen=buffer_size)
        self.batch_size = batch_size
        self.experiences = namedtuple("Experience", field_names=["state",
                                                                "action",
                                                                "reward",
                                                                "next_state",
                                                                "done"])
        self.seed = seed
        
    def add(self, state, action, reward, next_state, done):
        """Add a new experience to memory."""
        e = self.experiences(state,action,reward,next_state,done)
        self.memory.append(e)
        
    def sample(self):
        """Randomly sample a batch of experiences from memory"""
        experiences = random.sample(self.memory,k=self.batch_size)
        
        states = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float().to(device)
        actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).long().to(device)
        rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(device)
        next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float().to(device)
        dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float().to(device)
        
        return (states,actions,rewards,next_states,dones)
    def __len__(self):
        """Return the current size of internal memory."""
        return len(self.memory)


# training
# you need to set these variables (numOpps, actionInterval, runInterval, SOLVED_NUM)
# and inside dqn() (n_episodes, eps_decay, display_episodes)
if __name__ == "__main__":
    args = sys.argv
    numOpps = 3 # how many opponents
    actionInterval = 250 # interval to update the actions [ms]
    runInterval = 50
    displayInterval = 10
    SOLVED_NUM = 750 / runInterval # ideal step number to achieve goal, depending on intervel
    # SOLVED_SCORE = 1.0 * (GAMMA ** SOLVED_NUM) # judge if this network has been trained enough
    SOLVED_SCORE = 0.6

    show_flag = [False, False] # flag for displaying [(show or not), (main thread and GUI thread interval are synchronized or not (this is for speed up training but display the simulation))]

    dqn_agent = DQNAgent(state_size = 5 + 4 * Agent.MAX_OPPS, action_size=11*11, seed = 0)
    ## uncommend below line and put the specific model state to train from
    # dqn_agent.qnetwork_local.load_state_dict(torch.load("params/model_2021-04-06-17-52_3_50_250.pth", map_location=device))
    global env
    env = Env(numOpps, runInterval, actionInterval) # env = Env(numOpps, runInterval, actionInterval) starting from 3 fewer opponents
    # env.agent.setThetaRange((np.pi*2/5, np.pi*(1-2/5)))  # starting from proceeding almost straight
    env.reset()


    def dqn(n_episodes= 50000, max_t = 1000, eps_start=1.0, eps_end = 0.01, eps_decay=0.995):
        """Deep Q-Learning
        
        Params
        ======
            n_episodes (int): maximum number of training epsiodes
            max_t (int): maximum number of timesteps per episode
            eps_start (float): starting value of epsilon, for epsilon-greedy action selection
            eps_end (float): minimum value of epsilon 
            eps_decay (float): mutiplicative factor (per episode) for decreasing epsilon
            
        """
        scores = [] # list containing score from each episode
        average_scores = [] # average score of each 100 episodes
        scores_window = deque(maxlen=100) # last 100 scores
        step_window = deque(maxlen=100) # last 100 how many steps to be taken to goal
        eps = eps_start
        display_episodes = [[5000, 5001], [7500, 7501], [10000, 10001], [20000, 20001], [30000, 30005], [49990, 50000]] # when synchronize the interval and show the display ([[start, end], ...])
        display_index = 0 # index variable you don't have to touch

        for i_episode in range(1, n_episodes+1):
            # start showing the simulator display at some episodes
            if (i_episode == display_episodes[0][0]):
                show_flag[0] = True
                displayThread = threading.Thread(target=display, args=(env,displayInterval))
                key_flag = True
                show_flag[1] = True
                try:
                    displayThread.start()
                except KeyboardInterrupt:
                    key_flag = False
            # synchronize the interval and show the display
            if (show_flag[0]):
                if (i_episode == display_episodes[display_index][0]):
                    time.sleep(0.25)
                    show_flag[1] = True
                    env.gui.set_interval(runInterval)
                elif (i_episode == display_episodes[display_index][1]):
                    show_flag[1] = False
                    if (display_index < len(display_episodes) - 1):
                        display_index += 1
                    env.gui.set_interval(30 * 1000) # set proper GUI interval depending on the episodes at which the display is shown
                elif (i_episode == display_episodes[display_index][0] - 100):
                    env.gui.set_interval(1 * 1000)

            ### change the env conditions
            # if (i_episode == 20000):
            #     # env.agent.setThetaRange(((np.pi/3, np.pi*2/3)))
            #     env.change_opps(5)
            # if (i_episode == 50000):
            #     # env.agent.setThetaRange(((np.pi/6, np.pi*5/6)))
            #     env.change_opps(7)


            state = env.reset()
            score = 0
            done = False
            for t in range(max_t):
                action, q_values = dqn_agent.act(state, eps)
                ## comment out below if you don't wanna see the q_value plotting
                if (show_flag[0] and show_flag[1]):
                    env.gui.set_qvals(action, q_values)
                ##
                next_state,reward,done,goal_flag = env.step(action, display=show_flag[1])
                dqn_agent.step(state,action,reward,next_state,done)
                ## above step decides whether we will train(learn) the network
                ## actor (local_qnetwork) or we will fill the replay buffer
                ## if len replay buffer is equal to the batch size then we will
                ## train the network or otherwise we will add experience tuple in our 
                ## replay buffer.
                state = next_state
                score += reward * (GAMMA ** t)
                if done:
                    break
                # if (show_flag[0] and show_flag[1]):
                #     time.sleep(runInterval / 1000)
            scores_window.append(score) ## save the most recent score
            scores.append(score) ## save the score
            if (goal_flag):
                step_window.append(t)
            print('\rEpisode {}\t Epsilon {:.2f}\tScore {:.2f}\t@ {:0=3}'.format(i_episode,eps,score,t), end="")
            if i_episode %100==0:
                sys.stdout.write("\033[2K\033[G")
                sys.stdout.flush()
                print('\rEpisode {}\t Average Score {:.4f} \tAgerage Step {:.2f}'.format(i_episode,np.mean(scores_window), np.mean(step_window)))
                average_scores.append(np.mean(scores_window))
                
            if len(scores_window) > 50 and np.mean(scores_window)>=SOLVED_SCORE:
                print('\nEnvironment solve in {:d} epsiodes!\tAverage score: {:.2f}'.format(i_episode-100,np.mean(scores_window)))
                torch.save(dqn_agent.qnetwork_local.state_dict(),'./params/checkpoint.pth')
                break
            eps = max(eps*eps_decay,eps_end)## decrease the epsilon


        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        torch.save(dqn_agent.qnetwork_local.state_dict(), "./params/model_"+date+"_"+str(numOpps)+"_"+str(runInterval)+"_"+str(actionInterval)+".pth")
        return scores, average_scores, date


    def display(environment, interval):
        environment.display(interval)


    
    time.sleep(2)
    scores, average_scores, date = dqn()

    #plot the scores
    plt.figure()
    plt.plot(np.arange(len(scores)),scores)
    plt.plot(np.arange(50, 100*len(average_scores), 100), average_scores)
    plt.ylabel('Score')
    plt.xlabel('Epsiode #')
    plt.savefig('fig/score_'+date+'.png')
    plt.show()
    plt.show()
    plt.clf()