"""Contrato de retomada segura para transcrições de mídia longa."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


class ChunkCheckpointState(StrEnum):
    """Estado persistido de uma parte, sem conteúdo da transcrição."""

    PENDING = "pending"
    UPLOADING = "uploading"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class CheckpointChunk:
    """Metadados mínimos para decidir se uma parte deve ser reenviada."""

    id: int
    start_ms: int
    end_ms: int
    state: ChunkCheckpointState
    attempts: int = 0
    result_ref: str | None = None

    def __post_init__(self) -> None:
        if self.id < 0 or self.start_ms < 0 or self.end_ms <= self.start_ms:
            raise ValueError("intervalo de parte inválido")
        if self.attempts < 0:
            raise ValueError("número de tentativas inválido")
        expected_ref = f"chunk-{self.id}.dpapi"
        if self.state is ChunkCheckpointState.CONFIRMED:
            if self.result_ref != expected_ref:
                raise ValueError("parte confirmada exige referência de resultado válida")
        elif self.result_ref is not None:
            raise ValueError("somente parte confirmada pode referenciar resultado")


@dataclass(frozen=True, slots=True)
class LongMediaCheckpoint:
    """Manifesto sem caminho, áudio ou texto transcrito."""

    attempt_id: str
    source_fingerprint: str
    parameters_hash: str
    created_at: datetime
    expires_at: datetime
    chunks: tuple[CheckpointChunk, ...]

    def __post_init__(self) -> None:
        if not self.attempt_id:
            raise ValueError("identificador de tentativa ausente")
        if len(self.source_fingerprint) != 64 or len(self.parameters_hash) != 64:
            raise ValueError("hash inválido")
        if self.created_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError("datas precisam conter fuso horário")
        if self.expires_at <= self.created_at:
            raise ValueError("expiração inválida")
        if not self.chunks:
            raise ValueError("checkpoint precisa conter ao menos uma parte")
        if tuple(chunk.id for chunk in self.chunks) != tuple(range(len(self.chunks))):
            raise ValueError("partes precisam ser contíguas e ordenadas")


class CheckpointStore(Protocol):
    """Porta de persistência; implementações devem proteger resultados."""

    def save(self, checkpoint: LongMediaCheckpoint) -> None: ...

    def load_matching(
        self,
        source_fingerprint: str,
        parameters_hash: str,
        now: datetime,
    ) -> LongMediaCheckpoint | None: ...

    def save_result(self, attempt_id: str, chunk_id: int, payload: bytes) -> str: ...

    def load_result(self, attempt_id: str, chunk_id: int) -> bytes: ...

    def delete(self, attempt_id: str) -> None: ...

    def cleanup(self, now: datetime) -> None: ...
