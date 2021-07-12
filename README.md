# Reinforcement Learning for Autonomous Driving
Train the DQN, Deep Q Network of the car to proceed towards the goal avoiding the opponents.

<img width="1000" alt="overview.png" src="https://user-images.githubusercontent.com/52503908/125268545-c5c06880-e342-11eb-8e94-f6bae22dbbeb.png">

# Requirements

## Python

Python 3.6.9

## Packages 

```bash
$ python3 -m venv .venv  
$ source .venv/bin/activate  
(.venv) $ pip install -r requirements.txt  
```

# Usage

## Training

### Strategy

- Optimize reward_function() in `env.py`.
- Change the model architecture described in `dqn_model.py`.
- Optimize the hyperparameters of DQN in `dqn_agent.py`.
- Try various learning conditions by changing the key parameters such as `numOpps`, `actionInterval` in `dqn_agent.py`.

```bash
$ python dqn_agent.py
```

Model parameters are saved in `params/` directory, and the score graph (*TODO: the graph isn't appropriate, need to be fixed*) are shown and saved in `fig/` directory when the training has finished.


## Velification
Specify a `*.pth` file saved by the training process in `main.py`. If you don't, randomly intialized Q-net is used.

```bash
$ python main.py [opponent number]
# ex. python main.py 5
```

<img width="300" alt="ex1.png" src="https://user-images.githubusercontent.com/52503908/125262320-0b7a3280-e33d-11eb-985d-d2a208ed227f.gif"> <img width="300" alt="ex2.png" src="https://user-images.githubusercontent.com/52503908/125262335-0d43f600-e33d-11eb-8a1b-6401c518cf65.gif">
