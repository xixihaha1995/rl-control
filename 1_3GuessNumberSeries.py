import numpy as np
import gymnasium as gym
from gymnasium import spaces

from stable_baselines3.common.env_checker import check_env


class GuessSequenceEnv(gym.Env):
    """
    Environment where the agent guesses numbers in a sequence.
    Reward is -abs(guess - true_value) at each time step.
    """
    metadata = {"render_modes": ["console"]}

    def __init__(self, target_sequence=None, max_guess=8):
        super().__init__()
        self.target_sequence = target_sequence or [5, 8, 7, 1, 4]
        self.sequence_length = len(self.target_sequence)
        self.max_guess = max_guess

        # Actions are guesses from 0 to max_guess
        self.action_space = spaces.Discrete(self.max_guess + 1)

        # Observation could be the current step index (or dummy)
        self.observation_space = spaces.Discrete(self.sequence_length)

        self.current_step = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.total_reward = 0.0
        self.guesses = []
        self.done = False
        return np.array([0]).astype(np.int32), {}

    def step(self, action):
        if self.done:
            raise RuntimeError("Environment is done. Please reset.")

        target = self.target_sequence[self.current_step]
        step_reward = -abs(action - target)  # still use negative distance
        self.total_reward += step_reward
        self.guesses.append(action)

        self.current_step += 1
        self.done = self.current_step >= len(self.target_sequence)

        # Only return total reward on the last step
        reward = float(self.total_reward) if self.done else 0.0

        obs = np.array([0]).astype(np.int32)  # dummy obs (no need for prediction)
        info = {
            "target_sequence": self.target_sequence,
            "guesses": self.guesses,
        }

        return obs, reward, self.done, False, info

    def render(self):
        if self.current_step < len(self.target_sequence):
            print(f"Step {self.current_step}, Target: {self.target_sequence[self.current_step]}")
        else:
            print("🔁 Sequence complete.")

    def close(self):
        pass
# env = GuessSequenceEnv(max_guess=33)
# check_env(env, warn=True)

env = GuessSequenceEnv(max_guess=8)
obs, _ = env.reset()
env.render()

print("Observation space:", env.observation_space)
print("Action space:", env.action_space)
print("Sample action:", env.action_space.sample())
#
# # Try guessing randomly
n_steps = len(env.target_sequence)  # Automatically adapt to sequence length
total_reward = 0.0

obs, _ = env.reset()

for step in range(n_steps):
    action = env.action_space.sample()  # Random guess
    print(f"\nStep {step + 1}: Guessing {action}")

    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    total_reward += reward

    print(f"Observation: {obs}, Reward: {reward:.2f}, Done: {done}, Info: {info}")
    env.render()

    if done:
        print(f"\n✅ Sequence finished in {step + 1} steps. Total reward: {total_reward:.2f}")
        break
    else:
        print(f"\n⚠️ Sequence incomplete. Total reward after {n_steps} steps: {total_reward:.2f}")
from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.env_util import make_vec_env
target_sequence = [5, 8, 7, 1, 4]
max_number = max(target_sequence)

# Create a single or vectorized environment
env = GuessSequenceEnv(target_sequence=target_sequence)
vec_env = make_vec_env(GuessSequenceEnv, n_envs=1, env_kwargs=dict(target_sequence=target_sequence))

# Initialize the model
model = A2C("MlpPolicy", env, verbose=1)

# Train the model
model.learn(total_timesteps=100)  # Increase for better learning
#
n_steps = len(env.target_sequence)
obs = vec_env.reset()

total_reward = 0.0

for step in range(n_steps):
    action, _ = model.predict(obs, deterministic=True)
    print(f"\nStep {step + 1}: Guessing {action}")

    obs, reward, done, info = vec_env.step(action)

    # reward, done are arrays of shape (n_envs,), here n_envs=1
    total_reward += reward[0]

    print(f"Observation: {obs}")
    print(f"Reward: {reward[0]:.2f}")
    print(f"Done: {done[0]}")
    print(f"Info: {info[0]}")

    try:
        vec_env.render()
    except NotImplementedError:
        pass

    if done[0]:
        print(f"\n✅ Sequence finished in {step + 1} steps. Total reward: {total_reward:.2f}")
        break
else:
    print(f"\n⚠️ Sequence incomplete after {n_steps} steps. Total reward: {total_reward:.2f}")