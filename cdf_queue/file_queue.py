from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ItemStatus(Enum):
    New = 0
    Running = 1
    Ack = 2
    Nack = 3
    TimeOut = 4


@dataclass
class ItemQueue:
    file_external_id: str
    status: ItemStatus
    create_time: datetime
    update_time: Optional[datetime]


class RunStatus(Enum):
    Running = 0
    Success = 1
    Failed = 2


@dataclass
class ItemRun:
    file_external_id: str
    create_time: datetime
    update_time: Optional[datetime]
    function_id: int
    run_id: int
    status: RunStatus
    log_text: Optional[str]
    response_text: Optional[str]


class QueueBackend:
    @abstractmethod
    def create_item(item: ItemQueue) -> None:
        pass

    @abstractmethod
    def update_item(item: ItemQueue) -> None:
        pass

    @abstractmethod
    def create_run(run: ItemRun) -> None:
        pass

    @abstractmethod
    def update_run(run: ItemRun) -> None:
        pass


class TableBackend(QueueBackend):
    def __init__(
        self,
        db_name: str,
        table_items: str = "Items",
        table_runs: str = "Run",
    ):
        self.db_name = db_name
        self.table_items = table_items
        self.table_runs = table_runs
