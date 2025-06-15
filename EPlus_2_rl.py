from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from LichenEPlusRL import *

trainingEnv = gym.make('LichenEPlusRL-demo-v1')
obs, _ = trainingEnv.reset()
testingEnv = gym.make('LichenEPlusRL-demo-v1')

# model = A2C("MlpPolicy", trainingEnv, verbose=1).learn(5000)
# model = SAC("MlpPolicy", trainingEnv, verbose=1).learn(5000)
# model = DQN("MlpPolicy", trainingEnv, verbose=1).learn(5000)
# model = TD3("MlpPolicy", trainingEnv, verbose=1).learn(5000)
model = PPO("MlpPolicy", trainingEnv, verbose=1).learn(5000)

obs = testingEnv.reset()
n_steps = 20
for step in range(n_steps):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, info = testingEnv.step(action)
