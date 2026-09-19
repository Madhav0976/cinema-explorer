from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.title import Title


class WatchProvider(Base):
    __tablename__ = "watch_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tmdb_provider_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    titles: Mapped[list["TitleWatchProvider"]] = relationship(
        back_populates="provider",
        cascade="all, delete-orphan",
    )


class TitleWatchProvider(Base):
    __tablename__ = "title_watch_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("watch_providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    country_code: Mapped[str] = mapped_column(String(10), nullable=False)
    offer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "title_id",
            "provider_id",
            "country_code",
            "offer_type",
            name="uq_title_watch_provider_offer",
        ),
        Index(
            "ix_title_watch_providers_title_country",
            "title_id",
            "country_code",
        ),
    )

    title: Mapped["Title"] = relationship(back_populates="watch_providers")
    provider: Mapped["WatchProvider"] = relationship(back_populates="titles")

