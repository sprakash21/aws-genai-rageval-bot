ARG PG_MAJOR=14.4
FROM postgres:$PG_MAJOR-alpine AS pgvector-builder
ARG PG_MAJOR
RUN apk add --no-cache git build-base clang llvm13-dev
WORKDIR /home
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
WORKDIR /home/pgvector
RUN make
RUN make install

FROM postgres:14.4-alpine
ENV USER_ID=2000
ENV GROUP_ID=2000
USER root
COPY --from=pgvector-builder /usr/local/lib/postgresql/bitcode/vector.index.bc /usr/local/lib/postgresql/bitcode/vector.index.bc
COPY --from=pgvector-builder /usr/local/lib/postgresql/vector.so /usr/local/lib/postgresql/vector.so
COPY --from=pgvector-builder /usr/local/share/postgresql/extension /usr/local/share/postgresql/extension
COPY ./pg_vector/init_db.sql /docker-entrypoint-initdb.d/
RUN apk add --no-cache shadow && \
    groupmod -g 2000 postgres && \
    usermod -u 2000 -g 2000 postgres

USER postgres