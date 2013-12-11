# vim: fdm=indent
'''
author:     Fabio Zanini
date:       09/12/13
content:    Plot functions for Sanger chromatographs.
'''
# Modules
import numpy as np

# Globals
colors = {'A': 'r', 'C': 'b', 'G': 'g', 'T': 'k'}


# Functions
def plot_chromatograph(seq, ax, xlim=None):
    '''Plot Sanger chromatograph'''

    # Get raw signals and plot them
    chs = np.array([seq.annotations['channel '+str(i)] for i in xrange(1, 5)])
    ts = np.array(seq.annotations['peak positions'])
    bases = seq.annotations['channels']

    # Rescale x axis
    x = 1.0 * np.arange(chs.shape[1]) -ts[0]
    ts -= ts[0]
    ind = x <= ts[-1]
    x = x[ind]
    chs = chs[:, ind]
    norm = x[-1] / len(seq)
    x /= norm
    ts /= norm

    if xlim is not None:
        ind = (x >= xlim[0]) & (x <= xlim[1])
        x = x[ind]
        chs = chs[:, ind]

        ind = ((ts >= xlim[0]) & (ts <= xlim[1])).nonzero()[0]
        ts = ts[ind]
        seq = seq[ind[0]: ind[-1] + 1]

    for base, color in colors.iteritems():
        ax.plot(x, chs[bases.index(base)] / chs.max(), color=color, lw=2,
                label=base)

    # Plot bases at peak positions
    for i in xrange(len(ts)):
        ax.text(ts[i], -0.08, seq[i], color=colors[seq[i]])

    ax.set_ylim(ymin=-0.15, ymax=1.05)
    ax.set_xlim(xmin=ts[0] - max(2, 0.02 * (ts[-1] - ts[0])),
                xmax=ts[-1] + max(2, 0.02 * (ts[-1] - ts[0])))
    #ax.set_ylabel('Intensity [A.U.]')
    ax.set_yticklabels([])
    ax.grid()
    ax.legend(loc=1)



# Test script
if __name__ == '__main__':

    from parser import parse_abi
    filename = 'test_data/FZ01_A12_096.ab1'
    seq = parse_abi(filename)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(15, 6))

    plot_chromatograph(seq, ax, xlim=[10, 40])

    plt.ion()
    plt.show()
