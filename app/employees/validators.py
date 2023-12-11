from tortoise.validators import Validator


class ChoiceValidator(Validator):
    def __init__(self, choices: tuple) -> None:
        self.choices = choices

    def __call__(self, value):
        if value not in self.choices:
            raise ValueError(f"Невозможно установить значение '{value}'. Допустимые значения {self.choices}")