import uuid
from dataclasses import dataclass, field
from uuid import UUID

from src.core._shared.domain.entity import Entity


@dataclass(eq=False)
class Category(Entity):
    name: str
    description: str = ""
    is_active: bool = True

    def __post_init__(self):
        self.validate()

    def validate(self):
        if len(self.name) > 255:
            # raise ValueError("name cannot be longer than 255")
            self.notification.add_error("name cannot be longer than 255")

        if not self.name:  # len(self.name) == 0
            # raise ValueError("name cannot be empty")
            self.notification.add_error("name cannot be empty")

        if len(self.description) > 1024:
            # raise ValueError("description cannot be longer than 1024")
            self.notification.add_error("description cannot be longer than 1024")

        if self.notification.has_errors:
            # Não interrompemos o fluxo e acumulamos os erros
            # Poderíamos não retornar `ValueError` e deixar como responsabilidade do cliente verificar se há erros.
            raise ValueError(self.notification.messages)

    def __str__(self):
        return f"{self.name} - {self.description} ({self.is_active})"

    def __repr__(self):
        return f"<Category {self.name} ({self.id})>"

    def update_category(self, name, description):
        self.name = name
        self.description = description

        self.validate()

    def activate(self):
        self.is_active = True

        self.validate()

    def deactivate(self):
        self.is_active = False

        self.validate()
