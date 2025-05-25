"""
Chain of thought capturing and logging for agent systems.

This package provides a framework-agnostic way to capture, format, and display
the chain of thought reasoning from different agent frameworks.
"""

from aiden.common.utils.cot.protocol import StepSummary, ToolCall
from aiden.common.utils.cot.adapters import extract_step_summary_from_smolagents
from aiden.common.utils.cot.callable import ChainOfThoughtCallable
from aiden.common.utils.cot.emitters import (
    ChainOfThoughtEmitter,
    ConsoleEmitter,
    LoggingEmitter,
    MultiEmitter,
)

__all__ = [
    "StepSummary",
    "ToolCall",
    "extract_step_summary_from_smolagents",
    "ChainOfThoughtCallable",
    "ChainOfThoughtEmitter",
    "ConsoleEmitter",
    "LoggingEmitter",
    "MultiEmitter",
]
