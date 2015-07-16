import numpy as np
import pandas as pd
import argparse
from astropy.io import fits

from fiery_llama.matched_filters import PointFilter, cubeify


parser = argparse.ArgumentParser()
help_data = "Must be .h5 or .fits file type."
parser.add_argument("data", help=help_data)
table_help = "if .h5 file provide table name"
parser.add_argument("--data-table", help=table_help)

help_signal = "Must be .h5 or .fits file type."
parser.add_argument("signal", help=help_signal)
parser.add_argument("--signal-table", help=table_help)

help_noise = "Must be .h5 or .fits file type."
parser.add_argument("noise", help=help_noise)
parser.add_argument("--noise-table", help=table_help)

parser.add_argument("--nra", default=100)
parser.add_argument("--ndec", default=100)

_help = "the columns to filter on, if not given defaults to all filter columns"
parser.add_argument("--signal-columns", nargs="*", help=_help)

parser.add_argument("--create-image")


if __name__ == "__main__":
    args = parser.parse_args()

    if args.data_table is not None:
        data = pd.read_hdf(args.data, args.data_table)
    else:
        hdul = fits.open(args.data)
        data = pd.DataFrame(hdul[1].data)

    if args.signal_table is not None:
        signal_pts = pd.read_hdf(args.signal, args.signal_table)
    else:
        hdul = fits.open(args.signal)
        signal_pts = pd.DataFrame(hdul[1].data)

    if args.noise_table is not None:
        noise_pts = pd.read_hdf(args.noise, args.noise_table)
    else:
        hdul = fits.open(args.noise)
        noise_pts = pd.DataFrame(hdul[1].data)

    signal_columns = args.signal_columns
    if signal_columns is None:
        signal_columns = signal_pts.columns

    signal_filter = PointFilter(
        signal_pts,
        filtered_columns=signal_columns,
        sigma_vec=np.repeat(0.2, len(signal_columns)))

    noise_filter = PointFilter(
        noise_pts,
        filtered_columns=signal_columns,
        sigma_vec=np.repeat(0.2, len(signal_columns)))

    print('fitering')
    dsr = data
    print('signal')
    signal_weights = signal_filter.get_weights(dsr)
    print('noise')
    noise_weights = noise_filter.get_weights(dsr)
    weights = signal_weights - noise_weights

    # if args.hexbin is not None:
        # import matplotlib.pylab as plt
        # plt.hexbin(
        #     dsr["RA"],
        #     dsr["DEC"],
        #     gridsize=20,
        #     C=weights, reduce_C_function=np.sum)

        # plt.show()

    dsr['signal_weights'] = signal_weights
    dsr['noise_weights'] = noise_weights
    dsr['weights'] = weights
    dsr.to_hdf('output.h5', 'photometry')

    if args.create_image is not None:
        out_img = cubeify(
            dsr,
            n=(int(args.nra), int(args.ndec)),
            columns=['RA', 'DEC'],
            target='weights')

        cards = [
            # fits.Card(keyword='NAXIS1', value=out_img.shape[0]),
            # fits.Card(keyword='NAXIS2', value=out_img.shape[1]),
            fits.Card(keyword='RAINMIN', value=np.min(dsr['RA'])),
            fits.Card(keyword='RAINMAX', value=np.max(dsr['RA'])),
            fits.Card(keyword='DECINMIN', value=np.min(dsr['DEC'])),
            fits.Card(keyword='DECINMAX', value=np.max(dsr['DEC'])),
        ]
        
        header = fits.Header(cards=cards)
        primary_hdu = fits.PrimaryHDU(header=header)

        img_hdu = fits.ImageHDU(out_img)

        hdulist = fits.HDUList(
            [primary_hdu, img_hdu]
        )
        
        hdulist.writeto(args.create_image)








