import copy
import pytest
from deepforest._layer import Layer
from deepforest._estimator import Estimator

# Load utils
from sklearn.ensemble._hist_gradient_boosting.binning import _BinMapper
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split


# Load data and binning
X, y = load_digits(return_X_y=True)
binner = _BinMapper(random_state=142)
X_binned = binner.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_binned, y, test_size=0.42, random_state=42
)

# Parameters
layer_kwargs = {
    "layer_idx": 0,
    "n_classes": 10,
    "n_estimators": 1,
    "n_trees": 10,
    "max_depth": 3,
    "min_samples_leaf": 10,
    "partial_mode": False,
    "buffer": None,
    "n_jobs": -1,
    "random_state": 42,
    "verbose": 2,
}

estimator_kwargs = {
    "name": "rf",
    "n_trees": 10,
    "max_depth": 3,
    "min_samples_leaf": 10,
    "n_jobs": -1,
    "random_state": 42,
}


def test_layer_properties_after_fitting():

    layer = Layer(**layer_kwargs)
    X_aug = layer.fit_transform(X_train, y_train)
    y_pred_full = layer.predict_full(X_test)

    # n_trees
    assert (
        layer.n_trees_
        == 2 * layer_kwargs["n_estimators"] * layer_kwargs["n_trees"]
    )

    # Output dim
    expect_dim = 2 * layer_kwargs["n_classes"] * layer_kwargs["n_estimators"]
    assert X_aug.shape[1] == expect_dim
    assert y_pred_full.shape[1] == expect_dim


@pytest.mark.parametrize(
    "param", [(0, {"n_estimators": 0}), (1, {"n_trees": 0})]
)
def test_layer_invalid_training_params(param):
    case_kwargs = copy.deepcopy(layer_kwargs)
    case_kwargs.update(param[1])

    layer = Layer(**case_kwargs)

    if param[0] == 0:
        err_msg = "`n_estimators` = 0 should be strictly positive."
    elif param[0] == 1:
        err_msg = "`n_trees` = 0 should be strictly positive."

    with pytest.raises(ValueError, match=err_msg):
        layer.fit_transform(X_train, y_train)


def test_estimator_unknown():
    case_kwargs = copy.deepcopy(estimator_kwargs)
    case_kwargs.update({"name": "unknown"})

    err_msg = "Unknown type of estimator, which should be one of {{rf, erf}}."
    with pytest.raises(NotImplementedError, match=err_msg):
        Estimator(**case_kwargs)
