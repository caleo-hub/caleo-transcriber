"""Checkpoint local protegido pelo DPAPI do usuário atual do Windows."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import shutil
import uuid
from collections.abc import Mapping
from ctypes import wintypes
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from caleo_transcriber.application.checkpoints import (
    CheckpointChunk,
    ChunkCheckpointState,
    LongMediaCheckpoint,
)

_CRYPTPROTECT_UI_FORBIDDEN: Final = 0x01
_ENTROPY: Final = b"caleo-transcriber:checkpoint:v1"
_SAMPLE_BYTES: Final = 1024 * 1024


class CheckpointError(RuntimeError):
    """Falha segura da persistência de checkpoint."""


class CheckpointCorrupt(CheckpointError):
    """Checkpoint inválido, adulterado ou impossível de decifrar."""


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


class DpapiProtector:
    """Protege bytes para a conta Windows atual, sem interação de interface."""

    def __init__(self) -> None:
        self._crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    @staticmethod
    def _input_blob(data: bytes) -> tuple[_DataBlob, object]:
        buffer = ctypes.create_string_buffer(data, len(data))
        blob = _DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)))
        return blob, buffer

    def protect(self, plaintext: bytes) -> bytes:
        return self._transform(plaintext, decrypt=False)

    def unprotect(self, ciphertext: bytes) -> bytes:
        return self._transform(ciphertext, decrypt=True)

    def _transform(self, data: bytes, *, decrypt: bool) -> bytes:
        if not data:
            raise CheckpointCorrupt("conteúdo de checkpoint vazio")
        input_blob, input_buffer = self._input_blob(data)
        entropy_blob, entropy_buffer = self._input_blob(_ENTROPY)
        output_blob = _DataBlob()
        _ = input_buffer, entropy_buffer
        if decrypt:
            success = self._crypt32.CryptUnprotectData(
                ctypes.byref(input_blob),
                None,
                ctypes.byref(entropy_blob),
                None,
                None,
                _CRYPTPROTECT_UI_FORBIDDEN,
                ctypes.byref(output_blob),
            )
        else:
            success = self._crypt32.CryptProtectData(
                ctypes.byref(input_blob),
                None,
                ctypes.byref(entropy_blob),
                None,
                None,
                _CRYPTPROTECT_UI_FORBIDDEN,
                ctypes.byref(output_blob),
            )
        if not success:
            raise CheckpointCorrupt("DPAPI recusou o checkpoint")
        try:
            return ctypes.string_at(output_blob.pbData, output_blob.cbData)
        finally:
            self._kernel32.LocalFree(output_blob.pbData)


class WindowsCheckpointStore:
    """Manifestos atômicos e resultados cifrados, confinados à raiz recebida."""

    def __init__(self, root: Path, protector: DpapiProtector) -> None:
        self._root = root.resolve()
        self._protector = protector
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, checkpoint: LongMediaCheckpoint) -> None:
        directory = self._attempt_directory(checkpoint.attempt_id)
        directory.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": 1,
            "attempt_id": checkpoint.attempt_id,
            "source_fingerprint": checkpoint.source_fingerprint,
            "parameters_hash": checkpoint.parameters_hash,
            "created_at": checkpoint.created_at.astimezone(UTC).isoformat(),
            "expires_at": checkpoint.expires_at.astimezone(UTC).isoformat(),
            "chunks": [
                {
                    "id": chunk.id,
                    "start_ms": chunk.start_ms,
                    "end_ms": chunk.end_ms,
                    "state": chunk.state.value,
                    "attempts": chunk.attempts,
                    "result_ref": chunk.result_ref,
                }
                for chunk in checkpoint.chunks
            ],
        }
        self._write_atomic(directory / "manifest.json", _canonical_json(payload))

    def load_matching(
        self,
        source_fingerprint: str,
        parameters_hash: str,
        now: datetime,
    ) -> LongMediaCheckpoint | None:
        self.cleanup(now)
        for directory in sorted(self._root.iterdir()):
            manifest_path = directory / "manifest.json"
            if not directory.is_dir() or not manifest_path.is_file():
                continue
            try:
                checkpoint = self._read_manifest(manifest_path)
            except (CheckpointCorrupt, OSError, ValueError):
                self._delete_directory(directory)
                continue
            if (
                checkpoint.source_fingerprint == source_fingerprint
                and checkpoint.parameters_hash == parameters_hash
            ):
                recovered_chunks = tuple(
                    replace(chunk, state=ChunkCheckpointState.AMBIGUOUS)
                    if chunk.state is ChunkCheckpointState.UPLOADING
                    else chunk
                    for chunk in checkpoint.chunks
                )
                recovered = replace(checkpoint, chunks=recovered_chunks)
                if recovered != checkpoint:
                    self.save(recovered)
                return recovered
        return None

    def save_result(self, attempt_id: str, chunk_id: int, payload: bytes) -> str:
        if chunk_id < 0:
            raise ValueError("identificador de parte inválido")
        directory = self._attempt_directory(attempt_id)
        directory.mkdir(parents=True, exist_ok=True)
        result_ref = f"chunk-{chunk_id}.dpapi"
        self._write_atomic(directory / result_ref, self._protector.protect(payload))
        return result_ref

    def load_result(self, attempt_id: str, chunk_id: int) -> bytes:
        path = self._attempt_directory(attempt_id) / f"chunk-{chunk_id}.dpapi"
        try:
            protected = path.read_bytes()
            return self._protector.unprotect(protected)
        except (OSError, CheckpointCorrupt) as error:
            raise CheckpointCorrupt("resultado protegido indisponível") from error

    def delete(self, attempt_id: str) -> None:
        self._delete_directory(self._attempt_directory(attempt_id))

    def cleanup(self, now: datetime) -> None:
        for directory in tuple(self._root.iterdir()):
            if not directory.is_dir():
                continue
            manifest_path = directory / "manifest.json"
            try:
                checkpoint = self._read_manifest(manifest_path)
            except (CheckpointCorrupt, OSError, ValueError):
                self._delete_directory(directory)
                continue
            if checkpoint.expires_at <= now:
                self._delete_directory(directory)
                continue
            for audio_path in directory.glob("*.mp3"):
                audio_path.unlink(missing_ok=True)

    def _read_manifest(self, path: Path) -> LongMediaCheckpoint:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or payload.get("schema") != 1:
                raise CheckpointCorrupt("versão de manifesto inválida")
            chunks_value = payload["chunks"]
            if not isinstance(chunks_value, list):
                raise CheckpointCorrupt("lista de partes inválida")
            chunks = tuple(self._parse_chunk(item) for item in chunks_value)
            checkpoint = LongMediaCheckpoint(
                attempt_id=str(payload["attempt_id"]),
                source_fingerprint=str(payload["source_fingerprint"]),
                parameters_hash=str(payload["parameters_hash"]),
                created_at=datetime.fromisoformat(str(payload["created_at"])),
                expires_at=datetime.fromisoformat(str(payload["expires_at"])),
                chunks=chunks,
            )
            if self._attempt_directory(checkpoint.attempt_id) != path.parent.resolve():
                raise CheckpointCorrupt("identificador e diretório divergentes")
            return checkpoint
        except (KeyError, TypeError, json.JSONDecodeError) as error:
            raise CheckpointCorrupt("manifesto inválido") from error

    @staticmethod
    def _parse_chunk(value: object) -> CheckpointChunk:
        if not isinstance(value, dict):
            raise CheckpointCorrupt("parte inválida")
        return CheckpointChunk(
            id=int(value["id"]),
            start_ms=int(value["start_ms"]),
            end_ms=int(value["end_ms"]),
            state=ChunkCheckpointState(str(value["state"])),
            attempts=int(value["attempts"]),
            result_ref=None if value.get("result_ref") is None else str(value["result_ref"]),
        )

    def _attempt_directory(self, attempt_id: str) -> Path:
        try:
            canonical = str(uuid.UUID(attempt_id))
        except (ValueError, AttributeError) as error:
            raise ValueError("identificador de tentativa inválido") from error
        directory = (self._root / canonical).resolve()
        if directory.parent != self._root:
            raise ValueError("checkpoint fora da raiz")
        return directory

    def _delete_directory(self, directory: Path) -> None:
        resolved = directory.resolve()
        if resolved.parent != self._root:
            raise CheckpointError("recusa em remover diretório fora da raiz")
        if resolved.exists():
            shutil.rmtree(resolved)

    @staticmethod
    def _write_atomic(path: Path, payload: bytes) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        try:
            with temporary.open("wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def fingerprint_source(path: Path) -> str:
    """Identifica a mídia sem persistir seu caminho ou conteúdo."""

    stat = path.stat()
    digest = hashlib.sha256()
    digest.update(str(stat.st_size).encode("ascii"))
    digest.update(b"\0")
    digest.update(str(stat.st_mtime_ns).encode("ascii"))
    digest.update(b"\0")
    with path.open("rb") as handle:
        digest.update(handle.read(_SAMPLE_BYTES))
        if stat.st_size > _SAMPLE_BYTES:
            handle.seek(max(0, stat.st_size - _SAMPLE_BYTES))
            digest.update(handle.read(_SAMPLE_BYTES))
    return digest.hexdigest()


def hash_parameters(parameters: Mapping[str, object]) -> str:
    """Hash estável dos parâmetros que alteram o resultado."""

    return hashlib.sha256(_canonical_json(dict(parameters))).hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
