"""OpenTelemetry initialization for the service.

This module wires tracing, metrics, and logging to an OTLP collector.
Keeping telemetry setup here keeps the FastAPI app logic clean and readable.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "payment-service")
SERVICE_VERSION = "0.1"
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")


def _build_resource() -> Resource:
    # Resource attributes describe the service itself and are attached to all telemetry.
    return Resource.create(
        {
            "service.name": SERVICE_NAME,
            "service.version": SERVICE_VERSION,
        }
    )


def init_tracing(resource: Resource) -> None:
    """Configure tracing with an OTLP exporter."""
    tracer_provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)


def init_metrics(resource: Resource) -> None:
    """Configure metrics with a periodic OTLP exporter."""
    metric_exporter = OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True)
    reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)


def init_logging() -> None:
    """Configure structured logging with trace correlation.

    Injects trace_id and span_id into log records for correlation with traces.
    """
    # Custom formatter to include trace context
    class TraceFormatter(logging.Formatter):
        def format(self, record):
            # Get trace and span IDs from the record (injected by LoggingInstrumentor)
            trace_id = getattr(record, "otelTraceID", "")
            span_id = getattr(record, "otelSpanID", "")
            record.trace_id = trace_id
            record.span_id = span_id
            if trace_id and span_id:
                # W3C traceparent format: version-traceid-spanid-flags
                record.traceparent = f"00-{trace_id}-{span_id}-01"
            else:
                record.traceparent = ""
            return super().format(record)

    # Configure logging with the custom formatter
    formatter = TraceFormatter(
        "%(asctime)s %(levelname)s %(name)s "
        "trace_id=%(trace_id)s span_id=%(span_id)s traceparent=%(traceparent)s "
        "%(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    # Instrument logging to propagate context
    LoggingInstrumentor().instrument()


def init_telemetry() -> None:
    """Initialize all telemetry components."""
    resource = _build_resource()
    init_tracing(resource)
    init_metrics(resource)
    init_logging()


def get_tracer(name: Optional[str] = None):
    return trace.get_tracer(name or SERVICE_NAME)


def get_meter(name: Optional[str] = None):
    return metrics.get_meter(name or SERVICE_NAME)
