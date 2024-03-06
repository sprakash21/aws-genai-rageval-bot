from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from rag_application_framework.db.models.models import RagScore
import pandas as pd


class RagMonitorQuery:
    def __init__(self, session: Session, engine: Engine):
        self.session = session
        self.engine = engine

    def get_rag_scores_1_hour(self):
        """Returns a filter results for visualizing the score information into UI
        Returns:
            pandas.DataFrame: Scores as DataFrame to be visualized
        """
        since = datetime.utcnow() - timedelta(hours=1)
        query = (
            self.session.query(RagScore)
            .with_entities(
                RagScore.total_duration,
                RagScore.answer_relevancy,
                RagScore.context_precision,
                RagScore.faithfulness,
                RagScore.model_type,
                RagScore.qa_status,
                RagScore.correctness,
                RagScore.time_stamp,
            )
            .filter(RagScore.time_stamp >= since)
        )

        results_df = pd.read_sql(query.statement, self.engine)
        return results_df

    def get_rag_scores_2_days(self):
        """Returns a filter results for visualizing the score information into UI
        Returns:
            pandas.DataFrame: Scores as DataFrame to be visualized
        """
        since = datetime.utcnow() - timedelta(days=2)
        query = (
            self.session.query(RagScore)
            .with_entities(
                RagScore.total_duration,
                RagScore.answer_relevancy,
                RagScore.context_precision,
                RagScore.faithfulness,
                RagScore.model_type,
                RagScore.qa_status,
                RagScore.correctness,
                RagScore.time_stamp,
            )
            .filter(RagScore.time_stamp >= since)
        )
        results_df = pd.read_sql(query.statement, self.engine)
        return results_df

    def get_rag_scores_24_hour(self):
        """Returns a filter results for visualizing the score information into UI
        Returns:
            pandas.DataFrame: Scores as DataFrame to be visualized
        """
        since = datetime.utcnow() - timedelta(days=1)
        query = (
            self.session.query(RagScore)
            .with_entities(
                RagScore.total_duration,
                RagScore.answer_relevancy,
                RagScore.context_precision,
                RagScore.faithfulness,
                RagScore.model_type,
                RagScore.qa_status,
                RagScore.correctness,
                RagScore.time_stamp,
            )
            .filter(RagScore.time_stamp >= since)
        )
        results_df = pd.read_sql(query.statement, self.engine)
        return results_df

    def get_rag_scores_7_day(self):
        """Returns a filter results for visualizing the score information into UI
        Returns:
            pandas.DataFrame: Scores as DataFrame to be visualized
        """
        since = datetime.utcnow() - timedelta(days=7)
        query = (
            self.session.query(RagScore)
            .with_entities(
                RagScore.total_duration,
                RagScore.answer_relevancy,
                RagScore.context_precision,
                RagScore.faithfulness,
                RagScore.model_type,
                RagScore.qa_status,
                RagScore.correctness,
                RagScore.time_stamp,
            )
            .filter(RagScore.time_stamp >= since)
        )
        results_df = pd.read_sql(query.statement, self.engine)
        return results_df

    def get_rag_scores(self, filter_type="1-hour"):
        """Filters and retreives results based on the user input filters

        Args:
            filter_type (str, optional): _description_. Defaults to "1-hour".

        Returns:
            pandas.DataFrame: dataframe of results
        """
        if filter_type == "1-hour":
            return self.get_rag_scores_1_hour()
        elif filter_type == "24-hour":
            return self.get_rag_scores_24_hour()
        elif filter_type == "2-day":
            return self.get_rag_scores_2_days()
        elif filter_type == "7-day":
            return self.get_rag_scores_7_day()
        else:
            return None
