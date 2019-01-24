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

This flowgraph listens for packets from a UDP audio stream from the GQRX SDR software. Usually all you need to do is click the "UDP" button in the bottom right of the GQRX interface, but if you have reconfigured GQRX you may need to specify a host and port to the Python script; see `python equisat.py --help` for how to.

If any complete packets are successfully received, they will be printed to the screen along with the data fields found in the packet. To automatically publish good packets to Brown Space Engineering's database, see below

#### `apps/equisat_fm_input.grc` 

This flowgraph does essentially the same decoding as `equisat.grc`, but requires that you specify a FM-demodulated wav file to use as input using the `--wavfile=` parameter. It also does not publish to our API yet. You may also need to specify `--sample-rate` if your file was not recorded at 48kHz.

## Publishing to EQUiSat's telemetry database
You can publish good received packets to Brown Space Engineering's database server by specifying the following as command line arguments to the flowgraphs above:

- A station name/callsign
- Your latitude/longitude (optional)
- If you're replaying a recording, the UTC time it started at
- An API key. To generate one, run the `generate-api-key.sh` script in the root of the repository.
 
You can run `python equisat.py --help` for specifics. We'd really appreciate it if you send us your data!
 
## Pushing changes here to gr-satellites
This repository is designed to easily integrate into [gr-satellites](https://github.com/daniestevez/gr-satellites), and has a script to do so.

Run `./copy_to_gr-satellites <gr-satellites directory>` to copy and modify all the required files from gr-equisat_decoder to gr-satellites. 

This also copies the flowgraph `apps/equisat_gr-satellites.grc`. Note that this flowgraph is very similar to `apps/equisat.grc`, but is NOT automatically derived from it. So if you improve/update `equisat.grc`, you will need to manually update `equisat_gr-satellites.grc` to correspond. This will likely require you to have gr-satellites installed because this flowgraph draws the EQUiSat decoder blocks from gr-satellites among other things.