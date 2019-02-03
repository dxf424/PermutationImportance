"""These are handy metric functions which can be used to score model predictions
against the true values. Additionally, all of the metrics provided by
scikit-learn should also work"""


import numpy as np

from src.error_handling import AmbiguousProbabilisticForecastsException, UnmatchingProbabilisticForecastsException, UnmatchedLengthPredictionsException


__all__ = ["gerrity_score", "peirce_skill_score", "heidke_skill_score"]


def gerrity_score(truths, predictions, classes=None):
    """Determines the gerrity score, returning a scalar

    :param truths: The true labels of these data
    :param predictions: The predictions of the model
    :param classes: an ordered set for the label possibilities. If not given,
        will be deduced from the truth values
    :returns: a single value for the gerrity score
    """
    table = _get_contingency_table(truths, predictions, classes)
    return _gerrity_score(table)


def peirce_skill_score(truths, predictions, classes=None):
    """Determines the peirce skill score, returning a scalar

    :param truths: The true labels of these data
    :param predictions: The predictions of the model
    :param classes: an ordered set for the label possibilities. If not given,
        will be deduced from the truth values
    :returns: a single value for the peirce skill score
    """
    table = _get_contingency_table(truths, predictions, classes)
    return _peirce_skill_score(table)


def heidke_skill_score(truths, predictions, classes=None):
    """Determines the heidke skill score, returning a scalar

    :param truths: The true labels of these data
    :param predictions: The predictions of the model
    :param classes: an ordered set for the label possibilities. If not given,
        will be deduced from the truth values
    :returns: a single value for the heidke skill score
    """
    table = _get_contingency_table(truths, predictions, classes)
    return _heidke_skill_score(table)


def _get_contingency_table(truths, predictions, classes=None):
    """Uses the truths and predictions to compute a contingency matrix

    :param truths: The true labels of these data
    :param predictions: The predictions of the model
    :param classes: an ordered set for the label possibilities. If not given,
        will be deduced from the truth values if possible
    :returns: a numpy array of shape (num_classes, num_classes)
    """
    if len(truths) != len(predictions):
        raise UnmatchedLengthPredictionsException(truths, predictions)
    if len(truths.shape) == 2:
        # Fully probabilistic model
        if len(predictions.shape) != 2 or predictions.shape[1] != truths.shape[1]:
            raise UnmatchingProbabilisticForecastsException(
                truths, predictions)
        table = np.zeros((truths.shape[1], truths.shape[1]), dtype=np.float32)
        trues = np.argmax(truths, axis=1)
        preds = np.argmax(predictions, axis=1)
        for true, pred in zip(trues, preds):
            table[pred, true] += 1
    else:
        if len(predictions.shape) == 2:
            # in this case, we require the class listing
            if classes is None:
                raise AmbiguousProbabilisticForecastsException(
                    truths, predictions)
            preds = np.take(classes, np.argmax(predictions, axis=1))
        else:
            preds = predictions
        # Truths and predictions are now both deterministic
        if classes is None:
            classes = np.unique(np.append(np.unique(truths), np.unique(preds)))
        table = np.zeros((len(classes), len(classes)), dtype=np.float32)
        for i, c1 in enumerate(classes):
            for j, c2 in enumerate(classes):
                table[i, j] = [p == c1 and t == c2 for p,
                               t in zip(preds, truths)].count(True)
    return table


def _peirce_skill_score(table):
    """This score is borrowed with modification from the hagelslag repository
    MulticlassContingencyTable class. It is used here with permission of
    David John Gagne II <djgagne@ou.edu>

    Multiclass Peirce Skill Score (also Hanssen and Kuipers score, True Skill Score)
    """
    n = float(table.sum())
    nf = table.sum(axis=1)
    no = table.sum(axis=0)
    correct = float(table.trace())
    return (correct / n - (nf * no).sum() / n ** 2) / (1 - (no * no).sum() / n ** 2)


def _heidke_skill_score(table):
    """This score is borrowed with modification from the hagelslag repository
    MulticlassContingencyTable class. It is used here with permission of
    David John Gagne II <djgagne@ou.edu>
    """
    n = float(table.sum())
    nf = table.sum(axis=1)
    no = table.sum(axis=0)
    correct = float(table.trace())
    return (correct / n - (nf * no).sum() / n ** 2) / (1 - (nf * no).sum() / n ** 2)


def _gerrity_score(table):
    """This score is borrowed with modification from the hagelslag repository
    MulticlassContingencyTable class. It is used here with permission of
    David John Gagne II <djgagne@ou.edu>

    Gerrity Score, which weights each cell in the contingency table by its observed relative frequency.
    """
    k = table.shape[0]
    n = float(table.sum())
    p_o = table.sum(axis=0) / n
    p_sum = np.cumsum(p_o)[:-1]
    a = (1.0 - p_sum) / p_sum
    s = np.zeros(table.shape, dtype=float)
    for (i, j) in np.ndindex(*s.shape):
        if i == j:
            s[i, j] = 1.0 / (k - 1.0) * \
                (np.sum(1.0 / a[0:j]) + np.sum(a[j:k-1]))
        elif i < j:
            s[i, j] = 1.0 / (k - 1.0) * (np.sum(1.0 / a[0:i]
                                                ) - (j - i) + np.sum(a[j:k-1]))
        else:
            s[i, j] = s[j, i]
    return np.sum(table / float(table.sum()) * s)
