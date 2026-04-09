from inspect import signature
from typing import Any

from .methods import (
    ass_downstream,
    ass_upstream,
    fermer_vanne,
    inverser_canalisation,
    ouvrir_vanne,
)
from .tools import display_error_message

ACTIONS = (
    inverser_canalisation,
    ass_downstream,
    ass_upstream,
    fermer_vanne,
    ouvrir_vanne,
)

class InvalidArgumentError(Exception):
    pass


def run(name: str, **kwargs: Any):
    """
    Run the action with the given name and arguments.

    :param name: Name of the action to run. The available values are:
        - inverser_canalisation
        - ass_downstream
        - ass_upstream
        - fermer_vanne
        - ouvrir_vanne
    :param **kwargs: Arguments to pass to the action.
    :return: None
    """
    # Find action
    if action := next((a for a in ACTIONS if a.__name__ == name), None):
        # Check arguments
        sig = signature(action)
        params = sig.parameters

        def check(arg: str, value: Any) -> Any:
            if arg in params:
                anno = params[arg].annotation
                if not isinstance(value, anno):
                    value = anno(value)
                return value
            raise InvalidArgumentError(arg)

        try:
            if len(params) != len(kwargs):
                raise InvalidArgumentError()
            args = {arg: check(arg, value) for arg, value in kwargs.items()}
        except InvalidArgumentError:
            display_error_message(
                f"Arguments invalides for action \"{name}\", "
                f"Attendus: {sig}, "
                f"Reçus: {kwargs}"
            )
            return
        action(**args)
    else:
        display_error_message(
            f"L'action \"{name}\" n'a pas été trouvée!"
        )
