import dill
from random import choice
import re

with open('models/model', 'rb') as f:
    model_1 = dill.load(f)
model_1.generate(length=20, prefix='')
