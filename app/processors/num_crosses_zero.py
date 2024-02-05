from uuid import UUID

from sqlalchemy import text

from app.models.ecg import DataAnalysisDAL, DataAnalysis as DataAnalysisModel
from app.schemas.ecg import AnalysisStatus

from . import SignalProcessor


class NumCrossesZeroSignalProcessor(SignalProcessor):
    name = "num_crosses_zero"

    async def process(self, ecg_id: UUID) -> DataAnalysisModel:
        data_analysis = await super().process(ecg_id)
        # Process the signals
        data_analysis_dal = DataAnalysisDAL(self.db_session)
        data_analysis.status = AnalysisStatus.PROCESSING
        await data_analysis_dal.update(data_analysis)

        # Process signals using postgreSQL query
        sql_query = text(
            """
            SELECT
                name AS lead_name,
                COUNT(*) FILTER (WHERE (signal_value > 0 AND lag_signal_value < 0) OR (signal_value < 0 AND lag_signal_value > 0)) AS zero_crossings
            FROM (
                SELECT
                    name,
                    signal_value,
                    LAG(signal_value) OVER (PARTITION BY name ORDER BY signal_value_index) AS lag_signal_value
                FROM ecg_signal
                WHERE ecg_id = :ecg_id
            ) subquery
            GROUP BY name;
        """
        )
        data = dict(
            (await self.db_session.execute(sql_query, {"ecg_id": ecg_id})).all()
        )

        # Update data analysis
        data_analysis.result = data
        data_analysis.status = AnalysisStatus.COMPLETED
        await data_analysis_dal.update(data_analysis)

        # Return data analysis
        return data_analysis
