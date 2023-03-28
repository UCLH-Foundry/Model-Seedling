# basic FastAPI implementation
from fastapi import FastAPI
from serve import entrypoint
from .about import generate_about_json

app = FastAPI()

@app.get("/")
def root():
    return generate_about_json()

@app.get("/run")
def run(rawdata: dict = None):
    return entrypoint.run(rawdata)
