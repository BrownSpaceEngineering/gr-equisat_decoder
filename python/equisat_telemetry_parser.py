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
import packetparse
import yaml
import binascii

class equisat_telemetry_parser(gr.basic_block):
    """
    Parser block for EQUiSat telemetry
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="equisat_telemetry_parser",
            in_sig=[],
            out_sig=[])

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return

        packet = self.bytes_to_hex_str(pmt.u8vector_elements(msg))

        try:
            parsed, err = packetparse.parse_packet(packet)
            if err is not None:
                print("[ERROR] packet parsing failed: %s" % err)
                return
        except ValueError or KeyError as e:
            print("[ERROR] packet parsing errored: %s", e)
            return

        print("EQUiSat telemetry:")
        print(yaml.dump(parsed, default_flow_style=False))

    @staticmethod
    def bytes_to_hex_str(byts):
        return binascii.hexlify(bytearray(byts))