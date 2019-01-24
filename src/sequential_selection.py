"""While there are slightly different strategies for performing sequential
selection, they all use the same base idea, which is represented here"""

import numpy as np

from src.data_verification import verify_data, determine_variable_names
from src.result import ImportanceResult
from src.selection_strategies import sfs_strategy
from src.scoring_strategies import verify_scoring_strategy
from src.utils import convert_result_list_to_dict, get_data_subset


__all__ = ["sequential_forward_selection"]


def sequential_selection(training_data, scoring_data, scoring_fn, scoring_strategy, selection_strategy, variable_names=None, nimportant_vars=None, method=None):
    """Performs an abstract sequential selection over data given a particular
    set of functions for scoring, determining optimal variables, and selecting
    data

    :param training_data: a 2-tuple (inputs, outputs) for training in the
        scoring_fn
    :param scoring_data: a 2-tuple (inputs, outputs) for scoring in the
        scoring_fn
    :param scoring_fn: a function to be used for scoring. Should be of the form
        (training_data, scoring_data) -> float
    :param scoring_strategy: a function to be used for determining optimal
        variables or a string. If a function, should be of the form
            ([floats]) -> index. If a string, must be one of the options in
        scoring_strategies.VALID_SCORING_STRATEGIES
    :param selection_strategy: a function to be used for selecting a fraction of
        the data to be used at each iteration. Should be of the form
        (num_vars, important_vars: [index]) ->
            list of (variable being evaluated, data columns to include)
    :param variable_names: an optional list for variable names. If not given,
        will use names of columns of data (if pandas dataframe) or column
        indices
    :param nimportant_vars: number of times to compute the next most important
        variable. Defaults to all
    :param method: a string for the name of the method used. Defaults to the
        name of the selection_strategy if not given
    :returns: ImportanceResult object which contains the results for each run
    """

    training_data = verify_data(training_data)
    scoring_data = verify_data(scoring_data)

    scoring_strategy = verify_scoring_strategy(scoring_strategy)

    variable_names = determine_variable_names(training_data, variable_names)

    nimportant_vars = len(
        variable_names) if nimportant_vars is None else nimportant_vars

    method = selection_strategy.__name__ if method is None else method

    result_obj = ImportanceResult(method, variable_names)

    important_vars = list()
    num_vars = len(variable_names)
    for _ in range(nimportant_vars):
        result = _singlethread_iteration(training_data, scoring_data, scoring_fn,
                                         selection_strategy(num_vars, important_vars))
        next_result = convert_result_list_to_dict(
            result, variable_names, scoring_strategy)
        best_var = min(
            next_result.keys(), key=lambda key: next_result[key][0])
        best_index = np.flatnonzero(variable_names == best_var)[0]
        result_obj.add_new_results(
            next_result, next_important_variable=best_var)
        important_vars.append(best_index)

    return result_obj


def _singlethread_iteration(training_data, scoring_data, scoring_fn, selection_iterator):
    """Handles a single pass of the sequential selection algorithm, assuming a
    single worker thread

    :param training_data: (training_inputs, training_outputs)
    :param scoring_data: (scoring_inputs, scoring_outputs)
    :param scoring_fn: a function to be used for scoring. Should be of the form
        (training_data, scoring_data) -> float
    :param selection_iterator: the result of the selection strategy. Should be
        an iterable of (variable being evaluated, data columns to include)
    :returns: a list of (var, score)
    """
    training_inputs, training_outputs = training_data
    scoring_inputs, scoring_outputs = scoring_data

    result = list()
    for var, column_indices in selection_iterator:
        training_inputs_subset = get_data_subset(
            training_inputs, column_indices)
        scoring_inputs_subset = get_data_subset(scoring_inputs, column_indices)

        score = scoring_fn((training_inputs_subset, training_outputs),
                           (scoring_inputs_subset, scoring_outputs))
        result.append((var, score))
    return result


def sequential_forward_selection(training_data, scoring_data, scoring_fn, scoring_strategy, variable_names=None, nimportant_vars=None):
    """Performs an abstract sequential selection over data given a particular
    set of functions for scoring, determining optimal variables, and selecting
    data

    :param training_data: a 2-tuple (inputs, outputs) for training in the
        scoring_fn
    :param scoring_data: a 2-tuple (inputs, outputs) for scoring in the
        scoring_fn
    :param scoring_fn: a function to be used for scoring. Should be of the form
        (training_data, scoring_data) -> float
    :param scoring_strategy: a function to be used for determining optimal
        variables. Should be of the form ([floats]) -> index
    :param variable_names: an optional list for variable names. If not given,
        will use names of columns of data (if pandas dataframe) or column
        indices
    :param nimportant_vars: number of times to compute the next most important
        variable. Defaults to all
    :returns: ImportanceResult object which contains the results for each run
    """
    return sequential_selection(training_data, scoring_data, scoring_fn, scoring_strategy, sfs_strategy, variable_names=variable_names, nimportant_vars=nimportant_vars, method="Sequential Forward Selection")
