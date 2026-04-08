from .methods import (
    ass_downstream,
    ass_upstream,
    fermer_vanne,
    inverser_canalisation,
    ouvrir_vanne,
)
from .tools import display_error_message


def run(name: str, *args):
    """
    Run the action with the given name and arguments.

    :param name: Name of the action to run. The available values are:
        - inverser_canalisation
        - ass_downstream
        - ass_upstream
        - fermer_vanne
        - ouvrir_vanne
    :param *args: Arguments to pass to the action.
    :return: None
    """
    if name == "inverser_canalisation":
        inverser_canalisation(*args)
    elif name == "ass_downstream":
        ass_downstream(*args)
    elif name == "ass_upstream":
        ass_upstream(*args)
    elif name == "fermer_vanne":
        fermer_vanne(*args)
    elif name == "ouvrir_vanne":
        ouvrir_vanne(*args)
    else:
        display_error_message(
            f"L'action \"{name}\" n'a pas été trouvée!"
        )
