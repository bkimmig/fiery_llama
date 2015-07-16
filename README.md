# Fiery Llama
A tool that can be used for matched filter analysis. 

## Dependencies
- latbin 
    + pip install latbin
- numpy
- pandas
- astropy

## Authors
- Tim Anderton
- Brian Kimmig


## Installation
- Clone the directory where ever you would like on you machine.
    + git clone https://github.com/bkimmig/fiery_llama.git
- Add module to your PYTHONPATH (something like below, if bash)
    + export PYTHONPATH="path/to/fiery_llama/":$PYTHONPATH
    + alias fiery_llama="py -i path/to/fiery_llama/scripts/script.py"

## Pre-made scripts
- filter.py
    + Parameters needed: data, signal, noise
- basic_phot_filter.py
    + Parameters needed: data, signal

## Example
For an astronomy data set (photometry, 'g', 'r', 'i'). We can filter the data set with an isochrone and produce an image cube. Assume the isochrone has the same parameters (except position) that the data set has. Make sure column names in both the isochrone and data are named the same. In this example we will use a .h5 file type, this will also take .fits file type.

#### Files
- data.h5, data.fits
    + columns: 'RA' 'DEC' 'g' 'r' 'i'
- iso.h5, iso.fits
    + columns: 'g' 'r' 'i'

#### Run Command for script 'basic_phot_filter.py'
'basic_phot_filter.py' needs to be the file aliased.
Note: --nra and --ndec specify the output image size.

- Commands
    - if .h5 file
            $ fiery_llama data.h5 --data-table photometry iso_13.0gyr_1.5fe_19000pc_gr.h5 --signal-table isochrone --nra 100 --ndec 100 --create-image cube.fits 

    - .fits file
            $ fiery_llama data.fits  iso.fits --nra 100 --ndec 100 --create-image cube.fits 

output.h5 will be your data with the weights column added. cube.fits will be the weighted data cube grouped by ra and dec.