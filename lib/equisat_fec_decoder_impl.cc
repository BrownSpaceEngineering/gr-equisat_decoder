/* -*- c++ -*- */
/* 
 * Copyright 2018 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <algorithm>

#include <gnuradio/logger.h>

#include <gnuradio/io_signature.h>
#include "equisat_fec_decoder_impl.h"

extern "C" {
#include "rscode/ecc.h"
}

namespace gr {
  namespace equisat_decoder {

    equisat_fec_decoder::sptr
    equisat_fec_decoder::make()
    {
      return gnuradio::get_initial_sptr
        (new equisat_fec_decoder_impl());
    }

    /*
     * The private constructor
     */
    equisat_fec_decoder_impl::equisat_fec_decoder_impl()
      : gr::block("equisat_fec_decoder",
            gr::io_signature::make(0, 0, 0),
            gr::io_signature::make(0, 0, 0))
    {
        // initialize tables in rscode library
        initialize_ecc(NPAR);

        message_port_register_out(pmt::mp("out"));
        message_port_register_in(pmt::mp("in"));
        set_msg_handler(pmt::mp("in"),
              boost::bind(&equisat_fec_decoder_impl::msg_handler, this, _1));
    }

    /*
     * Our virtual destructor.
     */
    equisat_fec_decoder_impl::~equisat_fec_decoder_impl()
    {
    }

    void equisat_fec_decoder_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
    }

    int equisat_fec_decoder_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      return 0;
    }

    void equisat_fec_decoder_impl::msg_handler (pmt::pmt_t pmt_msg) {
        pmt::pmt_t msg = pmt::cdr(pmt_msg);
        size_t offset = 0; // for type reasons

        if (pmt::length(msg) < RAW_LEN) {
            std::cout << "Input vector was too small" << std::endl;
            return;
        }

        uint8_t data[RAW_LEN];
        memcpy(data, pmt::uniform_vector_elements(msg, offset), RAW_LEN);

        // extract the reed-solomon encoded section (past the 6-byte callsign)
        uint8_t* rs_data = data + CALLSIGN_LEN;

        // Reed-Solomon decoding
        decode_data(rs_data, RS_LEN);
        if (check_syndrome() != 0) {
            if (correct_errors_erasures(rs_data, RS_LEN, 0, NULL) != 1) {
                std::cout << "Reed-Solomon decoding failed\n" << std::endl;
                return;
            } else {
                std::cout << "Reed-Solomon corrected errors\n" << std::endl;
            }
        } else {
            std::cout << "Reed-Solomon found no errors\n" << std::endl;
        }

        // Add the original raw data (and omitted callsign specifically)
        // to the car of the pmt message
        pmt::pmt_t dict = pmt::make_dict();
        dict = pmt::dict_add(dict, pmt::intern("raw"), pmt::init_u8vector(RAW_LEN,
            (uint8_t*) pmt::uniform_vector_elements(msg, offset)));

        // Add back callsign, remove parity bytes, and send message
        uint8_t corrected[CALLSIGN_LEN + RS_LEN - NPAR];
        memcpy(corrected, data, CALLSIGN_LEN);
        memcpy(corrected + CALLSIGN_LEN, rs_data, RS_LEN - NPAR);
        message_port_pub(pmt::mp("out"),
                         pmt::cons(dict,
                                   pmt::init_u8vector(CALLSIGN_LEN + RS_LEN - NPAR, corrected)));
    }
  } /* namespace equisat_decoder */
} /* namespace gr */

