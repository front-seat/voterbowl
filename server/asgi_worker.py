# See https://github.com/encode/uvicorn/issues/709#issuecomment-653456209

from uvicorn.workers import UvicornWorker


class NoLifespanUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {**UvicornWorker.CONFIG_KWARGS, "lifespan": "off"}
