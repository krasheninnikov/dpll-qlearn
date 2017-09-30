import numpy as np
import sklearn
import sklearn.preprocessing
import sklearn.pipeline
from sklearn.linear_model import SGDRegressor
from sklearn.kernel_approximation import RBFSampler


def make_state(var_range, cdata):
    clause_lengths = np.array(map(len, cdata.clauses))

    n_clauses  = len(clause_lengths)
    percentile_len = np.percentile(clause_lengths, np.arange(6)*20)

    state = np.append(percentile_len, n_clauses)
    return state


class ReplayBuf():
    """
    Synchronised ring buffers that hold (s_t, a_t, reward, s_t_plus_1).
    - s_t and s_t_plus_1 have shape of (replay_size, n_ch, img_side, img_side)
    - a_t : int vector (one-hot encoding)
    - reward : int
    """
    def __init__(self, replay_len, s_len, n_actions):
        self.shape = s_len
        self.index = 0
        self.replay_len = replay_len

        self.s_t = np.zeros((replay_len,s_len), dtype = 'float32')
        self.s_t_plus_1 = np.zeros((replay_len,s_len), dtype = 'float32')
        self.n_actions = n_actions
        self.action = np.zeros((replay_len, n_actions))
        self.reward = np.zeros(replay_len)

        self.s_current = None
        self.a_current = None
        self.r_current = None

    def append(self, s_t, a_t, r_t, s_t_plus_1):
        self.s_t[self.index, :] = s_t
        self.s_t_plus_1[self.index, :] = s_t_plus_1
        self.reward[self.index] = r_t

        act = np.zeros(self.n_actions)
        act[a_t] = 1
        self.action[self.index] = act

        self.index += 1
        self.index = self.index % self.replay_len

    def append_s_a_r(self, s_t, a_t, r_t):
        if self.s_current is None:
            self.s_current = s_t
            self.a_current = a_t
            self.r_current = r_t

        if self.s_current is not None:
            self.append(self.s_current, self.a_current, self.r_current, s_t)
            self.s_current = s_t
            self.a_current = a_t
            self.r_current = r_t

    def game_over(self):
        self.s_current = None
        self.a_current = None
        self.r_current = None

        self.reward[self.index - 1] = 1

    def reset_index_back_by_n(self, n):
        self.index = self.index - n
        self.index = self.index % self.replay_len

class Estimator():
    """
    Value Function approximator.
    """

    def __init__(self, replay_buf):
        self.n_actions = replay_buf.n_actions

        # We create a separate model for each action in the environment's
        # action space. Alternatively we could somehow encode the action
        # into the features, but this way it's easier to code up.
        self.models = []
        for _ in range(self.n_actions):
            model = SGDRegressor(learning_rate="constant")
            # We need to call partial_fit once to initialize the model
            # or we get a NotFittedError when trying to make a prediction
            # This is quite hacky.
            # model.partial_fit([self.featurize_state(replay_buf.s_t)], [0])
            model.partial_fit(replay_buf.s_t, np.zeros(replay_buf.replay_len))
            self.models.append(model)


    def predict(self, s, a=None):
        """
        Makes value function predictions.

        Args:
            s: state to make a prediction for
            a: (Optional) action to make a prediction for

        Returns
            If an action a is given this returns a single number as the prediction.
            If no action is given this returns a vector or predictions for all actions
            in the environment where pred[i] is the prediction for action i.

        """

        if not a:
            return np.array([m.predict(s) for m in self.models])
        else:
            return self.models[a].predict(s)[0]

    def update(self, s, a, y):
        """
        Updates the estimator parameters for a given state and action towards
        the target y.
        """
        self.models[a].partial_fit(s, y)


    def policy_eps_greedy(self, epsilon, observation):

        """
        Creates an epsilon-greedy policy based on a given Q-function approximator and epsilon.

        Args:
            estimator: An estimator that returns q values for a given state
            epsilon: The probability to select a random action . float between 0 and 1.
            nA: Number of actions in the environment.

        Returns:
            A function that takes the observation as an argument and returns
            the probabilities for each action in the form of a numpy array of length nA.
        """

        A = np.ones(self.n_actions, dtype=float) * epsilon / self.n_actions
        q_values = self.predict([observation])
        best_action = np.argmax(q_values)
        A[best_action] += (1.0 - epsilon)
        return A

    def train(self, discount_factor, replay_buf):
        for a in range(replay_buf.n_actions):
            action_index = (replay_buf.action[:,a] == a)
            if sum(action_index) >0:
                q_values_next = self.predict(replay_buf.s_t_plus_1[action_index])
                td_target = replay_buf.reward[action_index] + discount_factor * np.max(q_values_next)
                self.update(replay_buf.s_t[action_index, :], a, td_target)
