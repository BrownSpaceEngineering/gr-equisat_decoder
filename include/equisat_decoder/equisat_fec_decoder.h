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


#ifndef INCLUDED_EQUISAT_DECODER_EQUISAT_FEC_DECODER_H
#define INCLUDED_EQUISAT_DECODER_EQUISAT_FEC_DECODER_H

#include <equisat_decoder/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace equisat_decoder {

    /*!
     * \brief <+description of block+>
     * \ingroup equisat_decoder
     *
     */
    class EQUISAT_DECODER_API equisat_fec_decoder : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<equisat_fec_decoder> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of equisat_decoder::equisat_fec_decoder.
       *
       * To avoid accidental use of raw pointers, equisat_decoder::equisat_fec_decoder's
       * constructor is in a private implementation
       * class. equisat_decoder::equisat_fec_decoder::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace equisat_decoder
} // namespace gr

#endif /* INCLUDED_EQUISAT_DECODER_EQUISAT_FEC_DECODER_H */

