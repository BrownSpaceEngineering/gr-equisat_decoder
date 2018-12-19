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

import numpy as np
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
    BSE_API_ROUTE = "api.brownspace.org/equisat/receive_raw"

    # minimum time between packet submits
    MIN_REQUEST_PERIOD = 1

    def __init__(self, station_name, api_key):
        gr.sync_block.__init__(self,
                               name="equisat_submitter",
                               in_sig=[],
                               out_sig=None)

        self.station_name = station_name
        self.api_key = api_key

        # since we have multiple inputs, keep queues and pop off sections
        # when we have a (corresponding) one of each (i.e. equal length queues)
        self.raw_queue = []
        self.corrected_queue = []

        self.message_port_register_in(pmt.intern('raw'))
        self.message_port_register_in(pmt.intern('corrected'))
        self.set_msg_handler(pmt.intern('in'), self.handle_raw_msg)

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
        jsn = {
            "raw": raw,
            "corrected": corrected,
            "station_name": self.station_name,
            "api_key": self.api_key
        }

        try:
            r = requests.post(self.BSE_API_ROUTE, json=jsn)
            if r.status_code != requests.codes.ok:
                print("[ERROR] couldn't submit packet (%d): %s" % (r.status_code, r.text))
        except Exception as ex:
            print("[ERROR] couldn't submit packet: %s" % ex)






