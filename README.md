# EQUiSat Decoder
A GNU radio Out-Of-Tree Module and custom blocks to decode EQUiSat's 4FSK transceiver

## Dependencies
- [GNU Radio](https://wiki.gnuradio.org/index.php/InstallingGR) (this repo is a GNU Radio "module")
- [Swig](http://swig.org/download.html) (usually available in package managers; required for GNU Radio to generate Python bindings from C++)
- See `requirements.txt` for additional Python dependencies (run `pip install -r requirements.txt `)

## Installation
Run:
```
git submodule init
git submodule update
mkdir build
cd build
cmake ..
make
sudo make install
```

## Running
There are GNU Radio flowgraphs in `apps/` that you can "compile" and run as follows:
```
grcc <flowgraph>.grc
python <flowgraph>.py # run the generated python file
```
You can also open the flowgraph in GNU Radio Companion and click "generate" instead of using `grcc`

These flowgraphs are:
#### `apps/equisat.grc` 

This flowgraph listens for packets from a UDP audio stream from the GQRX SDR software. Usually all you need to do is click the "UDP" button in the bottom right of the GQRX interface, but if you have reconfigured GQRX you may need to specify a host and port to the Python script; see `python equisat.py --help` for how to.

If any complete packets are successfully received, they will be printed to the screen along with the data fields found in the packet. If you specify a callsign and database ID, the packet will also be published to Brown Space Engineering's data server (we'd love it if you send us your data)! 

#### `apps/equisat_fm_input.grc` 

This flowgraph does essentially the same decoding as `equisat.grc`, but requires that you specify a FM-demodulated wav file to use as input using the `--wavfile=` parameter. It also does not publish to our API yet. You may also need to specify `--sample-rate` if your file was not recorded at 48kHz.