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
        import matplotlib.pyploy as plt
        fig, ax = plt.subplots(1, 1, figsize=(16, 6))

    if seq is None:
        ax.set_xlim(-2, 102)
        ax.set_ylim(-0.15, 1.05)
        return

    # Get raw signals and plot them
    chs = [seq.annotations['channel '+str(i)] for i in xrange(1, 5)]
    ts = seq.annotations['peak positions']
    bases = seq.annotations['channels']

    # Rescale x axis
    x = [1.0 * r - ts[0] for r in xrange(len(chs[0]))]
    ts = [t - ts[0] for t in ts]
    ind = [True if xi <= ts[-1] else False for xi in x]
    x = [xi for (indi, xi) in izip(ind, x) if indi]
    chs = [[ci for (indi, ci) in izip(ind, ch) if indi] for ch in chs]
    norm = 1.0 * x[-1] / len(seq)
    x = [1.0 * xi / norm for xi in x]
    ts = [1.0 * ti / norm for ti in ts]

    if xlim is not None:
        ind = [(xi >= xlim[0]) and (xi <= xlim[1]) for xi in x]
        if not any(ind):
            return 

        x = [xi for (indi, xi) in izip(ind, x) if indi]
        chs = [[ci for (indi, ci) in izip(ind, ch) if indi] for ch in chs]
        ind = [i for (i, ti) in enumerate(ts) if (ti >= xlim[0]) and (ti <= xlim[1])]
        ts = ts[ind[0]: ind[-1] + 1]
        seq = seq[ind[0]: ind[-1] + 1]

    chmax = max(map(max, chs))
    for base, color in colors.iteritems():
        y = [1.0 * ci / chmax for ci in chs[bases.index(base)]]
        ax.plot(x, y, color=color, lw=2,
                label=base)

    # Plot bases at peak positions
    for i in xrange(len(ts)):
        ax.text(ts[i], -0.11, seq[i], color=colors[seq[i]])

    ax.set_ylim(ymin=-0.15, ymax=1.05)
    ax.set_xlim(xmin=ts[0] - max(2, 0.02 * (ts[-1] - ts[0])),
                xmax=ts[-1] + max(2, 0.02 * (ts[-1] - ts[0])))
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

    plot_chromatograph(seq, ax, xlim=[10, 40])

    plt.ion()
    plt.show()
