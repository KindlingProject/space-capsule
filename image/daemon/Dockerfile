FROM debian:buster-slim

ENV CHAOSBLADE_HOME=/opt/chaosblades
COPY chaosblade-1.5.0 /opt/chaosblade
ENV PATH=/opt/chaosblade:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN curl -L https://github.com/chaos-mesh/toda/releases/download/v0.2.2/toda-linux-amd64.tar.gz | tar xz -C /usr/local/bin

RUN case "$TARGET_PLATFORM" in \
    'amd64') \
    export NSEXEC_ARCH='x86_64'; \
    ;; \
    'arm64') \
    export NSEXEC_ARCH='aarch64'; \
    ;; \
    *) echo >&2 "error: unsupported architecture '$TARGET_PLATFORM'"; exit 1 ;; \
    esac; \
    curl -L https://github.com/chaos-mesh/nsexec/releases/download/v0.1.6/nsexec-$NSEXEC_ARCH-unknown-linux-gnu.tar.gz | tar xz -C /usr/local/bin; \
    mv /usr/local/bin/libnsenter.so /usr/local/lib/libnsenter.so;

COPY iolatency /opt/iolatency

CMD ["sh", "-c", "tail -f /dev/null"]