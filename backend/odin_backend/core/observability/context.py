"""Async-safe causal trace context propagation."""

from __future__ import annotations

from contextvars import ContextVar, Token
from uuid import uuid4

from pydantic import BaseModel, Field


class CausalTraceContext(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    span_id: str = Field(default_factory=lambda: str(uuid4()))
    parent_span_id: str | None = None
    causal_chain_id: str = Field(default_factory=lambda: str(uuid4()))
    mission_id: str | None = None
    task_id: str | None = None
    workflow_id: str | None = None
    agent_id: str | None = None
    signal_id: str | None = None

    def child_span(
        self,
        *,
        mission_id: str | None = None,
        task_id: str | None = None,
        workflow_id: str | None = None,
        agent_id: str | None = None,
        signal_id: str | None = None,
    ) -> CausalTraceContext:
        return CausalTraceContext(
            trace_id=self.trace_id,
            span_id=str(uuid4()),
            parent_span_id=self.span_id,
            causal_chain_id=self.causal_chain_id,
            mission_id=mission_id or self.mission_id,
            task_id=task_id or self.task_id,
            workflow_id=workflow_id or self.workflow_id,
            agent_id=agent_id or self.agent_id,
            signal_id=signal_id or self.signal_id,
        )

    def fork_trace(
        self,
        *,
        mission_id: str | None = None,
        causal_chain_id: str | None = None,
    ) -> CausalTraceContext:
        """New trace_id, same or new causal chain (e.g. new mission)."""
        return CausalTraceContext(
            trace_id=str(uuid4()),
            span_id=str(uuid4()),
            parent_span_id=self.span_id,
            causal_chain_id=causal_chain_id or self.causal_chain_id,
            mission_id=mission_id or self.mission_id,
            task_id=self.task_id,
            workflow_id=self.workflow_id,
            agent_id=self.agent_id,
        )


_current: ContextVar[CausalTraceContext | None] = ContextVar("odin_causal_trace", default=None)


def current_context() -> CausalTraceContext | None:
    return _current.get()


def bind_context(ctx: CausalTraceContext) -> Token:
    return _current.set(ctx)


def reset_context(token: Token) -> None:
    _current.reset(token)


def ensure_context(**kwargs) -> CausalTraceContext:
    ctx = current_context()
    if ctx is None:
        ctx = CausalTraceContext(**{k: v for k, v in kwargs.items() if v is not None})
        bind_context(ctx)
        return ctx
    updates = {k: v for k, v in kwargs.items() if v is not None}
    if updates:
        data = ctx.model_dump()
        data.update(updates)
        ctx = CausalTraceContext(**data)
        bind_context(ctx)
    return ctx
