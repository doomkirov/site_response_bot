from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Text

from settings.database import Base


class LinksModel(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)

    last_checked = Column(BigInteger, default=0)
    last_status = Column(Integer, default=0)
    last_error_status = Column(Integer, default=0)
    last_error_time = Column(BigInteger, default=0)
    last_success_time = Column(BigInteger, default=0)

    class Config:
        orm_mode = True

    def __str__(self):
        return self.url


class SiteIncidentModel(Base):
    __tablename__ = "site_incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String, nullable=False)
    started_at = Column(BigInteger, nullable=False, index=True)
    status_code = Column(Integer, nullable=False)
    description = Column(Text, nullable=False, default="")
    confirmed_at = Column(BigInteger, nullable=True)
    confirmed_status_code = Column(Integer, nullable=True)
    confirmed_description = Column(Text, nullable=True)
    alert_suppressed = Column(Boolean, nullable=False, default=False)
    alert_sent_at = Column(BigInteger, nullable=True)
    recovered_at = Column(BigInteger, nullable=True, index=True)
    recovery_sent_at = Column(BigInteger, nullable=True)


class DailyReportModel(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(String, nullable=False, unique=True)
    sent_at = Column(BigInteger, nullable=False)
