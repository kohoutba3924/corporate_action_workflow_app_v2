# src/corporate_action_workflow_app_v2/logging_adapter/local_file_sink.py

import json
from pathlib import Path
from typing import Union

from corporate_action_workflow_app_v2.semantic import (
    ErrorEntry,
    IntrospectionEvent,
    LogEntry,
)


class LocalFileSink:
    """
    Demo-only logging sink that writes structured semantic entries
    to a local file for inspection. In production, this would be
    replaced with stdout and a cloud logging backend.
    """

    def __init__(self, file_path: Union[str, Path] = "../../logs/app.log"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, entry: Union[LogEntry, ErrorEntry, IntrospectionEvent]):
        serialized = entry.model_dump()
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(serialized) + "\n")
