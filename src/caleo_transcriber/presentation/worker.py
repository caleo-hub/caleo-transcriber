"""Ponte Qt para executar o caso de uso fora da thread da interface."""

from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from caleo_transcriber.application import (
    BatchProcessor,
    TranscribeSingleFileCommand,
    TranscribeSingleFileUseCase,
    TranscriptionAlreadyRunningError,
)


class CancellationToken:
    def __init__(self) -> None:
        self._requested = Event()

    def request(self) -> None:
        self._requested.set()

    def is_requested(self) -> bool:
        return self._requested.is_set()


class TranscriptionWorker(QObject):
    result_ready = Signal(object)
    safe_error = Signal(str)
    finished = Signal()

    def __init__(
        self,
        use_case: TranscribeSingleFileUseCase,
        command: TranscribeSingleFileCommand,
        cancellation: CancellationToken,
    ) -> None:
        super().__init__()
        self._use_case = use_case
        self._command = command
        self._cancellation = cancellation

    @Slot()
    def run(self) -> None:
        try:
            result = self._use_case.execute(self._command, self._cancellation.is_requested)
        except TranscriptionAlreadyRunningError:
            self.safe_error.emit("Já existe uma transcrição em andamento.")
        except Exception:
            self.safe_error.emit(
                "O trabalho foi interrompido por uma falha interna. Você pode tentar novamente."
            )
        else:
            self.result_ready.emit(result)
        finally:
            self.finished.emit()


class BatchWorker(QObject):
    summary_ready = Signal(object)
    safe_error = Signal(str)
    finished = Signal()

    def __init__(self, processor: BatchProcessor) -> None:
        super().__init__()
        self._processor = processor

    @Slot()
    def run(self) -> None:
        try:
            self.summary_ready.emit(self._processor.run())
        except Exception:
            self.safe_error.emit(
                "A fila foi interrompida por uma falha interna. "
                "Os itens concluídos foram preservados."
            )
        finally:
            self.finished.emit()
