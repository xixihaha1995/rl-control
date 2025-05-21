import numpy as np
import gymnasium as gym
from gymnasium import spaces

from stable_baselines3.common.env_checker import check_env


class GuessNumberEnv(gym.Env):
    """
    A simple environment where the agent tries to guess a target number from 0 to 8.
    The episode ends when the guess is correct.
    """
    metadata = {"render_modes": ["console"]}

    def __init__(self, max_number=8, render_mode="console"):
        super(GuessNumberEnv, self).__init__()
        self.max_number = max_number
        self.render_mode = render_mode

        # Action space: choose a number from 0 to max_number
        self.action_space = spaces.Discrete(self.max_number + 1)

        # Observation space: dummy (stateless), could be anything
        self.observation_space = spaces.Discrete(1)

        self.target_number = None
        self.guess_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.target_number = 6
        self.guess_count = 0
        if self.render_mode == "console":
            print(f"[Environment] A new number has been chosen between 0 and {self.max_number}")
        return 0, {}  # dummy observation

    def step(self, action):
        self.guess_count += 1
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action {action}. Must be in 0 to {self.max_number}")

        reward = 1 if action == self.target_number else 0
        terminated = bool(action == self.target_number)
        truncated = False
        info = {"target": self.target_number, "guess_count": self.guess_count}

        if self.render_mode == "console":
            print(f"[Step] Agent guessed: {action} -> {'Correct!' if reward == 1 else 'Wrong'}")

        return 0, reward, terminated, truncated, info  # dummy observation

    def render(self):
        if self.render_mode == "console":
            print(f"[Render] Try to guess the number between 0 and {self.max_number}")

    def close(self):
        pass
# from stable_baselines3.common.env_checker import check_env
# env = GuessNumberEnv(max_number=8)
# check_env(env, warn=True)

# env = GuessNumberEnv(max_number=8)
# obs, _ = env.reset()
# env.render()
#
# print("Observation space:", env.observation_space)
# print("Action space:", env.action_space)
# print("Sample action:", env.action_space.sample())
#
# # Try guessing randomly
# n_steps = 20
# for step in range(n_steps):
#     action = env.action_space.sample()  # Random guess
#     print(f"\nStep {step + 1}: Guessing {action}")
#     obs, reward, terminated, truncated, info = env.step(action)
#     done = terminated or truncated
#     print(f"Observation: {obs}, Reward: {reward}, Done: {done}, Info: {info}")
#     env.render()
#     if done:
#         print(f"🎯 Correct guess! Found {info['target']} in {info['guess_count']} steps.")
#         break
# else:
#     print("❌ Failed to guess the number within the allowed steps.")
from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.env_util import make_vec_env
# Create vectorized environment (optional for single env, but good practice for SB3)
vec_env = make_vec_env(GuessNumberEnv, n_envs=1, env_kwargs=dict(max_number=8))

# Or use single env directly
env = GuessNumberEnv(max_number=8)

# Train the agent with A2C (or PPO/DQN)
model = A2C("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=25)

obs = vec_env.reset()
n_steps = 20

for step in range(n_steps):
    action, _ = model.predict(obs, deterministic=True)

    print(f"\nStep {step + 1}")
    print("Action:", action)

    obs, reward, done, info = vec_env.step(action)

    print("Observation:", obs)
    print("Reward:", reward)
    print("Done:", done)

    # Optional: render if your env supports it
    try:
        vec_env.render()
    except NotImplementedError:
        pass

    if done[0]:  # done is a list/array in VecEnv, so use done[0]
        print("Goal reached! 🎯 Reward:", reward[0])
        break
