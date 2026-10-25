# src/corporate_action_workflow_app_v2/logging_adapter/stdout_sink.py

import json
from typing import Union

from corporate_action_workflow_app_v2.semantic import (
    ErrorEntry,
    IntrospectionEvent,
    LogEntry,
)


class StdoutSink:
    """
    Cloud-aligned sink that prints structured semantic entries to stdout.
    In containerized deployments, stdout is the primary logging channel.
    """

    def write(self, entry: Union[LogEntry, ErrorEntry, IntrospectionEvent]):
        serialized = entry.model_dump()
        print(json.dumps(serialized))
