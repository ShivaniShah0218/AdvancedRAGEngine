"""
This module defines Prometheus metrics for monitoring the application. It includes counters for tracking the total number of HTTP requests and login attempts, as well as a histogram for measuring request latency. These metrics can be used to gain insights into the application's performance and usage patterns.
"""
from prometheus_client import Counter, Histogram

REQUEST_COUNT=Counter(
    "app_requests_total",
    "Total HTTP Requests",
    ["method","endpoint"]
    )

LOGIN_ATTEMPTS=Counter(
    "login_attempts_total",
    "Total login attempts",
    ["status", "role"]
    )

REQUEST_LATENCY=Histogram(
    "request_latency_seconds",
    "Request Latency"
    )
