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

        parsed, errs = packetparse.parse_packet(packet)
        if len(errs) > 0:
            print("[WARNING] packet parsing errors (database will not accept packet): %s" % (", ".join(errs)))
        else:
            print("[INFO] no packet parsing errors")

        # remove non-useful info
        self.clean_parsed(parsed)

        # print one string to keep them together in terminal (many threads printing)
        out = "EQUiSat telemetry:\n" + yaml.dump(parsed, default_flow_style=False)
        print(out)

    @staticmethod
    def clean_parsed(parsed):
        if parsed is None:
            return

        if parsed.has_key("data"):
            dat = parsed["data"]
            if type(dat) == list:
                for i in range(len(dat)):
                    if dat[i].has_key("data_hash"):
                        del dat[i]["data_hash"]
            elif type(dat) == dict and dat.has_key("data_hash"):
                del dat["data_hash"]

        if parsed.has_key("errors"):
            errs = parsed["errors"]
            for i in range(len(errs)):
                if errs[i].has_key("data_hash"):
                    del errs[i]["data_hash"]

    @staticmethod
    def bytes_to_hex_str(byts):
        return binascii.hexlify(bytearray(byts))