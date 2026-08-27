from inspect import Parameter, signature
from typing import Any

from .methods import (
    aep_pgr_nearest_vannes,
    aep_pgr_path_to_nearest_target,
    ass_downstream,
    ass_upstream,
    fermer_vanne,
    inverser_canalisation,
    noop_action,
    ouvrir_vanne,
)
from .tools import display_error_message

ACTIONS = (
    inverser_canalisation,
    ass_downstream,
    ass_upstream,
    fermer_vanne,
    ouvrir_vanne,
    noop_action,
    aep_pgr_path_to_nearest_target,
    aep_pgr_nearest_vannes,
)


class RunActionError(Exception):
    pass


class InvalidArgumentError(RunActionError):
    pass


class MissingParameterError(RunActionError):
    pass


class MethodNotFoundError(RunActionError):
    pass


def run(name: str, **kwargs: Any) -> RunActionError | None:
    """
    Run the action with the given name and arguments.

    :param name: Name of the action to run. The available values are:
        - inverser_canalisation
        - ass_downstream
        - ass_upstream
        - fermer_vanne
        - ouvrir_vanne
        - aep_pgr_nearest_vannes
    :param **kwargs: Arguments to pass to the action.
    :return: None
    """
    # Find action
    if action := next((a for a in ACTIONS if a.__name__ == name), None):
        # Check arguments
        sig = signature(action)
        params = sig.parameters

        def check(param: Parameter) -> Any:
            if param.name not in kwargs:
                raise MissingParameterError(param.name)

            anno = param.annotation
            value = kwargs[param.name]
            if not isinstance(value, anno):
                try:
                    value = anno(value)
                except ValueError:
                    raise InvalidArgumentError(param.name) from None
            return value

        try:
            args = {arg: check(param) for arg, param in params.items()}
        except RunActionError as err:
            display_error_message(
                f'Arguments invalides for action "{name}", Attendus: {sig}, Reçus: {kwargs}'
            )
            return err

        action(**args)
        return None

    display_error_message(f"L'action \"{name}\" n'a pas été trouvée!")

    return MethodNotFoundError(name)
