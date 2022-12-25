from PyQt5.Qt import *
from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5 import QtCore, QtWidgets, uic ,QtGui
from PyQt5.QtGui import *
from numpy.lib.function_base import angle
from mainWindow import Ui_MainWindow
import pyqtgraph as pg
import vtk
from vtk.util import numpy_support
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk 
import numpy
import json
# common packages 
import numpy as np 
import os
import copy
import matplotlib.pyplot as plt
from functools import reduce
# reading in dicom files
import pydicom
# scipy linear algebra functions 
from scipy.linalg import norm
from ipywidgets.widgets import * 
import ipywidgets as widgets
from plotly.graph_objs import *
import sys
import math as mathh
math = vtk.vtkMath()
import os
from scipy import ndimage 
from scipy.interpolate import CubicSpline
from math import sqrt 
from matplotlib.path import Path
from turtle import color, pen, pencolor
from sympy import symbols
from os import listdir
from os.path import isfile, join
from matplotlib.patches import Ellipse
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
import cv2
import time
from operator import itemgetter
