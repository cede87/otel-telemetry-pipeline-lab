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

client traffic
↓
instrumented service (Python)
↓
OpenTelemetry SDK
↓
OpenTelemetry Collector
↓
telemetry processing pipeline
↓
metrics / logs / traces backends

The pipeline will allow experimentation with:

- telemetry batching
- sampling strategies
- attribute processing
- cardinality implications
- telemetry routing

---

## Repository Components

### Service

A small Python service instrumented with OpenTelemetry.  
It generates telemetry signals including:

- traces
- metrics
- structured logs

The service exposes simple HTTP endpoints to simulate application workloads.

---

### Load Generator

A lightweight traffic generator used to produce requests against the service.

This component allows simulation of different runtime scenarios such as:

- latency spikes
- request bursts
- error responses

These scenarios make the telemetry pipeline more interesting to observe.

---

### OpenTelemetry Collector

The collector acts as the central telemetry pipeline component.

Its responsibilities include:

- receiving telemetry signals
- batching and processing telemetry
- exporting signals to different backends

The project experiments with different processors and pipeline configurations.

---

### Observability Backends

Telemetry data is exported to observability backends for analysis and visualization.

Typical backends include:

- metrics storage
- log aggregation
- trace visualization

These allow inspection of system behaviour and correlation between signals.

---

## Topics Explored

This lab focuses on understanding several important observability concepts:

- telemetry signal types (metrics, logs, traces)
- telemetry ingestion pipelines
- batching and processing strategies
- trace sampling techniques
- high-cardinality telemetry attributes
- telemetry routing and enrichment

---

## Running the Environment

The full environment will run locally using containers.

The goal is to provide a reproducible setup that can be launched easily.

This will start the full telemetry environment including the instrumented service, telemetry pipeline and observability backends.

---

## Why This Project

Modern distributed systems generate enormous amounts of telemetry data. Understanding how telemetry pipelines work is critical for designing scalable observability platforms.

This project provides a hands-on environment to explore these systems and understand the architectural trade-offs behind telemetry ingestion and processing.

---

## Status

This project is an evolving lab environment and will continue to grow as new observability experiments are added.
