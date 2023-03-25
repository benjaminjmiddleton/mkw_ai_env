# -*- coding: utf-8 -*-
from collections import deque
import random
import socket
import json
import atari_py
import cv2
import torch

DRIFT_LEFT = -2
WHEELIE_LEFT = -1
WHEELIE_FORWARD = 0
WHEELIE_RIGHT = 1
DRIFT_RIGHT = 2
DRIFT_FORWARD = 3

class Env():
  def __init__(self, args):
    self.device = args.device
    # self.ale = atari_py.ALEInterface()
    # self.ale.setInt('random_seed', args.seed)
    # self.ale.setInt('max_num_frames_per_episode', args.max_episode_length)
    # self.ale.setFloat('repeat_action_probability', 0)  # Disable sticky actions
    # self.ale.setInt('frame_skip', 0)
    # self.ale.setBool('color_averaging', False)
    # self.ale.loadROM(atari_py.get_game_path(args.game))  # ROM loading must be done after setting options
    # actions = self.ale.getMinimalActionSet() #[ 0  1  3  4 11 12]
    # self.actions = dict([i, e] for i, e in zip(range(len(actions)), actions)) # {0: 0, 1: 1, 2: 3, 3: 4, 4: 11, 5: 12}
    # self.lives = 0  # Life counter (used in DeepMind training)
    # self.life_termination = False  # Used to check if resetting only from loss of life
    self.actions = {0: DRIFT_LEFT, 1: WHEELIE_LEFT, 2: WHEELIE_FORWARD, 3: WHEELIE_RIGHT, 4: DRIFT_RIGHT, 5: DRIFT_FORWARD}
    self.window = args.history_length  # Number of frames to concatenate
    self.state_buffer = deque([], maxlen=args.history_length)
    # Wait to make initial connection to dolphin client
    host = socket.gethostname()
    port = 5555
    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(1)
    self.client_socket, _ = sock.accept()
    # self.training = True  # Consistent with model training mode

  def _get_state(self):
    # state = cv2.resize(self.ale.getScreenGrayscale(), (84, 84), interpolation=cv2.INTER_LINEAR)
    message = json.loads(self.client_socket.recv(131072).decode('utf-8'))
    observation = message[0]
    reward = message[1]
    done = message[2]
    frame = message[3]
    return torch.tensor(observation, dtype=torch.float32, device=self.device).div_(255), reward, done, frame

  def _reset_buffer(self):
    for _ in range(self.window):
      self.state_buffer.append(torch.zeros(84, 84, device=self.device))

  def reset(self):
    self.client_socket.send( ( json.dumps( (WHEELIE_FORWARD, True) ).encode("utf-8") ) )
    # if self.life_termination:
    #   self.life_termination = False  # Reset flag
    #   self.ale.act(0)  # Use a no-op after loss of life
    # else:
    # Reset internals
    self._reset_buffer()
    # self.ale.reset_game()
    # Perform up to 30 random no-ops before starting
    # for _ in range(random.randrange(30)):
    #   observation, _, _ = self._get_state()
    #   self.client_socket.send( ( json.dumps( (WHEELIE_FORWARD, False) ).encode("utf-8") ) )
      # self.ale.act(0)  # Assumes raw action 0 is always no-op
      # if self.ale.game_over():
      #   self.ale.reset_game()
    # Process and return "initial" state
    observation, _, _, _ = self._get_state()
    self.state_buffer.append(observation)
    # self.lives = self.ale.lives()
    return torch.stack(list(self.state_buffer), 0)

  def step(self, action):
    # Repeat action 4 times, max pool over last 2 frames
    # frame_buffer = torch.zeros(2, 84, 84, device=self.device)
    # reward, done = 0, False
    # for t in range(4):
    #   reward += self.ale.act(self.actions.get(action))
    #   if t == 2:
    #     frame_buffer[0] = self._get_state()
    #   elif t == 3:
    #     frame_buffer[1] = self._get_state()
    #   done = self.ale.game_over()
    #   if done:
    #     break
    # observation = frame_buffer.max(0)[0]
    self.client_socket.send( ( json.dumps( (self.actions[action], False) ).encode("utf-8") ) )
    observation, reward, done, frame = self._get_state() # json.loads(self.client_socket.recv(131072).decode('utf-8'))
    self.state_buffer.append(observation)
    # Detect loss of life as terminal in training mode
    # if self.training:
    #   lives = self.ale.lives()
    #   if lives < self.lives and lives > 0:  # Lives > 0 for Q*bert
    #     self.life_termination = not done  # Only set flag when not truly done
    #     done = True
    #   self.lives = lives
    # Return state, reward, done
    return torch.stack(list(self.state_buffer), 0), reward, done, frame

  # Uses loss of life as terminal signal
  # def train(self):
  #   self.training = True

  # Uses standard terminal signal
  # def eval(self):
  #   self.training = False

  def action_space(self):
    return len(self.actions)

  # def render(self):
  #   cv2.imshow('screen', self.ale.getScreenRGB()[:, :, ::-1])
  #   cv2.waitKey(1)

  def close(self):
    self.client_socket.close()
