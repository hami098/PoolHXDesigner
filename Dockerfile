FROM python:3.12-slim AS wheel_builder

WORKDIR /build

RUN pip install --no-cache-dir hatchling==1.32.4

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels .


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLET_FORCE_WEB_SERVER=true

RUN useradd --create-home --shell /usr/sbin/nologin designer \
    && mkdir -p /work/results \
    && chown -R designer:designer /work

WORKDIR /work

COPY requirements-lock.txt /tmp/requirements-lock.txt
COPY --from=wheel_builder /wheels /tmp/wheels

RUN set -eux; \
    built_wheel="$(ls /tmp/wheels/*.whl)"; \
    pip install --no-cache-dir \
        --constraint /tmp/requirements-lock.txt \
        "${built_wheel}[web-interface]"; \
    rm -rf /tmp/wheels /tmp/requirements-lock.txt; \
    pool-heat-exchanger-designer --help > /dev/null

COPY examples /work/examples

USER designer

EXPOSE 8550

ENTRYPOINT ["pool-heat-exchanger-designer"]
CMD ["gui", "--web", "--host", "0.0.0.0", "--port", "8550"]
