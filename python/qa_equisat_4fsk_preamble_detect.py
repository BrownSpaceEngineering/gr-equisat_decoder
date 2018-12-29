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
from equisat_4fsk_preamble_detect import equisat_4fsk_preamble_detect
import qa_equisat_4fsk_block_decode
import numpy as np

packet_raw_EQUiSatx50 = qa_equisat_4fsk_block_decode.packet_raw_EQUiSatx50

class qa_equisat_4fsk_preamble_detect (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_is_preamble_cycle(self):
        self.assertFalse(equisat_4fsk_preamble_detect._is_preamble_cycle([0, 0, 0, 0], 0, 0.1))
        self.assertTrue(equisat_4fsk_preamble_detect._is_preamble_cycle([-1, -1, 1, 1], 0, 0.1))
        self.assertTrue(equisat_4fsk_preamble_detect._is_preamble_cycle([-1000, -900, 100, 101], 0, 0.1))
        self.assertFalse(equisat_4fsk_preamble_detect._is_preamble_cycle([-1000, -900, 900, 1000], 0, 0.01))
        self.assertFalse(equisat_4fsk_preamble_detect._is_preamble_cycle([-1000, -900, 900, 1000], 0, 0.1))

    def test_check_for_preamble(self):
        inpt = [0]*equisat_4fsk_preamble_detect.MAX_PREAMBLE_LEN
        found, start, end, high, low = equisat_4fsk_preamble_detect.check_for_preamble(inpt)
        self.assertFalse(found)

        found, start, end, high, low = equisat_4fsk_preamble_detect.check_for_preamble(
            [0, 0.1, -0.1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, 1, 0, -1], 12, 0.1)
        self.assertTrue(found)
        self.assertEqual(start, 3)
        self.assertEqual(end, 15)
        self.assertEqual(high, 1)
        self.assertEqual(low, -1)

        inpt = np.array(packet_raw_EQUiSatx50)
        found, start, end, high, low = equisat_4fsk_preamble_detect.check_for_preamble(inpt)
        self.assertTrue(found)
        self.assertEqual(start, 9)
        self.assertEqual(end, 193)
        self.assertAlmostEqual(high, 9200, delta=100)
        self.assertAlmostEqual(low, -9500, delta=100)

        # TODO: test multiple preambles, with bad ones initially

    def test_get_symbols(self):
        # note: +2 = 1, +1 = 0, -1 = 2, -2 = 3
        high = 200 # avg +1 = 104 => +1 cutoff = 152.5
        low = -180 # avg -1 = -85 => -1 cutoff = -132.5
        inpt = np.array([-173, 212, 30, -60, 153, -300, -110, -132.6, 20])
        exp_syms = [3, 1, 0, 2, 1, 3, 2, 3, 0]
        syms = equisat_4fsk_preamble_detect.get_symbols(inpt, high, low)
        self.assertFloatTuplesAlmostEqual(syms, exp_syms)

    def test_buffer_splits(self):
        hist_len = equisat_4fsk_preamble_detect.HISTORY_LEN
        min_pre_len = equisat_4fsk_preamble_detect.DEF_MIN_PREAMBLE_LEN
        st_preamble = equisat_4fsk_preamble_detect.ST_WAIT_FOR_PREAMBLE
        st_frame_sync = equisat_4fsk_preamble_detect.ST_IN_FRAME_SYNC
        hist_fill = [0]*equisat_4fsk_preamble_detect.HISTORY_LEN

        self.buffer_splits_helper([], 0, st_preamble)
        self.buffer_splits_helper([-1, -1, 1, 1], 0, st_preamble)
        self.buffer_splits_helper(hist_fill, 0, st_preamble)
        # consumes preamble section
        self.buffer_splits_helper(hist_fill + [-1, -1, 1, 1], 4, st_preamble)
        # consumes random stuff
        self.buffer_splits_helper(hist_fill + [1, -1, 1, -1], 4, st_preamble)
        # skips perfectly aligned preamble
        self.buffer_splits_helper([-1, -1, 1, 1] * (hist_len / 4), 0, st_preamble)
        # consumes complete aligned preamble
        self.buffer_splits_helper([-1, -1, 1, 1] * (hist_len / 4) + [1, -1, 1, -1, 1], 0, st_frame_sync)
        # consumes longer preamble
        self.buffer_splits_helper([-1, -1, 1, 1] * (hist_len / 4 + 2) + [1, -1, 1, -1, 1], 8, st_frame_sync)
        # consumes shorter preamble
        self.buffer_splits_helper([-1, -1, 1, 1] * (min_pre_len / 4) + [1, -1, 1, -1] * ((hist_len - min_pre_len) / 4), 0, st_frame_sync)
        # consumes preambles split across history boundary
        self.buffer_splits_helper([1, -1, 1, -1, 1] + [-1, -1, 1, 1] * (hist_len / 4 + 2) + [1, -1, 1, -1, 1], 5+8, st_frame_sync)
        self.buffer_splits_helper([1, -1, 1, -1, 1] + [1, -1, 1, -1] * ((hist_len - min_pre_len) / 4) + [-1, -1, 1, 1] * (min_pre_len / 4) + [1, -1, 1, -1, 1], 5, st_frame_sync)
        # consumes preambles past history
        self.buffer_splits_helper(hist_fill + [-1, -1, 1, 1] * (min_pre_len / 4) + [1, -1, 1, -1, 1], min_pre_len, st_frame_sync)
        self.buffer_splits_helper(hist_fill + [1, -1, 1, -1, 1] + [-1, -1, 1, 1] * (min_pre_len / 4) + [1, -1, 1, -1, 1], 5+min_pre_len, st_frame_sync)

    def buffer_splits_helper(self, inpt, expected_consumed, new_state):
        block = equisat_4fsk_preamble_detect(byte_buf_size=255)

        # hacky substitute for consume so we can test what it's called with
        def consume_test(index, num):
            self.assertEqual(expected_consumed, num)

        block.consume = consume_test
        block.general_work([inpt], None)
        self.assertEqual(new_state, block.state)


if __name__ == '__main__':
    gr_unittest.run(qa_equisat_4fsk_preamble_detect, "qa_equisat_4fsk_preamble_detect.xml")
