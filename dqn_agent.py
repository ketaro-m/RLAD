import sys
import matplotlib.pyplot as plt
import threading
import time

import numpy as np
import random
from collections import namedtuple, deque
from Car import *
from env import Env #later uncomment

import torch
import torch.nn.functional as F
import torch.optim as optim

from dqn_model import QNet

BUFFER_SIZE = int(1e5)  #replay buffer size
BATCH_SIZE = 64         # minibatch size
GAMMA = 0.99            # discount factor
TAU = 1e-3              # for soft update of target parameters
LR = 5e-4               # learning rate
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
            return np.argmax(action_values.cpu().data.numpy())
        else:
            return random.choice(np.arange(self.action_size))
            
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
        #shape of output from the model (batch_size,action_dim) = (64,4)
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
if __name__ == "__main__":
    args = sys.argv
    numOpps = int(args[1])
    interval = int(args[2]) # interval to update the actions

    show = False
    if (len(args) > 3):
        if (args[3] == "--display"):
            show = True


    dqn_agent = DQNAgent(state_size = 5 + 4 * Agent.MAX_OPPS, action_size=11*11, seed = 0)
    global env
    env = Env(numOpps, interval)
    env.reset()


    def dqn(n_episodes= 200, max_t = 1000, eps_start=1.0, eps_end = 0.01, eps_decay=0.996):
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
        scores_window = deque(maxlen=100) # last 100 scores
        eps = eps_start
        for i_episode in range(1, n_episodes+1):
            state = env.reset()
            score = 0
            for t in range(max_t):
                action = dqn_agent.act(state, eps)
                next_state,reward,done = env.step(action)
                dqn_agent.step(state,action,reward,next_state,done)
                ## above step decides whether we will train(learn) the network
                ## actor (local_qnetwork) or we will fill the replay buffer
                ## if len replay buffer is equal to the batch size then we will
                ## train the network or otherwise we will add experience tuple in our 
                ## replay buffer.
                state = next_state
                score += reward
                if done:
                    break
                scores_window.append(score) ## save the most recent score
                scores.append(score) ## save the score
                eps = max(eps*eps_decay,eps_end)## decrease the epsilon
                print('\rEpisode {}\tAverage Score {:.2f}'.format(i_episode,np.mean(scores_window)), end="")
                if i_episode %100==0:
                    print('\rEpisode {}\tAverage Score {:.2f}'.format(i_episode,np.mean(scores_window)))
                    
                if np.mean(scores_window)>=200.0:
                    print('\nEnvironment solve in {:d} epsiodes!\tAverage score: {:.2f}'.format(i_episode-100,
                                                                                            np.mean(scores_window)))
                    torch.save(dqn_agent.qnetwork_local.state_dict(),'checkpoint.pth')
                    break

                if (show):
                    time.sleep(interval / 1000)
                    
        return scores


    def display(env, interval):
        env.display(interval)


    def train():
        time.sleep(2)
        scores= dqn()

        #plot the scores
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.plot(np.arange(len(scores)),scores)
        plt.ylabel('Score')
        plt.xlabel('Epsiode #')
        plt.show()



    if (show):
        runThread = threading.Thread(target=train)
        displayThread = threading.Thread(target=display, args=(env,interval))


        flag = True
        try:
            runThread.start()
            displayThread.start()
            print("thread started")
            runThread.join()
            displayThread.join()
        except KeyboardInterrupt:
            flag = False
    else:
        train()