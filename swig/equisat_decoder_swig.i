/* -*- c++ -*- */

#define EQUISAT_DECODER_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "equisat_decoder_swig_doc.i"

%{
#include "equisat_decoder/equisat_fec_decoder.h"
%}


%include "equisat_decoder/equisat_fec_decoder.h"
GR_SWIG_BLOCK_MAGIC2(equisat_decoder, equisat_fec_decoder);
