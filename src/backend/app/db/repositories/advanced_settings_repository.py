"""This module provides a repository for calculation sets."""

from sqlalchemy import and_, select
from sqlalchemy.orm import Session


from db.schemas.calculation import AdvancedSettings
from models.setup import AdvancedSettingsDto


class AdvancedSettingsRepository:
    """Repository for managing calculation sets."""

    def get(self, session: Session, settings: AdvancedSettingsDto) -> AdvancedSettings | None:
        """Get Advanced Calculation Settings from database.

        Args:
            settings (AdvancedSettingsDto): Advanced calculation settings.

        Returns:
            AdvancedSettings: Advanced calculation settings.
        """

        statement = select(AdvancedSettings).where(
            and_(
                AdvancedSettings.ignore_water == settings.ignore_water,
                AdvancedSettings.read_hetatm == settings.read_hetatm,
                AdvancedSettings.permissive_types == settings.permissive_types,
            )
        )

        advanced_settings = (session.execute(statement)).unique().scalars(AdvancedSettings).first()

        return advanced_settings

    def store(self, session: Session, advanced_settings: AdvancedSettings) -> None:
        """Store an Advanced Calculation Settings in the database.

        Args:
            advanced_settings (AdvancedSettings): Advanced calculation settings.
        """

        session.add(advanced_settings)
