# Import the game
import gym_super_mario_bros
# Import the Joypad wrapper
from nes_py.wrappers import JoypadSpace
# Import the SIMPLIFIED controls
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT
from gym.wrappers import GrayScaleObservation
# Import Vectorization Wrappers
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv
# Import Matplotlib to show the impact of frame stacking
from matplotlib import pyplot as plt
# Import os for file path management
import os
# Import PPO for algos
from stable_baselines3 import PPO
# Import Base Callback for saving models
from stable_baselines3.common.callbacks import BaseCallback

# Setup game
def brute_force_game() -> None:
    env = gym_super_mario_bros.make('SuperMarioBros-v0')
    env = JoypadSpace(env, SIMPLE_MOVEMENT)

    done = True
    # Loop through each frame in the game
    for step in range(100000):
        # Start the game to begin with
        if done:
            # Start the game
            env.reset()
        # Do random actions
        state, reward, done, info = env.step(env.action_space.sample())
        # Show the game on the screen
        env.render()
    # Close the game
    env.close()


class TrainAndLoggingCallback(BaseCallback):

    def __init__(self, check_freq, save_path, verbose=1):
        super(TrainAndLoggingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.save_path = save_path

    def _init_callback(self):
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self):
        if self.n_calls % self.check_freq == 0:
            model_path = os.path.join(self.save_path, 'best_model_{}'.format(self.n_calls))
            self.model.save(model_path)

            return True


def train_ai_model() -> None:
    # 1. Create the base environment
    env = gym_super_mario_bros.make('SuperMarioBros-v0')
    # 2. Simplify the controls
    env = JoypadSpace(env, SIMPLE_MOVEMENT)
    # 3. Grayscale
    env = GrayScaleObservation(env, keep_dim=True)
    # 4. Wrap inside the Dummy Environment
    env = DummyVecEnv([lambda: env])
    # 5. Stack the frames
    env = VecFrameStack(env, 4, channels_order='last')

    state = env.reset()
    state, reward, done, info = env.step([5])

    # plt is pyplot from matlib
    plt.figure(figsize=(20, 16))
    for idx in range(state.shape[3]):
        plt.subplot(1, 4, idx + 1)
        plt.imshow(state[0][:, :, idx])
    plt.show()

    CHECKPOINT_DIR = './train/'
    LOG_DIR = './logs/'

    # Setup model saving callback
    callback = TrainAndLoggingCallback(check_freq=10000, save_path=CHECKPOINT_DIR)

    # This is the AI model started
    model = PPO('CnnPolicy', env, verbose=1, tensorboard_log=LOG_DIR, learning_rate=0.000001,
                n_steps=512, device="opencl",)
    print(model.device)

    # Train the AI model, this is where the AI model starts to learn
    model.learn(total_timesteps=1000000, callback=callback)


if __name__ == "__main__":
    # brute_force_game()
    train_ai_model()
