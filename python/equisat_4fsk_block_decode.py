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
import array

class equisat_4fsk_block_decode(gr.basic_block):
    """
    Block de-interlacer and decoder for Brown Space Engineering's
    EQUiSat radio using a transparent 4FSK protocol.
    """

    # input block length in symbols
    SYMS_PER_BLOCK = 80
    # bytes per block (after decoding)
    BYTES_PER_BLOCK = 18

    def __init__(self, max_num_blocks):
        gr.basic_block.__init__(self,
            name="equisat_4fsk_block_decode",
            in_sig=[],
            out_sig=[])

        self.max_num_blocks = max_num_blocks

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)
        self.message_port_register_out(pmt.intern('out'))

        self.num_packets = 0

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return

        syms = np.array(pmt.u8vector_elements(msg), dtype='uint8')
        if len(syms) < self.BYTES_PER_BLOCK:
            # can't decode a partial block
            return

        decodable_blocks = len(syms)/self.SYMS_PER_BLOCK
        num_blocks = min(decodable_blocks, self.max_num_blocks)
        byts = np.zeros(self.BYTES_PER_BLOCK*num_blocks, dtype=np.uint8)

        for block in range(num_blocks):
            byts_i = block*self.BYTES_PER_BLOCK
            syms_i = block*self.SYMS_PER_BLOCK
            byts[byts_i:byts_i+self.BYTES_PER_BLOCK] = self.decode_block(syms[syms_i:syms_i+self.SYMS_PER_BLOCK])

        # ignore first 5 bytes of first block as these contain packet metadata
        byts_arr = array.array('B', byts[5:])
        print(self._bytearr_to_string(byts_arr))
        self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.car(msg_pmt), pmt.init_u8vector(len(byts_arr), byts_arr)))
        self.num_packets += 1

    @staticmethod
    def decode_block(in_syms):
        """ Decodes an 80-symbol long section by de-interleaving the sets of 8
        symbols distributed across 9 blocks (ignoring the 1 leading symbol
        of overhead per), and then de-interleaving 18 bytes (9 pairs) from
        8 sets of 9 symbols.
        """
        # de-interlace symbols
        symbols = np.zeros(72, dtype=np.uint8)  # total symbols in 8*9 blocks
        # 8-symbol "blocks" in input correspond to 8-symbol sections in decoded symbols,
        # sections also correspond to (but don't align with) 2-byte output sections
        # k is block/symbol index, i is position/section index
        for k in range(8):
            for i in range(9):
                # ith position symbol in block k is actually the
                # kth position symbol in section i
                # (ignore symbol at start of block)
                symbols[i * 8 + k] = in_syms[(k + 1) + k * 9 + i]

        # de-interlace bits from symbols (only interlaced per secion)
        byts = np.zeros(18)
        # i is section index, and we have 2 bytes per sections (though the bits/symbols
        # are not aligned because lcm(9, 8) = 72 =/= 8). They still map directly though.
        # Finally, k is same symbol index as before. Note k does not directly
        # correspond to the bit index by the above
        for i in range(9):
            byte1 = 0
            byte2 = 0
            for k in range(8):
                sym = symbols[i * 8 + k]
                sym_lsb = sym & 0b01
                sym_msb = (sym & 0b10) >> 1
                # treat MSB of symbol as first byte (i.e. left to right ordering,
                # NOT swapped/interlaced (again))
                # simultaneous conversion to byte-wise little endian (as expected by Python)
                byte1 |= sym_msb << (7 - k)
                byte2 |= sym_lsb << (7 - k)
            byts[2 * i] = byte1
            byts[2 * i + 1] = byte2

        return byts

    @staticmethod
    def _bytearr_to_string(byts):
        """ Converts a numpy array of integer byte-values to a string """
        chrs = [chr(int(c)) for c in byts]
        return "".join(chrs)