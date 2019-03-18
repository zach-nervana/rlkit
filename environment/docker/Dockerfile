# We need the CUDA base dockerfile to enable GPU rendering
# on hosts with GPUs.
# The image below is a pinned version of nvidia/cuda:9.1-cudnn7-devel-ubuntu16.04 (from Jan 2018)
# If updating the base image, be sure to test on GPU since it has broken in the past.
FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04


RUN apt-get update -q \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    git \
    libgl1-mesa-dev \
    libgl1-mesa-glx \
    libglew-dev \
    libosmesa6-dev \
    software-properties-common \
    net-tools \
    unzip \
    vim \
    virtualenv \
    wget \
    xpra \
    xserver-xorg-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN DEBIAN_FRONTEND=noninteractive add-apt-repository --yes ppa:deadsnakes/ppa && apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install --yes python3.5-dev python3.5 python3-pip
RUN virtualenv --python=python3.5 env

RUN rm /usr/bin/python
RUN ln -s /env/bin/python3.5 /usr/bin/python
RUN ln -s /env/bin/pip3.5 /usr/bin/pip
RUN ln -s /env/bin/pytest /usr/bin/pytest

RUN curl -o /usr/local/bin/patchelf https://s3-us-west-2.amazonaws.com/openai-sci-artifacts/manual-builds/patchelf_0.9_amd64.elf \
    && chmod +x /usr/local/bin/patchelf

ENV LANG C.UTF-8

RUN mkdir -p /root/.mujoco \
    && wget https://www.roboti.us/download/mjpro150_linux.zip -O mujoco.zip \
    && unzip mujoco.zip -d /root/.mujoco \
    && rm mujoco.zip
COPY mjkey.txt /root/.mujoco/
ENV LD_LIBRARY_PATH /root/.mujoco/mjpro150/bin:${LD_LIBRARY_PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib64:${LD_LIBRARY_PATH}

COPY environment/docker/vendor/Xdummy /usr/local/bin/Xdummy
RUN chmod +x /usr/local/bin/Xdummy

# Workaround for https://bugs.launchpad.net/ubuntu/+source/nvidia-graphics-drivers-375/+bug/1674677
COPY environment/docker/vendor/10_nvidia.json /usr/share/glvnd/egl_vendor.d/10_nvidia.json

RUN apt-get update && apt-get install -y libav-tools

# For some reason this works despite an error showing up...
# don't install when using kubernetes
# RUN DEBIAN_FRONTEND=noninteractive apt-get -qy install nvidia-384; exit 0
# ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/lib/nvidia-384

RUN mkdir /root/code
WORKDIR /root/code

# For atari-py
RUN mkdir /usr/lib/nvidia
RUN apt-get install -y zlib1g-dev swig cmake

# Previous versions installed from a requirements.txt, but direct pip
# install seems cleaner
RUN pip install --no-cache-dir \
      glfw>=1.4.0 \
      numpy>=1.11 \
      Cython>=0.27.2 \
      imageio>=2.1.2 \
      cffi>=1.10 \
      imagehash>=3.4 \
      ipdb \
      Pillow>=4.0.0 \
      pycparser>=2.17.0 \
      pytest>=3.0.5 \
      pytest-instafail==0.3.0 \
      scipy>=0.18.0 \
      sphinx \
      sphinx_rtd_theme \
      numpydoc \
      cloudpickle==0.5.2 \
      cached-property==1.3.1 \
      gym[all]==0.10.5 \
      gitpython==2.1.7 \
      gtimer==1.0.0b5 \
      awscli==1.11.179 \
      boto3==1.4.8 \
      ray==0.2.2 \
      path.py==10.3.1 \
      http://download.pytorch.org/whl/cu90/torch-0.4.1-cp35-cp35m-linux_x86_64.whl \
      joblib==0.9.4 \
      opencv-python==3.4.0.12 \
      torchvision==0.2.0 \
      sk-video==1.1.10 \
      git+https://github.com/zach-nervana/multiworld.git \
      pygame

COPY . /root/code
RUN pip install -e .
