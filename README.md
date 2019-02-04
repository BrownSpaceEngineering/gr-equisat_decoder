# EQUiSat Decoder
A GNU radio Out-Of-Tree Module and custom blocks to decode EQUiSat's 4FSK transceiver

## Dependencies
- [GNU Radio](https://wiki.gnuradio.org/index.php/InstallingGR) (this repo is a GNU Radio "module")
- [Swig](http://swig.org/download.html) (usually available in package managers; required for GNU Radio to generate Python bindings from C++)
- See `requirements.txt` for additional Python dependencies (run `pip install -r requirements.txt `)

## Build and Installation
Run:
```
pip install -r requirements.txt # if you haven't
git submodule init # for BrownSpaceEngineering/packetparse
git submodule update
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
```

## Running
There are GNU Radio flowgraphs in `apps/` that you can "compile" and run as follows:
```
grcc <flowgraph>.grc
python <flowgraph>.py # run the generated python file
```
You can also open the flowgraph in [GNU Radio Companion](https://wiki.gnuradio.org/index.php/GNURadioCompanion) and click "generate" instead of using `grcc`

These flowgraphs are:
#### `apps/equisat.grc`

This flowgraph listens for packets from a UDP audio stream from the GQRX SDR software or other frontends (see below). Usually all you need to do is click the "UDP" button in the bottom right of the GQRX interface, but if you have reconfigured GQRX you may need to specify a host and port to the Python script; see `python equisat.py --help` for how to.

**If you don't have or don't want to use GQRX as a frontend**, check out [gr-frontends](https://github.com/daniestevez/gr-frontends) for alternative scripts that also stream over UDP. This repo provides frontends for SDRs, file sources, and other sources. For Windows, it is possible to use SDR# with [this plugin](https://github.com/cpicoto/satnogstracker) to stream UDP audio and track the satellite. 

If any complete packets are successfully received, they will be printed to the screen along with the data fields found in the packet. To automatically publish good packets to Brown Space Engineering's database, see below.

#### `apps/equisat_fm_input.grc` 

This flowgraph does essentially the same decoding as `equisat.grc`, but requires that you specify a FM-demodulated wav file to use as input using the `--wavfile=` parameter. It also does not publish to our API yet. You may also need to specify `--sample-rate` if your file was not recorded at 48kHz.

## Optimizing performance
The decoder is still in development, and performance can benefit from some tuning to a specific setup. Here are some variables in the flowgraphs worth tuning:
- `gain_mu` - this is a parameter for the MM Clock Recovery block for recovering the 4FSK symbols. [GNU Radio documentation](https://www.gnuradio.org/doc/doxygen/classgr_1_1digital_1_1clock__recovery__mm__cc.html) suggests that the optimal setting of this variable is dependent on the amplitude of the FM-demodulated audio coming into the flowgraph (i.e. the amplitude of the symbols). We've found that the correct tuning can make a significant difference in decoding quality. Generally decreasing the value is most helpful; overly large values can result in instability.
 
- `Min premable length (EQUiSat 4FSK Preamble Detector)` - this is a parameter that controls the minimum length of preamble is required for the decoder to try and search for the sync word and subsequently decode the following blocks. Decreasing it can allow the decoder to find more packets, but it is unlikely to improve the quality of the demodulated data, and setting it far too low can have an adverse impact on packet quality and detect preambles from noise.

## Publishing to EQUiSat's telemetry database
You can publish good received packets to Brown Space Engineering's database server by specifying the following as command line arguments to the flowgraphs above:

- A station name/callsign
- Your latitude/longitude (optional)
- If you're replaying a recording, the UTC time it started at
- An API key. To generate one, run the `generate-api-key.sh` script in the root of the repository.
 
You can run `python equisat.py --help` for specifics. We'd really appreciate it if you send us your data!
 