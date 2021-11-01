import pickle, sys

class response:

  def __init__(self,header, data):
    self.header = header
    try:
      self.json = pickle.loads(data[header:])
    except Exception as e:
      print(e)
      self.json = None
    self.raw = data