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
import math
import array

class equisat_4fsk_block_decode(gr.basic_block):
    """
    Block de-interlacer and decoder for Brown Space Engineering's
    EQUiSat radio using a transparent 4FSK protocol.

    Requires msg_size argument, the size of the original transmitted message in bytes
    """

    # input block length in symbols
    SYMS_PER_BLOCK = 80
    # bytes per block (after decoding)
    BYTES_PER_BLOCK = 18
    # number of excess metadata bytes in the first block
    HEADER_BLOCK_BYTES = 5

    def __init__(self, msg_size, print_packets=False):
        gr.basic_block.__init__(self,
            name="equisat_4fsk_block_decode",
            in_sig=None,
            out_sig=None)

        self.msg_size = msg_size
        # need enough blocks to contain a complete message (including header bytes on front)
        self.total_num_blocks = self.get_required_num_blocks(msg_size)
        self.print_packets = print_packets

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

        decodable_blocks = len(syms)/self.SYMS_PER_BLOCK
        if decodable_blocks < self.total_num_blocks:
            # can't decode a partial block or a set of too few blocks
            print("[WARNING] Insufficient number of blocks provided; %d given but need %d for %d bytes" %
                  (decodable_blocks, self.total_num_blocks, self.msg_size))
            return

        num_blocks = min(decodable_blocks, self.total_num_blocks)
        byts = np.zeros(self.BYTES_PER_BLOCK*num_blocks, dtype=np.uint8)

        for block in range(num_blocks):
            byts_i = block*self.BYTES_PER_BLOCK
            syms_i = block*self.SYMS_PER_BLOCK
            byts[byts_i:byts_i+self.BYTES_PER_BLOCK] = self.decode_block(syms[syms_i:syms_i+self.SYMS_PER_BLOCK])

        # ignore first few bytes of first block as these contain packet metadata
        # cut off the rest to the requested length
        byts_arr = array.array('B', byts[self.HEADER_BLOCK_BYTES:self.HEADER_BLOCK_BYTES + self.msg_size])
        if self.print_packets:
            print(self._bytearr_to_string(byts_arr))

        self.message_port_pub(pmt.intern('out'), pmt.cons(pmt.get_PMT_NIL(), pmt.init_u8vector(len(byts_arr), byts_arr)))
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
    def get_required_num_blocks(num_bytes):
        """ Returns the quantity of blocks (including the header block) needed to hold num_bytes"""
        return int(math.ceil((equisat_4fsk_block_decode.HEADER_BLOCK_BYTES + num_bytes)
                         / float(equisat_4fsk_block_decode.BYTES_PER_BLOCK)))

    @staticmethod
    def _bytearr_to_string(byts):
        """ Converts a numpy array of integer byte-values to a string """
        chrs = [chr(int(c)) for c in byts]
        return "".join(chrs)