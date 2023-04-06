#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
from fastapi import FastAPI, Request, Response

from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from opencensus.trace.span import SpanKind
from opencensus.trace.attributes_helper import COMMON_ATTRIBUTES

from serve import entrypoint
from .about import generate_about_json
from .azure_logging import initialize_logging, disable_unwanted_loggers


logger = logging.getLogger(__name__)

HTTP_URL = COMMON_ATTRIBUTES['HTTP_URL']
HTTP_STATUS_CODE = COMMON_ATTRIBUTES['HTTP_STATUS_CODE']

# create fastapi app
app = FastAPI()

@app.on_event("startup")
async def initialize_logging_on_startup():
    initialize_logging(logging.INFO)
    disable_unwanted_loggers()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next) -> Response:
    
    # picks up APPLICATIONINSIGHTS_CONNECTION_STRING automatically
    tracer = Tracer(exporter=AzureExporter(sampler=ProbabilitySampler(1.0)))
    with tracer.span("main") as span:
        span.span_kind = SpanKind.SERVER
            
        response = await call_next(request)

        tracer.add_attribute_to_current_span(
                attribute_key=HTTP_STATUS_CODE,
                attribute_value=response.status_code)
        tracer.add_attribute_to_current_span(
            attribute_key=HTTP_URL,
            attribute_value=str(request.url))
        
    return response


@app.get("/")
def root():
    logging.info("Root endpoint called")
    return generate_about_json()


@app.get("/run")
def run(rawdata: dict = None):
    logging.info("Run endpoint called")
    return entrypoint.run(rawdata)
