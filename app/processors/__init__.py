from abc import ABC, abstractmethod
from uuid import UUID

from app.models.ecg import DataAnalysisDAL, DataAnalysis as DataAnalysisModel
from sqlalchemy.ext.asyncio import AsyncSession


class BaseSignalProcessor(ABC):
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
