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

class xdl_micro_4fsk_decoder(gr.basic_block):
    """
    A GNU Radio block to decode the XDL Micro Radio
    operating in its 9600-baud 4FSK Transparent Mode
    (with FEC and scrambler disabled).

    Input must be the 4800 Hz 4FSK symbols (corresponding
    to four 4FSK frequencies, with no requirements on their
    absolute values)
    """
    # packet progress states
    ST_SEARCHING = 0 # searching for preamble or in incomplete preamble
    ST_IN_HEADER = 1 # past preamble but haven't gotten through header
    ST_IN_BLOCKS = 2 # waiting to fill block buffer from incoming

    # packet layout constants
    HEADER_LEN = 25 # symbols
    BLOCK_LEN = 80 # symbols
    # largest possible/smallest acceptable preamble length (for starting to parse packet)
    MAX_PREAMBLE_LEN = 184 # symbols
    MIN_PREAMBLE_LEN = 92 # symbols; must be mult of 4

    # packet/preamble detection constants
    # percentage of first symbol in pair that second must be within to be "the same"
    SYM_SIMILARITY_THRESH = 0.125

    def __init__(self):
        gr.basic_block.__init__(self,
            name="xdl_micro_4fsk_decoder",
            in_sig=[np.float32],
            out_sig=[np.uint32]) # only need one byte but GNU radio needs same input/output size

        # set enough history to be large enough to store a ful premable
        self.NEW_DATA_INDEX = self.MAX_PREAMBLE_LEN
        self.set_history(self.NEW_DATA_INDEX)

        # the current state in the sequence of reading a packet
        self.state = self.ST_SEARCHING
        # when in ST_IN_HEADER, this gives the # of SYMBOLS of header read so far
        self.header_syms_read = 0

        # the current input values of the +2 and -2 symbols
        self.high = 0
        self.low = 0

        # buffer to hold incoming block data for a single block
        self.block_buf = np.empty(self.BLOCK_LEN)
        self.block_buf_i = 0 # current index in buf
        self.decoded_blocks = 0 # number of blocks decoded


    def forecast(self, noutput_items, ninput_items_required):
        """ Called by GNU radio to determine how many input items must be
        delivered to produce a given number of output items.
        """
        # setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            # TODO: for each byte output we need
            ninput_items_required[i] = noutput_items

            # TODO: use set_output_multiple??


    def general_work(self, input_items, output_items):
        """ Called by GNU Radio on input stream """
        # NOTE: input_items always includes self.MAX_PREAMBLE_LEN "old" bytes
        # we've already read, and the rest are new (see set_history above)
        inpt = input_items[0]
        # finite state machine:
        if self.state is self.ST_SEARCHING:
            # if searching, check for start of preamble and
            # set up for start of packet if found
            maybe_preamble = inpt[:self.MAX_PREAMBLE_LEN]
            found, start, end, high, low = self.check_for_preamble(maybe_preamble)

            if found:
                # if preamble is found, setup packet state
                self.high = high
                self.low = low

                # then, skip header bytes and try to read the
                # first block after that


                # NOTE: because we check every time and bytes
                # are shifted in one at a time, TODO: is it?
                # we know the preamble is just aligned with the end


                self.header_syms_read = 0
                self.state = self.ST_IN_HEADER
                # (continue down to ST_IN_HEADER case)
            else:
                return 0

        if self.state == self.ST_IN_HEADER:
            # calculate the number of bytes that have been read since the end
            # of the preamble, including both the the old ones in the
            # historical part of the buffer and the new ones in the second half
            # i.e.:
            #                               V post_header_index
            # |<-self.self.NEW_DATA_INDEX->|<--rest of buffer----->|
            # |       |  preamble    | head|r |  block 0  ....     |
            #                        |<--->| self.header_syms_read
            #                        |<------>| self.HEADER_LEN
            post_header_index = self.NEW_DATA_INDEX + self.HEADER_LEN - self.header_syms_read
            if post_header_index < len(inpt):
                # if we have more than the header's worth of bytes,
                # we can start adding to the first block
                self.block_buf_i = 0
                self.decoded_blocks = 0
                out, at_end, self.block_buf_i = self.process_blocks(inpt[post_header_index:],
                                                                    self.block_buf, self.block_buf_i, self.high, self.low)

                if at_end:
                    # if we happen to get an entire packet in one buffer
                    self.state = self.ST_SEARCHING
                else:
                    # otherwise, continue reading blocks
                    self.state = self.ST_IN_BLOCKS

                output_items[0] = out
                return len(out)

            elif post_header_index == len(inpt):
                # if we just barely got the header,
                # start on the blocks immediately next time
                self.state = self.ST_IN_BLOCKS
                return 0

            else:
                # if we only got header bytes, wait for more  later
                self.state = self.ST_IN_HEADER
                self.header_syms_read += len(inpt) - self.NEW_DATA_INDEX # new bytes
                return 0

        elif self.state == self.ST_IN_BLOCKS:
            # process all _new_ data as blocks
            out, dec_blocks, self.block_buf_i = self.process_blocks(inpt[self.NEW_DATA_INDEX:],
                self.block_buf, self.block_buf_i, self.high, self.low)
            self.decoded_blocks += dec_blocks
            # TODO: just reset if we've exceeded a number of blocks
            # (later we'll figure out how to read the length from the header)
            if self.decoded_blocks > 350/18: # 350 bytes
                self.state = self.ST_SEARCHING

            output_items[0] = out
            return len(out)

        else: # revert
            assert False

    ### Premable handling ###

    @staticmethod
    def check_for_preamble(inpt, min_preamble_len=MIN_PREAMBLE_LEN,
        sym_sim_thresh=SYM_SIMILARITY_THRESH):
        """ Checks for a run of sets of 4 adjacent symbols resembling
        a preamble "cycle", i.e. -2 -2 +2 +2. Returns True if such a
        run of min_preamble_len symbols exists (min_preamble_len/4 such cycles).
        Returns whether one was found, its start and end index
        cycle, and the low and high value.
        """
        high_sum = 0
        low_sum = 0
        cycle_count = 0
        start = 0
        end = 0
        found_first = False
        i = 0
        while i < len(inpt)-4:
            if xdl_micro_4fsk_decoder.is_preamble_cycle(inpt, i, sym_sim_thresh):
                # (note start if first found)
                if not found_first:
                    start = i
                # add cycle and then jump to next
                cycle_count += 1
                # the low part comes first in the cycle (is_preamble_cycle enforces this)
                low_sum += inpt[i] + inpt[i+1]
                high_sum += inpt[i+2] + inpt[i+3]
                i += 4
                found_first = True
                # in case we're the end, use this cycle as the end
                # was incremented past last cycle, plus one to be start of next byte sequence (i.e. header)
                end = i+1

            elif found_first:
                # if we didn't find a cycle but we'd already found one,
                # we've reached the end of the possible preamble
                break
            else:
                # if we found nothing, continue stepping one at a time
                i += 1

        if 4*cycle_count < min_preamble_len: # num symbols
            # no valid preamble if insufficient cycles found
            return False, -1, -1, 0, 0
        else:
            # average ALL the +2s and -2s to get the high/low values
            # (two symbols per cycle)
            high = high_sum / (2 * cycle_count)
            low = low_sum / (2 * cycle_count)
            print(high, low)
            print(inpt[start:end])
            return True, start, end, high, low


    @staticmethod
    def is_preamble_cycle(inpt, i, sym_sim_thresh):
        """ Checks if the set of 4 raw values in inpt starting at i
        resemble a preamble cycle up to sim_thresh """
        pair1_close = abs(inpt[i] - inpt[i+1]) <= sym_sim_thresh * abs(inpt[i])
        pair2_close = abs(inpt[i+2] - inpt[i+3]) <= sym_sim_thresh * abs(inpt[i+2])
        pair1_avg = (inpt[i] + inpt[i+1]) / 2
        pair2_avg = (inpt[i+2] + inpt[i+3]) / 2
        return pair1_close and pair2_close and pair1_avg < 0 and pair2_avg > 0

    ### Block/packet handling ###

    @staticmethod
    def process_blocks(block_inpt, block_buf, block_buf_i, high, low, block_len=BLOCK_LEN):
        """ Adds data from the given input to the given block buffer
        (starting at the given index in the block buffer),
        decoding multiple blocks and producing output if necessary.
        Also checks based on symbols whether to terminate
        Returns any such data, the count of blocks decoded, and the new block_buf_i
        """
        out = np.empty((1, 18)) # decoded bytes per one block
        block_inpt_i = 0
        dec_blocks = 0
        # transfer remaining input into buffer until full for decoding
        while block_inpt_i < len(block_inpt):
            cur_block_remaining = block_len - block_buf_i
            block_inpt_remaining = len(block_inpt) - block_inpt_i
            if cur_block_remaining > block_inpt_remaining:
                # if we don't have enough to fill up the block,
                # fill up what we can and return
                block_buf[block_buf_i:(block_buf_i+block_inpt_remaining)] = block_inpt[block_inpt_i:]
                block_buf_i = block_buf_i+block_inpt_remaining
                block_inpt_i = len(block_inpt) # return now

            else:
                # if we still need to fill up some more before
                # decoding, do so
                if cur_block_remaining < block_inpt_remaining:
                    # if we can fill up a block, fill it up and then decode it
                    block_buf[block_buf_i:block_len] = block_inpt[block_inpt_i:(block_inpt_i+cur_block_remaining)]
                    block_inpt_i = block_inpt_i+cur_block_remaining

                np.append(out, xdl_micro_4fsk_decoder.decode_block_raw(block_buf, high, low))
                block_buf_i = 0

        return out, dec_blocks , block_buf_i

    @staticmethod
    def decode_block_raw(block_buf, high, low):
        """ Decodes the given block buffer of raw float data by converting
        into symbols and decoding, using the given high and low raw values
        corresponding to +2 and -2 symbols, respectively """
        syms = xdl_micro_4fsk_decoder.get_symbols(block_buf, high, low)
        return xdl_micro_4fsk_decoder.decode_block(syms)

    @staticmethod
    def get_symbols(inpt, high, low):
        """ Converts raw input values into numerical base-4 symbols, based
        on the given high value corresponding to +2 deviation and low to -2
        """
        # shift symbols from range [high, low] to range [2, -2]
        # and then threshold
        syms = np.zeros(len(inpt), dtype=np.uint8)
        syms = 4 * (syms - low) / high - 2
        for i in range(len(syms)):
            if syms[i] >= 1.5:
                syms[i] = 1
            elif syms[i] >= 0:
                syms[i] = 0
            elif syms[i] > -1.5:
                syms[i] = 2
            else:
                syms[i] = 3
        return syms

    @staticmethod
    def decode_block(in_syms):
        """ Decodes an 80-symbol long section by de-interleaving the sets of 8
        symbols distributed across 9 blocks (ignoring the 1 leading symbol
        of overhead per), and then de-interleaving 18 bytes (9 pairs) from
        8 sets of 9 symbols.
        """
        # de-interlace symbols
        symbols = np.zeros(72, dtype=np.uint8) # total symbols in 8*9 blocks
        # 8-symbol "blocks" in input correspond to 8-symbol sections in decoded symbols,
        # sections also correspond to (but don't align with) 2-byte output sections
        # k is block/symbol index, i is position/section index
        for k in range(8):
            for i in range(9):
                # ith position symbol in block k is actually the
                # kth position symbol in section i
                # (ignore symbol at start of block)
                symbols[i*8 + k] = in_syms[(k+1) + k*9 + i]

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
                sym = symbols[i*8 + k]
                sym_lsb = sym & 0b01
                sym_msb = (sym & 0b10) >> 1
                # treat MSB of symbol as first byte (i.e. left to right ordering,
                # NOT swapped/interlaced (again))
                # simultaneous conversion to byte-wise little endian (as expected by Python)
                byte1 |= sym_msb << (7-k)
                byte2 |= sym_lsb << (7-k)
            byts[2*i] = byte1
            byts[2*i+1] = byte2

        return byts
