import matplotlib.pyplot as plt
import os
import numpy as np

def main():

    plt.bar(['Mission 1','Mission 2'],[14.6,12.8],width=0.5)
    plt.ylim([0,20])
    plt.ylabel("Average regular victims saved")
    plt.show()
    



main()
