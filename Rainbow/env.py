# -*- coding: utf-8 -*-
from collections import deque
import random
import socket
import json
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

  def _get_state(self):
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
    self._reset_buffer()
    observation, _, _, _ = self._get_state()
    self.state_buffer.append(observation)
    return torch.stack(list(self.state_buffer), 0)

  def step(self, action):
    self.client_socket.send( ( json.dumps( (self.actions[action], False) ).encode("utf-8") ) )
    observation, reward, done, frame = self._get_state() # json.loads(self.client_socket.recv(131072).decode('utf-8'))
    self.state_buffer.append(observation)
    return torch.stack(list(self.state_buffer), 0), reward, done, frame

  def action_space(self):
    return len(self.actions)

  def close(self):
    self.client_socket.close()
