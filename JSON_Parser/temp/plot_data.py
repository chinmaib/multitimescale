import os
import numpy as np
import matplotlib.pyplot as plt


def main():

    hi = [2962,2482,678,1957,29,1233,28,13,46]

    plt.bar(['Nav','Search','Still','Mov Vic','Door', \
            'action','Marker','Rm Marker','Exit'],hi)
    plt.xlabel('Role')
    plt.ylabel('Average distribution of labels')
    plt.ylim(0,5000)
    plt.show()



main()
