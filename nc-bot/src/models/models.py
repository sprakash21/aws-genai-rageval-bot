import datetime
from sqlalchemy import String, DateTime, Integer, Double, Boolean, ARRAY, Numeric
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict


class Base(DeclarativeBase):
    pass


class RagScore(Base):
    __tablename__ = "rag_score"
    score_id = mapped_column(Integer, primary_key=True)
    chain_info = mapped_column(MutableDict.as_mutable(JSONB))
    total_duration = mapped_column(Numeric)
    model_type = mapped_column(String(255))
    faithfulness = mapped_column(Double)
    context_precision = mapped_column(Double)
    qa_status = mapped_column(Boolean, default=False)
    time_stamp = mapped_column(DateTime)
    harmfulness = mapped_column(Double)
    answer_relevancy = mapped_column(Double)

    def __repr__(self):
        return f"RagScore(score_id={self.score_id}, chain_info={self.chain_info}, total_duration={self.total_duration}, model_type={self.model_type}, faithfulness={self.faithfulness}, context_precision={self.context_precision}, qa_status={self.qa_status}, time_stamp={self.time_stamp}, harmfulness={self.harmfulness}, answer_relevancy={self.answer_relevancy})"
