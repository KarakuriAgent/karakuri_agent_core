FROM ubuntu:24.10
SHELL ["/bin/bash", "-c"]

# ホストのUIDとGID（適宜置き換える）
# ARG HOST_UID=1000
# ARG HOST_GID=1000
ARG FLUTTER_CHANNEL=stable
ARG FLUTTER_VERSION=3.24.5
ARG ANDROID_COMMANDLINE_TOOL_VERSION=11076708
ARG ANDROID_BUILD_TOOLS_VERSION=33.0.1
ARG ANDROID_PLATFORMS_VERSION=android-34

USER root

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y curl git unzip xz-utils zip libglu1-mesa wget tar
# develop Linux apps
RUN apt-get install -y clang cmake git ninja-build pkg-config libgtk-3-dev liblzma-dev libstdc++-12-dev
# develop Android apps
RUN apt-get install openjdk-17-jdk -y && update-java-alternatives --set java-1.17.0-openjdk-amd64
# develop Web apps
RUN apt-get install nodejs npm -y

# ユーザーとグループのUIDとGIDをホストのものに変更
# RUN groupmod -g ${HOST_GID} ubuntu \
#     && usermod -u ${HOST_UID} -g ${HOST_GID} ubuntu \
#     && chown -R ${HOST_UID}:${HOST_GID} /home/ubuntu

USER ubuntu

# Install Flutter sdk
ENV FLUTTER_HOME=~/flutter
RUN cd ~ \
    && wget https://storage.googleapis.com/flutter_infra_release/releases/${FLUTTER_CHANNEL}/linux/flutter_linux_${FLUTTER_VERSION}-${FLUTTER_CHANNEL}.tar.xz \
    && tar -xvf flutter*.tar.xz \
    && rm -f flutter*.tar.xz
RUN ~/flutter/bin/flutter precache

# add Flutter PATH
ENV PATH="/home/ubuntu/flutter/bin:${PATH}"
RUN chmod -R 755 ~/flutter/bin

# Install AndroidSDK
ENV ANDROID_HOME=/home/ubuntu/android-sdk
RUN wget -O /home/ubuntu/android-sdk.zip https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_COMMANDLINE_TOOL_VERSION}_latest.zip
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && unzip -q /home/ubuntu/android-sdk.zip -d ${ANDROID_HOME}/cmdline-tools/
RUN rm -rf /home/ubuntu/android-sdk.zip
RUN mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest
RUN yes | ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager --licenses
RUN ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager "tools" "platform-tools" "build-tools;${ANDROID_BUILD_TOOLS_VERSION}" "platforms;${ANDROID_PLATFORMS_VERSION}"

# add Android PATH
ENV PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/tools:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}:${PATH}"
