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
    HEADER_LEN = 22 # symbols
    BLOCK_LEN = 80 # symbols
    # largest possible/smallest acceptable preamble length (for starting to parse packet)
    MAX_PREAMBLE_LEN = 185 # symbols
    MIN_PREAMBLE_LEN = 92 # symbols; must be mult of 4

    # packet/preamble detection constants
    # percentage of first symbol in pair that second must be within to be "the same"
    SYM_SIMILARITY_THRESH = 0.33

    def __init__(self):
        gr.basic_block.__init__(self,
            name="xdl_micro_4fsk_decoder",
            in_sig=[np.float32],
            out_sig=[np.uint32]) # only need one byte but GNU radio needs same input/output size

        # set enough history to be large enough to store a ful premable
        self.NUM_OLD_DATA = self.MAX_PREAMBLE_LEN
        self.set_history(self.NUM_OLD_DATA)

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
        self.num_decoded_blocks = 0 # number of blocks decoded


    def forecast(self, noutput_items, ninput_items_required):
        """ Called by GNU radio to determine how many input items must be
        delivered to produce a given number of output items.
        """
        # TODO: just a rough estimate; it takes 80 symbols for 18 bytes
        ninput_items_required[0] = (1887*noutput_items)/356 #self.MAX_PREAMBLE_LEN + self.HEADER_LEN + (80*noutput_items)/(18*noutput_items)
        # TODO: use set_output_multiple??

    def general_work(self, input_items, output_items):
        """ Called by GNU Radio with input stream """
        # NOTE: input_items always includes self.NUM_OLD_DATA "old" bytes
        # we've already read, and the rest are new (see set_history above)
        inpt = input_items[0]

        # finite state machine, with the ability to possibly transition through
        # all states in one iteration (if we get a full packet in inpt)
        start_i = self.NUM_OLD_DATA-1 # where current state should start in input
        if self.state is self.ST_SEARCHING:
            # reset state variables when we start searching
            self.header_syms_read = 0
            self.num_decoded_blocks = 0
            self.block_buf_i = 0

            # if searching, check for start of preamble in the HISTORY and
            # set up for start of packet if found
            found, start, end, high, low = self.check_for_preamble(inpt)
            if found:
                # if preamble is found, setup packet state
                self.high = high
                self.low = low

                # now, try and start reading the header (reset start_i to wherever the preamble ended)
                # note this should never be smaller than self.NEW_DATA_INDEX, so start_i will be increasing
                self.state = self.ST_IN_HEADER
                start_i = end
                # continue down into ST_IN_HEADER case (it'll check if there's data on the header)
            else:
                return 0

        if self.state == self.ST_IN_HEADER:
            # reset our buffer to be just that after preamble (if the preamble was in this input)
            rem = inpt[start_i:]
            # check if the new data is enough to complete the header
            header_remaining = self.HEADER_LEN - self.header_syms_read
            if len(rem) >= header_remaining:
                # move onto blocks, starting past end of header
                self.state = self.ST_IN_BLOCKS
                start_i += header_remaining
            else:
                # state is still ST_IN_HEADER, just note we read some more
                self.header_syms_read += len(rem)
                return 0

        if self.state == self.ST_IN_BLOCKS:
            # just reset if we've exceeded a number of blocks
            # TODO: later we'll figure out how to read the length from the header
            max_blocks = 350/18 # 350 bytes = 19.4 = 20 blocks

            # process all new/remaining data as blocks (we may have read both header and preamble out of this)
            rem = inpt[start_i:]
            out, dec_blocks, self.block_buf_i = self.process_blocks(rem,
                self.block_buf, self.block_buf_i, max_blocks, self.high, self.low)

            # in the special case of the first block, ignore the first 5 bytes (these are apparently overhead)
            if self.num_decoded_blocks == 0 and len(out) > 5:
                out = out[5:]

            self.num_decoded_blocks += dec_blocks
            if self.num_decoded_blocks > max_blocks:
                self.state = self.ST_SEARCHING

            output_items[0] = out
            print(xdl_micro_4fsk_decoder._bytearr_to_string(out))
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
            if xdl_micro_4fsk_decoder._is_preamble_cycle(inpt, i, sym_sim_thresh):
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
            return True, start, end, high, low


    @staticmethod
    def _is_preamble_cycle(inpt, i, sym_sim_thresh):
        """ Checks if the set of 4 raw values in inpt starting at i
        resemble a preamble cycle up to sim_thresh """
        pair1_close = abs(inpt[i] - inpt[i+1]) <= sym_sim_thresh * abs(inpt[i])
        pair2_close = abs(inpt[i+2] - inpt[i+3]) <= sym_sim_thresh * abs(inpt[i+2])
        pair1_avg = (inpt[i] + inpt[i+1]) / 2
        pair2_avg = (inpt[i+2] + inpt[i+3]) / 2
        return pair1_close and pair2_close and pair1_avg < 0 and pair2_avg > 0

    ### Block/packet handling ###

    @staticmethod
    def process_blocks(block_inpt, block_buf, block_buf_i, max_blocks, high, low):
        """ Adds data from the given input to the given block buffer
        (starting at the given index in the block buffer),
        decoding multiple blocks (up to max_blocks) and producing output if necessary.
        Also checks based on symbols whether to terminate
        Returns any such data, the count of blocks decoded, and the new block_buf_i
        """
        out = np.empty(0) # decoded bytes per one block
        dec_blocks = 0
        inpt_rem = block_inpt

        # keep filling buffer until we either run out of input
        # or decode the maximum number of blocks
        while len(inpt_rem) > 0 and dec_blocks <= max_blocks:
            full, num_filled = xdl_micro_4fsk_decoder._fill_buf(block_buf, block_buf_i, inpt_rem)
            block_buf_i = (block_buf_i + num_filled) % len(block_buf)
            inpt_rem = inpt_rem[num_filled:]
            # if we've filled the buffer (and are not doing it for the last time after having
            # maxed out our block count), then decode the data
            if full:
                # if we successfully got a complete block, decode it
                block_out = xdl_micro_4fsk_decoder.decode_block_raw(block_buf, high, low)
                out = np.append(out, block_out)
                dec_blocks += 1

        return out, dec_blocks, block_buf_i

    @staticmethod
    def _fill_buf(buf, buf_i, inpt):
        """ Fills as much of the given numpy buffer from inpt, starting at buf_i in the buffer.
        Returns whether the buffer was filled and how many elements from input were used
        """
        buf_remaining = len(buf) - buf_i
        inpt_remaining = len(inpt)
        if inpt_remaining < buf_remaining:
            # if we don't have enough to fill up the buffer, fill up what we can
            buf[buf_i:(buf_i + inpt_remaining)] = inpt
            return False, inpt_remaining
        else:
            # otherwise, if we can at least fill up the current block, do so
            buf[buf_i:] = inpt[0:buf_remaining]
            return True, buf_remaining

    @staticmethod
    def decode_block_raw(block_buf, high, low):
        """ Decodes the given block buffer of raw float data by converting
        into symbols and decoding, using the given high and low raw values
        corresponding to +2 and -2 symbols, respectively """
        syms = xdl_micro_4fsk_decoder.get_symbols(block_buf, high, low)
        return xdl_micro_4fsk_decoder.decode_block(syms)

    @staticmethod
    def get_symbols(inpt, high, low):
        """ Converts raw input values in a numpy array into numerical base-4 symbols,
        based on the given high value corresponding to +2 deviation and low to -2
        """
        # shift symbols from range [high, low] to range [1, -1]
        # and then threshold
        syms = 2 * (inpt - low) / float(high - low) - 1
        for i in range(len(syms)):
            if syms[i] >= 0.75:
                syms[i] = 1
            elif syms[i] >= 0.0:
                syms[i] = 0
            elif syms[i] > -0.75:
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

    @staticmethod
    def _bytearr_to_string(byts):
        """ Converts a numpy array of integer byte-values to a string """
        chrs = [chr(int(c)) for c in byts]
        return "".join(chrs)