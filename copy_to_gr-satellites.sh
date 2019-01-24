#!/usr/bin/env bash
# This script copies the required files from this repository to the gr-satellites repository,
# making updating both easier.
# Note that this does not completely install the EQUiSat decoder in gr-satellites;
# further configuration is required (this is just an update script)

# additional modifications:
# - grc/CMakeLists.txt
# - python/CMakeLists.txt
# - python/__init__.py
# - include/satellites/CMakeLists.txt
# - lib/CMakeLists.txt
# - swig/satellites.i

if [[ -n "$1" ]]; then
    SATS_DIR=$1
else
    SATS_DIR=../gr-satellites
fi

# grc (xml)
cp -v grc/equisat_decoder_equisat_4fsk_block_decode.xml "$SATS_DIR/grc/satellites_equisat_4fsk_block_decode.xml"
cp -v grc/equisat_decoder_equisat_4fsk_preamble_detect.xml "$SATS_DIR/grc/satellites_equisat_4fsk_preamble_detect.xml"
cp -v grc/equisat_decoder_equisat_submitter.xml "$SATS_DIR/grc/satellites_equisat_submitter.xml"
cp -v grc/equisat_decoder_equisat_telemetry_parser.xml "$SATS_DIR/grc/satellites_equisat_telemetry_parser.xml"
cp -v grc/equisat_decoder_equisat_fec_decoder.xml "$SATS_DIR/grc/satellites_equisat_fec_decoder.xml"
# replace categories in XML
sed -i -e "s/\[EQUiSat Decoder\]/\[Satellites\]\/Packet/" "$SATS_DIR/grc/satellites_equisat_4fsk_block_decode.xml" "$SATS_DIR/grc/satellites_equisat_4fsk_preamble_detect.xml"
sed -i -e "s/\[EQUiSat Decoder\]/\[Satellites\]\/Misc/" "$SATS_DIR/grc/satellites_equisat_submitter.xml"
sed -i -e "s/\[EQUiSat Decoder\]/\[Satellites\]\/Telemetry/" "$SATS_DIR/grc/satellites_equisat_telemetry_parser.xml"
sed -i -e "s/\[EQUiSat Decoder\]/\[Satellites\]\/FEC/" "$SATS_DIR/grc/satellites_equisat_fec_decoder.xml"

# replace imports, etc. in XML
sed -i -e "s/equisat_decoder/satellites/g" "$SATS_DIR"/grc/satellites_equisat_*

# python
cp -v python/equisat_4fsk_block_decode.py "$SATS_DIR/python/"
cp -v python/equisat_4fsk_preamble_detect.py "$SATS_DIR/python/"
cp -v python/equisat_submitter.py "$SATS_DIR/python/"
cp -v python/equisat_telemetry_parser.py "$SATS_DIR/python/"

# packetparse
cp -v python/packetparse/packetparse.py "$SATS_DIR/python/equisat_packetparse.py"
# replace constants import in packetparse with the file itself
sed -i -e "/from constants import constants/{r python/packetparse/constants.py" -e "d}" "$SATS_DIR/python/equisat_packetparse.py"
# update imports with new name
sed -i -e "s/import packetparse/import equisat_packetparse as packetparse/g" "$SATS_DIR/python/equisat_telemetry_parser.py"

# C++
cp -v include/equisat_decoder/equisat_fec_decoder.h "$SATS_DIR/include/satellites/"
cp -v lib/equisat_fec_decoder_impl.* "$SATS_DIR/lib/"
# update class name
sed -i -e "s/EQUISAT_DECODER_API/SATELLITES_API/g" "$SATS_DIR/include/satellites/equisat_fec_decoder.h"
# change namespaces, includes, header guards, and comments
sed -i -e "s/equisat_decoder/satellites/gI" "$SATS_DIR/include/satellites/equisat_fec_decoder.h" "$SATS_DIR"/lib/equisat_fec_decoder_impl.*

# apps
cp -v apps/equisat_gr-satellites.grc "$SATS_DIR/apps/equisat.grc"


