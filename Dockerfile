FROM dorowu/ubuntu-desktop-lxde-vnc:bionic
ARG DECODER_DIR=/root/gr-equisat_decoder/

# install GNU Radio
RUN add-apt-repository -y ppa:gnuradio/gnuradio-releases-3.7 \
    && apt-get install -y gnuradio

# install library and build tools
RUN apt-get install -y python-pip cmake swig

# install Python dependencies
COPY requirements.txt ${DECODER_DIR}
WORKDIR ${DECODER_DIR}
RUN pip install -r requirements.txt

# do this yourself; running it here messes with caching:
# RUN git submodule update --init --recursive

# cmake build and install
# copy only what CMake needs (notably excluding most stuff in apps/)
COPY CMakeLists.txt ${DECODER_DIR}
COPY apps/CMakeLists.txt ${DECODER_DIR}/apps/
COPY cmake      ${DECODER_DIR}/cmake 
COPY docs       ${DECODER_DIR}/docs 
COPY grc        ${DECODER_DIR}/grc 
COPY include    ${DECODER_DIR}/include 
COPY lib        ${DECODER_DIR}/lib 
COPY python     ${DECODER_DIR}/python 
COPY swig       ${DECODER_DIR}/swig

RUN mkdir build \
    && cd build \
    # default prefix is /usr/local which doesn't match this image
    && cmake -DCMAKE_INSTALL_PREFIX=/usr .. \
    && make \
    && make install \
    && ldconfig

# add shortcut to GNU Radio Companion
RUN mkdir /root/Desktop \
    && printf "[Desktop Entry]\nType=Application\nName=GNU Radio Companion\nExec=gnuradio-companion %%F" > /root/Desktop/grc.desktop

VOLUME apps/

# keep entrypoint of root image