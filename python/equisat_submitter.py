#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
import pmt
import time
import requests
import datetime
from .equisat_telemetry_parser import equisat_telemetry_parser

class equisat_submitter(gr.sync_block):
    """
    Block responsible for submitting EQUiSat telemetry to BSE's
    telemetry server.

    Receives (and correlates) two message inputs,
    the raw packet and its Reed-Solomon corrected version (both PDUs).
    """

    # route to telemetry input handler
    BSE_API_ROUTE = "http://api.brownspace.org/equisat/receive/raw"

    # minimum time between packet submits
    MIN_REQUEST_PERIOD = 1

    def __init__(self, station_name, api_key, latitude, longitude, initial_timestamp, post_publicly,
                 api_route=BSE_API_ROUTE, source_app="gr-equisat_decoder"):
        gr.sync_block.__init__(self,
                               name="equisat_submitter",
                               in_sig=[],
                               out_sig=None)

        if station_name is None or len(station_name) == 0:
            print("[WARNING] you need to specify a station name (callsign or name) to publish to the BSE data server")
        if api_key is None or len(api_key) == 0:
            print("[WARNING] you need to specify an API key to publish to the BSE data server")

        self.station_name = station_name
        self.latitude = latitude
        self.longitude = longitude
        self.post_publicly = post_publicly
        self.api_key = api_key
        self.api_route = api_route
        self.source_app = source_app

        dtformat = '%Y-%m-%d %H:%M:%S'
        if initial_timestamp == "":
            self.initial_timestamp = None
        else:
            self.initial_timestamp = datetime.datetime.strptime(initial_timestamp, dtformat)
        self.start_timestamp = datetime.datetime.utcnow()

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def handle_msg(self, msg_pmt):
        meta = pmt.car(msg_pmt)
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print("[ERROR] Received invalid message type. Expected u8vector")
            return

        raw_vec = pmt.dict_ref(meta, pmt.intern("raw"), pmt.get_PMT_NIL())
        if raw_vec != pmt.get_PMT_NIL() and pmt.is_u8vector(raw_vec):
            raw = equisat_telemetry_parser.bytes_to_hex_str(
                pmt.u8vector_elements(raw_vec))
        else:
            print("[WARNING] No raw field provided in PDU; not publishing raw transmission")
            raw = None

        corrected = equisat_telemetry_parser.bytes_to_hex_str(pmt.u8vector_elements(msg))
        self.submit_packet(raw, corrected)
        time.sleep(self.MIN_REQUEST_PERIOD)

    def submit_packet(self, raw, corrected):
        if self.station_name is None or len(self.station_name) == 0 or \
                self.api_key is None or len(self.api_key) == 0:
            print("[WARNING] not submitting to the BSE data server because no API key or station name provided")
            return

        now = datetime.datetime.utcnow()
        if self.initial_timestamp is None:
            rx_time = now
        else:
            rx_time = self.initial_timestamp + (now - self.start_timestamp)

        epoch = datetime.datetime(1970, 1, 1)
        rx_time_posix = (rx_time - epoch).total_seconds() * 1000  # ms since 1970

        jsn = {
            "raw": raw,
            "corrected": corrected,
            "station_name": self.station_name,
            "source": self.source_app,
            "post_publicly": self.post_publicly,
            "rx_time": rx_time_posix,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "secret": self.api_key
        }

        try:
            r = requests.post(self.api_route, json=jsn)
            if r.status_code == 201:
                print("Submitted duplicate packet from '%s' successfully" % self.station_name)
            elif r.status_code == requests.codes.ok:
                print("Submitted packet from '%s' successfully" % self.station_name)
            else:
                print("[WARNING] couldn't submit packet (%d): %s" % (r.status_code, r.text))

        except Exception as ex:
            print("[ERROR] couldn't submit packet: %s" % ex)






