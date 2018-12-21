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

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from qa_equisat_4fsk_block_decode import qa_equisat_4fsk_block_decode
import numpy as np

class qa_equisat_submitter (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_full_packet_route(self):
        data = qa_equisat_4fsk_block_decode.read_wave("../samples/4_equisat_packets_2nd_correct.wav")
        src = blocks.vector_source_f(data, repeat=False)
        preamble_detector = equisat_4fsk_preamble_detect(byte_buf_size=num_bytes)
        block_decoder = equisat_4fsk_block_decode(msg_size=num_bytes)
        dst = blocks.message_debug()
        self.tb.connect(src, preamble_detector)
        self.tb.msg_connect(preamble_detector, "out", block_decoder, "in")
        self.tb.msg_connect(block_decoder, "out", dst, "store")

        # Wait for all messages to be sent
        self.tb.start()
        while block_decoder.num_packets < num_packets:
            time.sleep(1.5)
        self.tb.stop()
        self.tb.wait()

        # may be more packets received than num_packets
        packets = []
        for i in range(dst.num_messages()):
            packets.append(pmt.u8vector_elements(pmt.cdr(dst.get_message(i))))
        return packets

if __name__ == '__main__':
    gr_unittest.run(qa_equisat_4fsk_preamble_detect, "qa_equisat_4fsk_preamble_detect.xml")
