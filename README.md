# OpenTelemetry Telemetry Pipeline Lab

This repository contains a small experimental environment to explore modern observability pipelines using OpenTelemetry.

The purpose of this project is to understand how telemetry signals (metrics, traces and logs) flow through a typical observability pipeline and how different components interact in a real-world setup.

Rather than focusing on a specific production system, this repository acts as a learning and experimentation lab to investigate concepts such as telemetry ingestion, processing, sampling and visualization.

---

## Project Goals

The main objective of this project is to gain a deeper understanding of telemetry pipelines by building a minimal but realistic observability stack.

The project explores:

- Instrumenting services with OpenTelemetry
- Collecting telemetry using the OpenTelemetry Collector
- Processing telemetry through pipeline processors
- Exporting telemetry signals to different backends
- Visualizing system behaviour through observability dashboards

The goal is not to build a production-ready system, but to explore the architecture and trade-offs involved in observability platforms.

---

## Architecture Overview

The project simulates a simplified telemetry pipeline.
