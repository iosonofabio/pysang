# vim: fdm=indent
'''
author:     Fabio Zanini
date:       09/12/13
content:    Plot functions for Sanger chromatographs.
'''
# Modules
from itertools import izip

# Globals
colors = {'A': 'r', 'C': 'b', 'G': 'g', 'T': 'k'}


# Functions
def plot_chromatograph(seq, ax=None, xlim=None):
    '''Plot Sanger chromatograph'''

    if ax is None:
        import matplotlib.pyplot as plt
        plt.ion()
        fig, ax = plt.subplots(1, 1, figsize=(16, 6))

    if seq is None:
        ax.set_xlim(-2, 102)
        ax.set_ylim(-0.15, 1.05)
        return

    # Get signals
    traces = [seq.annotations['channel '+str(i)] for i in xrange(1, 5)]
    peaks = seq.annotations['peak positions']
    bases = seq.annotations['channels']
    x = seq.annotations['trace_x']

    # Limit to a region if necessary
    if xlim is not None:
        ind = [(xi >= xlim[0]) and (xi <= xlim[1]) for xi in x]
        if not any(ind):
            return 

        x = [xi for (indi, xi) in izip(ind, x) if indi]
        traces = [[ci for (indi, ci) in izip(ind, tr) if indi] for tr in traces]
        ind = [i for (i, ti) in enumerate(peaks) if (ti >= xlim[0]) and (ti <= xlim[1])]
        peaks = peaks[ind[0]: ind[-1] + 1]
        seq = seq[ind[0]: ind[-1] + 1]

    # Plot traces
    trmax = max(map(max, traces))
    for base, color in colors.iteritems():
        y = [1.0 * ci / trmax for ci in traces[bases.index(base)]]
        ax.plot(x, y, color=color, lw=2, label=base)

    # Plot bases at peak positions
    for i, peak in enumerate(peaks):
        ax.text(peak, -0.11, seq[i], color=colors[seq[i]],
                horizontalalignment='center')

    ax.set_ylim(ymin=-0.15, ymax=1.05)
    ax.set_xlim(xmin=peaks[0] - max(2, 0.02 * (peaks[-1] - peaks[0])),
                xmax=peaks[-1] + max(2, 0.02 * (peaks[-1] - peaks[0])))
    ax.set_yticklabels([])
    ax.grid()
    ax.legend(loc=1)



# Test script
if __name__ == '__main__':

    from parser import parse_abi
    from pkg_resources import resource_stream
    input_file = resource_stream(__name__, 'data/FZ01_A12_096.ab1')
    seq = parse_abi(input_file)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(15, 6))

    plot_chromatograph(seq, ax, xlim=[210, 240])

    plt.ion()
    plt.show()
