import gymnasium as gym, numpy as np
from gymnasium import spaces
from queue import Queue
from stable_baselines3.common.env_checker import check_env
from EPlus_0_Simulator import EPlusSimulatorForGymEnv


class EplusEnv(gym.Env):
    def __init__(self, grid_size=10):
        super(EplusEnv, self).__init__()
        self.obs_queue = Queue(maxsize=1)
        self.act_queue = Queue(maxsize=1)
        self.epSimulator = EPlusSimulatorForGymEnv(self.obs_queue, self.act_queue)
    def reset(self, seed=None, options=None):
        """
        Important: the observation must be a numpy array
        :return: (np.array)
        """
        super().reset(seed=seed, options=options)
        self.epsimulator.start()  # start the EnergyPlus simulator thread
        # here we convert to float32 to make it more general (in case we want to use continuous actions)
        return np.array([self.agent_pos]).astype(np.float32), {}  # empty info dict

    def step(self, action):
        self.timestep += 1
        terminated, truncated = False, False

        if self.energyplus_simulator.simulation_complete:
            truncated = True
            obs = self.last_obs
        else:
            self.act_queue.put(action)
            obs = self.obs_queue.get()

        if action == self.LEFT:
            self.agent_pos -= 1
        elif action == self.RIGHT:
            self.agent_pos += 1
        else:
            raise ValueError(
                f"Received invalid action={action} which is not part of the action space"
            )
        # Account for the boundaries of the grid
        self.agent_pos = np.clip(self.agent_pos, 0, self.grid_size)
        # Are we at the left of the grid?
        terminated = bool(self.agent_pos == 0)
        truncated = False  # we do not limit the number of steps here

        # Null reward everywhere except when reaching the goal (left of the grid)
        reward = 1 if self.agent_pos == 0 else 0
        '''
        energy_term = self.lambda_energy * self.W_energy * self.energy_penalty
        comfort_term = self.lambda_temp * \
            (1 - self.W_energy) * self.comfort_penalty
        reward = energy_term + comfort_term
        '''

        # Optionally we can pass additional info, we are not using that for now
        info = {}

        return (
            np.fromiter(obs.values(), dtype=np.float32),
            reward,
            terminated,
            truncated,
            info,
        )

    def render(self):
        pass

    def close(self):
        self.epSimulator.stop()

from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.env_util import make_vec_env

# Instantiate the env
vec_env = make_vec_env(GoLeftEnv, n_envs=1, env_kwargs=dict(grid_size=10))

env = GoLeftEnv(grid_size=10)
print("before learning")
# Train the agent
model = A2C("MlpPolicy", env, verbose=1).learn(5000)
print("after learning")

# # Test the trained agent
# # using the vecenv
obs = vec_env.reset()
n_steps = 20
for step in range(n_steps):
    action, _ = model.predict(obs, deterministic=True)
    print(f"Step {step + 1}")
    print("Action: ", action)
    obs, reward, done, info = vec_env.step(action)
    print("obs=", obs, "reward=", reward, "done=", done)
    vec_env.render()
    if done:
        # Note that the VecEnv resets automatically
        # when a done signal is encountered
        print("Goal reached!", "reward=", reward)
        break