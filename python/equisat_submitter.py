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
from equisat_telemetry_parser import equisat_telemetry_parser

class equisat_submitter(gr.sync_block):
    """
    Block responsible for submitting EQUiSat telemetry to BSE's
    telemetry server.

    Receives (and correlates) two message inputs,
    the raw packet and its Reed-Solomon corrected version (both PDUs).
    """

    # route to telemetry input handler
    BSE_API_ROUTE = "http://localhost:3000/equisat/receive/raw"#"http://api.brownspace.org/equisat/receive/raw"

    # minimum time between packet submits
    MIN_REQUEST_PERIOD = 1

    def __init__(self, station_name, api_key, api_route=BSE_API_ROUTE):
        gr.sync_block.__init__(self,
                               name="equisat_submitter",
                               in_sig=[],
                               out_sig=None)

        if station_name is None or len(station_name) == 0:
            print("[WARNING] you need to specify a station name (callsign or name) to publish to the BSE data server")
        if api_key is None or len(api_key) == 0:
            print("[WARNING] you need to specify an API key to publish to the BSE data server")

        self.station_name = station_name
        self.api_key = api_key
        self.api_route = self.BSE_API_ROUTE # TODO

        # since we have multiple inputs, keep queues and pop off sections
        # when we have a (corresponding) one of each (i.e. equal length queues)
        self.raw_queue = []
        self.corrected_queue = []

        self.message_port_register_in(pmt.intern('raw'))
        self.message_port_register_in(pmt.intern('corrected'))
        self.set_msg_handler(pmt.intern('raw'), self.handle_raw_msg)
        self.set_msg_handler(pmt.intern('corrected'), self.handle_corrected_msg)

    def handle_raw_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return

        self.raw_queue.append(equisat_telemetry_parser.bytes_to_hex_str(pmt.u8vector_elements(msg)))
        self.submit_if_ready()

    def handle_corrected_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return

        self.corrected_queue.append(equisat_telemetry_parser.bytes_to_hex_str(pmt.u8vector_elements(msg)))
        self.submit_if_ready()

    def submit_if_ready(self):
        while len(self.raw_queue) == len(self.corrected_queue) and len(self.raw_queue) > 0:
            self.submit_packet(self.raw_queue.pop(0), self.corrected_queue.pop(0))
            time.sleep(self.MIN_REQUEST_PERIOD)

    def submit_packet(self, raw, corrected):
        if self.station_name is None or len(self.station_name) == 0 or \
                self.api_key is None or len(self.api_key) == 0:
            print("[WARNING] not submitting to the BSE data server because no API key or station name provided")
            return

        jsn = {
            "raw": raw,
            "corrected": corrected,
            "station_name": self.station_name,
            "secret": self.api_key
        }

        try:
            r = requests.post(self.api_route, json=jsn)
            if r.status_code == 201:
                print("Submitted duplicate packet from '%s' successfully" % self.station_name)
            elif r.status_code == requests.codes.ok:
                print("Submitted packet from '%s' successfully" % self.station_name)
            else:
                print("[ERROR] couldn't submit packet (%d): %s" % (r.status_code, r.text))

        except Exception as ex:
            print("[ERROR] couldn't submit packet: %s" % ex)






