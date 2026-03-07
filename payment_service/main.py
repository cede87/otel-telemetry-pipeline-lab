"""Payment service that simulates a gateway call for distributed tracing."""

from __future__ import annotations

import logging
import random
import time
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .telemetry import get_meter, get_tracer, init_telemetry

# Initialize telemetry once at import time so instrumentation is ready before serving.
init_telemetry()

logger = logging.getLogger("payment-service")
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Metrics
request_counter = meter.create_counter(
    name="request_counter",
    description="Total number of HTTP requests",
    unit="1",
)

error_counter = meter.create_counter(
    name="error_counter",
    description="Total number of error responses",
    unit="1",
)

request_latency = meter.create_histogram(
    name="request_latency",
    description="Request latency in milliseconds",
    unit="ms",
)

app = FastAPI(title="Payment Service", version="0.1")

# Instrument FastAPI for automatic tracing. It extracts the incoming traceparent header.
FastAPIInstrumentor().instrument_app(app)


def _attrs(request: Request) -> Dict[str, str]:
    return {
        "http.method": request.method,
        "http.route": request.url.path,
    }


@app.post("/charge")
def charge(request: Request) -> Dict[str, str]:
    start = time.perf_counter()
    attrs = _attrs(request)

    with tracer.start_as_current_span("payment-handler") as span:
        logger.info("processing payment", extra={"route": "/charge"})
        span.add_event("processing payment")

        with tracer.start_as_current_span("payment.gateway.call") as gateway_span:
            sleep_s = random.uniform(0.1, 0.5)
            time.sleep(sleep_s)
            gateway_span.set_attribute("sleep_seconds", sleep_s)

        if random.random() < 0.1:
            error_counter.add(1, attrs)
            latency_ms = (time.perf_counter() - start) * 1000
            request_latency.record(latency_ms, attrs)
            logger.error("payment gateway error", extra={"route": "/charge"})
            raise HTTPException(status_code=502, detail="payment gateway error")

        span.add_event("payment completed")
        logger.info("payment completed", extra={"route": "/charge"})

    request_counter.add(1, attrs)
    latency_ms = (time.perf_counter() - start) * 1000
    request_latency.record(latency_ms, attrs)

    return {"status": "ok", "message": "payment processed"}
