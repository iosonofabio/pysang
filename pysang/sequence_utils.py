# vim: fdm=indent
'''
author:     Fabio Zanini
date:       14/12/13
content:    Sequence utility functions.
'''
# Functions
def reverse_complement(seqrecord):
    '''Reverse complement a Sanger chromatography SeqRecord including traces.'''
    from Bio.SeqRecord import SeqRecord
    from Bio.Seq import reverse_complement as rc

    # Reverse complement called sequence
    seqn = seqrecord.seq.reverse_complement()

    srev = SeqRecord(seqn,
                     id=seqrecord.id, name=seqrecord.name,
                     description=seqrecord.description)

    # Complement light channels and reverse each one
    srev.annotations['channels'] = ''.join(map(rc, seqrecord.annotations['channels']))
    for i in xrange(1, 5):
        srev.annotations['channel '+str(i)] = seqrecord.annotations['channel '+str(i)][::-1]

    # Reverse peak positions
    if 'trace_x' in seqrecord.annotations:
        tmax = seqrecord.annotations['trace_x'][-1]
    else:
        tmax = len(seqrecord.annotations['channel 1'])
    srev.annotations['peak positions'] = [tmax - p for p in seqrecord.annotations['peak positions'][::-1]]

    # Copy the rest
    for key in seqrecord.annotations:
        if key not in srev.annotations:
            srev.annotations[key] = seqrecord.annotations[key]

    return srev



# Test script
if __name__ == '__main__':

    from parser import parse_abi
    from pkg_resources import resource_stream
    input_file = resource_stream(__name__, 'data/FZ01_A12_096.ab1')
    seq = parse_abi(input_file)

    seqrev = reverse_complement(seq)

    from plot import plot_chromatograph
    plot_chromatograph(seq, xlim=[10, 40])
    plot_chromatograph(seqrev, xlim=[len(seq) - 40, len(seq) - 10])

