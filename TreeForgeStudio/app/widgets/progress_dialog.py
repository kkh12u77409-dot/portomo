"""Progress dialog widget for long-running filesystem operations.

Shows a determinate or indeterminate progress bar with a status message.
Runs its worker on a :class:`QThread` so the UI never blocks.
"""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import pyqtSignal, QThread, QObject
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QHBoxLayout,
)


class _Worker(QObject):
    """Generic worker that runs a callable on a background thread."""

    finished = pyqtSignal(object)      # result / exception marker
    progress = pyqtSignal(int, int, str)  # current, total, message
    failed = pyqtSignal(str)

    def __init__(self, fn: Callable[..., object], *args: object, **kwargs: object) -> None:
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self._cancelled = False
        self._report: Optional[Callable[[int, int, str], None]] = None

    def set_progress_reporter(self, reporter: Callable[[int, int, str], None]) -> None:
        self._report = reporter

    def request_cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        try:
            if self._report is not None:
                self._kwargs["report"] = self._emit_progress
            result = self._fn(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as exc:  # pragma: no cover - defensive
            self.failed.emit(str(exc))

    def _emit_progress(self, current: int, total: int, message: str) -> None:
        self.progress.emit(current, total, message)


class _Thread(QThread):
    def __init__(self, worker: _Worker, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._worker = worker

    def run(self) -> None:
        self._worker.run()


class ProgressDialog(QDialog):
    """A modal progress dialog for long-running operations.

    Usage::

        dlg = ProgressDialog(self, "Creating structure...")
        dlg.run_async(fn, *args, on_finished=callback)
    """

    def __init__(
        self,
        parent: Optional[object] = None,
        title: str = "Working...",
        indeterminite: bool = False,
    ) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.setObjectName("ProgressDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setMinimumHeight(150)
        self._indeterminate = indeterminite
        self._on_finished: Optional[Callable[[object], None]] = None
        self._build_ui(title)

    def _build_ui(self, title: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("ProgressTitle")
        self._title_label.setWordWrap(True)
        layout.addWidget(self._title_label)

        self._bar = QProgressBar()
        if self._indeterminate:
            self._bar.setRange(0, 0)
        else:
            self._bar.setRange(0, 100)
        self._bar.setObjectName("ProgressBar")
        layout.addWidget(self._bar)

        self._status = QLabel("")
        self._status.setObjectName("ProgressStatus")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self._cancel_button = QPushButton(self.tr("Cancel"))
        self._cancel_button.setObjectName("ProgressCancel")
        self._cancel_button.clicked.connect(self._on_cancel)
        button_row.addWidget(self._cancel_button)
        layout.addLayout(button_row)

    # ------------------------------------------------------------------
    # Async execution
    # ------------------------------------------------------------------

    def run_async(
        self,
        fn: Callable[..., object],
        *args: object,
        on_finished: Optional[Callable[[object], None]] = None,
        block: bool = True,
        **kwargs: object,
    ) -> None:
        """Run *fn* on a worker thread and close the dialog when finished.

        When *block* is True the dialog is shown modally (``exec``); when
        False the dialog is shown non-modally (``show``) and control returns
        immediately, which is friendlier for automated tests.
        """
        self._on_finished = on_finished
        worker = _Worker(fn, *args, **kwargs)
        worker.progress.connect(self._update_progress)
        worker.finished.connect(self._handle_finished)
        worker.failed.connect(self._handle_failed)
        self._worker = worker
        self._thread = _Thread(worker, self)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()
        if block:
            self.exec()
        else:
            self.show()

    def _update_progress(self, current: int, total: int, message: str) -> None:
        if total > 0:
            self._bar.setRange(0, total)
            self._bar.setValue(current)
        if message:
            self._status.setText(message)

    def _handle_finished(self, result: object) -> None:
        self._result = result
        if self._on_finished is not None:
            self._on_finished(result)

    def _handle_failed(self, message: str) -> None:
        self._status.setText(message)
        # Auto-close after showing the error briefly.
        self._cancel_button.setEnabled(False)

    def _on_thread_finished(self) -> None:
        """Close the dialog once the worker thread has fully finished."""
        if self.isVisible():
            self.accept()

    def _on_cancel(self) -> None:
        if hasattr(self, "_worker") and self._worker is not None:
            self._worker.request_cancel()
        self.reject()

    # ------------------------------------------------------------------
    # Synchronous helper
    # ------------------------------------------------------------------

    @staticmethod
    def run(
        parent: Optional[object],
        title: str,
        fn: Callable[..., object],
        *args: object,
        on_finished: Optional[Callable[[object], None]] = None,
        block: bool = True,
        **kwargs: object,
    ) -> object:
        """Convenience: create a dialog, run *fn* async, return the result."""
        dialog = ProgressDialog(parent, title)
        dialog.run_async(fn, *args, on_finished=on_finished, block=block, **kwargs)
        return getattr(dialog, "_result", None)
