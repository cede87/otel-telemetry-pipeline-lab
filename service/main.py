"""FastAPI service that emits traces, metrics, and logs for experimentation."""

from __future__ import annotations

import logging
import random
import time
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, Request
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from .telemetry import get_meter, get_tracer, init_telemetry

# Initialize telemetry once at import time so instrumentation is ready before serving.
init_telemetry()

logger = logging.getLogger("telemetry-lab")
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

app = FastAPI(title="Telemetry Lab Service", version="0.1")

# Instrument FastAPI for automatic tracing
FastAPIInstrumentor().instrument_app(app)
# Instrument HTTPX so it propagates the W3C traceparent header on outbound calls.
HTTPXClientInstrumentor().instrument()


def _attrs(request: Request) -> Dict[str, str]:
    # Attributes let us slice metrics by endpoint and method.
    return {
        "http.method": request.method,
        "http.route": request.url.path,
    }


@app.get("/fast")
def fast(request: Request) -> Dict[str, str]:
    start = time.perf_counter()
    attrs = _attrs(request)

    with tracer.start_as_current_span("fast-handler") as span:
        span.set_attribute("handler.kind", "fast")
        # Simulate an internal step
        with tracer.start_as_current_span("fast.internal.compute"):
            _ = sum([1, 2, 3])

    request_counter.add(1, attrs)
    latency_ms = (time.perf_counter() - start) * 1000
    request_latency.record(latency_ms, attrs)

    logger.info("fast response", extra={"route": "/fast"})
    return {"status": "ok", "endpoint": "/fast"}


@app.get("/slow")
def slow(request: Request) -> Dict[str, str]:
    start = time.perf_counter()
    attrs = _attrs(request)

    with tracer.start_as_current_span("slow-handler") as span:
        span.set_attribute("handler.kind", "slow")
        # Simulate slow processing with a child span
        with tracer.start_as_current_span("slow.internal.sleep"):
            sleep_s = random.uniform(0.2, 1.5)
            time.sleep(sleep_s)
            span.set_attribute("sleep_seconds", sleep_s)

    request_counter.add(1, attrs)
    latency_ms = (time.perf_counter() - start) * 1000
    request_latency.record(latency_ms, attrs)

    logger.info("slow response", extra={"route": "/slow", "latency_ms": latency_ms})
    return {"status": "ok", "endpoint": "/slow", "latency_ms": round(latency_ms, 2)}


@app.get("/error")
def error(request: Request) -> Dict[str, str]:
    start = time.perf_counter()
    attrs = _attrs(request)

    with tracer.start_as_current_span("error-handler") as span:
        span.set_attribute("handler.kind", "error")
        # Simulate a flaky dependency
        with tracer.start_as_current_span("error.internal.random"):
            fail = random.random() < 0.3
            span.set_attribute("error.random_failure", fail)

        if fail:
            error_counter.add(1, attrs)
            latency_ms = (time.perf_counter() - start) * 1000
            request_latency.record(latency_ms, attrs)
            logger.error("simulated error", extra={"route": "/error"})
            raise HTTPException(status_code=500, detail="simulated error")

    request_counter.add(1, attrs)
    latency_ms = (time.perf_counter() - start) * 1000
    request_latency.record(latency_ms, attrs)
    logger.info("error endpoint succeeded", extra={"route": "/error"})
    return {"status": "ok", "endpoint": "/error"}


@app.post("/checkout")
def checkout(request: Request, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    start = time.perf_counter()
    attrs = _attrs(request)

    with tracer.start_as_current_span("checkout-handler"):
        logger.info("calling payment service", extra={"route": "/checkout"})
        # HTTPX instrumentation injects the traceparent header here to propagate context.
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.post(
                    "http://payment-service:8000/charge", json=payload or {}
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            error_counter.add(1, attrs)
            latency_ms = (time.perf_counter() - start) * 1000
            request_latency.record(latency_ms, attrs)
            logger.error("payment service call failed", extra={"error": str(exc)})
            raise HTTPException(status_code=502, detail="payment service error") from exc

    request_counter.add(1, attrs)
    latency_ms = (time.perf_counter() - start) * 1000
    request_latency.record(latency_ms, attrs)
    logger.info("checkout completed", extra={"route": "/checkout"})
    return {"status": "ok", "payment": response.json()}
