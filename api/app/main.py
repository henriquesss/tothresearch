from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(title="Toth Research API")


app = create_app()
