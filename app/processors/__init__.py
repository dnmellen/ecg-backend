from abc import ABC, abstractmethod
import importlib
import inspect
import os
import pkgutil
from uuid import UUID

from fastapi import BackgroundTasks

from app.models.ecg import DataAnalysisDAL, DataAnalysis as DataAnalysisModel
from sqlalchemy.ext.asyncio import AsyncSession


class SignalProcessor(ABC):
    name: str | None = None

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    @abstractmethod
    async def process(self, ecg_id: UUID) -> DataAnalysisModel:
        data_analysis_dal = DataAnalysisDAL(self.db_session)

        # Create empty data analysis
        return await data_analysis_dal.create(
            DataAnalysisModel(
                ecg_id=ecg_id,
                name=self.name,
            )
        )


async def process_signals_task(signal_processor: SignalProcessor, ecg_id: UUID) -> None:
    """Background task to process signals"""
    await signal_processor.process(ecg_id)


def get_all_processors() -> list[SignalProcessor]:
    """Return all signal processors"""
    # Get the path to the package
    package_path = os.path.dirname(__file__)

    # Use pkgutil to iterate through all modules in the package
    package_modules = pkgutil.iter_modules([package_path])

    signal_processor_subclasses = []

    for _, module_name, _ in package_modules:
        full_module_name = f".{module_name}"

        # Import the module dynamically
        module = importlib.import_module(full_module_name, package="app.processors")

        # Iterate through the objects in the module
        for name, obj in inspect.getmembers(module):
            # Check if the object is a class and a subclass of SignalProcessor
            if (
                inspect.isclass(obj)
                and issubclass(obj, SignalProcessor)
                and obj != SignalProcessor
            ):
                signal_processor_subclasses.append(obj)

    return signal_processor_subclasses


def process_signals(
    db_session: AsyncSession, background_tasks: BackgroundTasks, ecg_id: UUID
) -> None:
    """Process signals for a given ecg"""
    signal_processors = get_all_processors()
    for signal_processor in signal_processors:
        processor = signal_processor(db_session)
        background_tasks.add_task(process_signals_task, processor, ecg_id)
