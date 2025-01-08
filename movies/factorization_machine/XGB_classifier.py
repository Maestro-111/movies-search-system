from imblearn.under_sampling._prototype_selection._tomek_links import TomekLinks
from sklearn.compose._column_transformer import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.preprocessing._encoders import OneHotEncoder
from xgboost import XGBClassifier,callback

from scipy.stats import uniform, randint

from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, classification_report)

from sklearn.model_selection import RandomizedSearchCV

import joblib
import os
from pathlib import Path

from config.logger_config import model_logger
import matplotlib.pyplot as plt

from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.pipeline import Pipeline as ImbPipeline

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class EvalHistory(callback.TrainingCallback):

    def __init__(self):
        self.history = {}

    def after_iteration(self, model, epoch, evals_log):
        for key, metrics in evals_log.items():
            for metric_name, value in metrics.items():
                if key not in self.history:
                    self.history[key] = {}
                if metric_name not in self.history[key]:
                    self.history[key][metric_name] = []
                self.history[key][metric_name].append(value[-1])
        return False


class CustomEarlyStopping:
    def __init__(self, tolerance=5, verbose=True):
        """
        Initialize early stopping for classification.

        Args:
            tolerance (int): Number of epochs to wait for improvement
            verbose (bool): Whether to print stopping information
        """
        self.tolerance = tolerance
        self.verbose = verbose
        self.best_score = None
        self.counter = 0

    def __call__(self, env):
        eval_result = env.evaluation_result_list

        # Get validation accuracy (assuming it's the second metric)
        current_score = eval_result[1][1]

        if self.best_score is None:
            self.best_score = current_score
        elif current_score < self.best_score:
            self.counter += 1
            if self.verbose:
                print(f"EarlyStopping counter: {self.counter} out of {self.tolerance}")
            if self.counter >= self.tolerance:
                if self.verbose:
                    print("Early stopping triggered")
                return True
        else:
            self.best_score = current_score
            self.counter = 0

        return False


class MovieRatingXGB:

    """
    XGBoost classifier for movie rating prediction
    """

    param_grid = {
        'n_estimators': [80],
        'max_depth': [2],  #randint(3, 8),
        'learning_rate': uniform(0.01, 0.2),
        'subsample': [1],
        'colsample_bytree': uniform(0.7, 0.3),
        'min_child_weight': randint(5, 30),
        'gamma': [0,1,5],
        'reg_alpha': uniform(0, 50),
        'reg_lambda': uniform(0, 50),
    }

    def __init__(self, df, target:str, test_size=0.2, val_size=0.1,
                 iters=20, tolerance=5, random_state=42, save=False):
        """
        Initialize the movie rating classifier.

        Args:
            df (DataFrame): Input DataFrame with features and target
            features (list): List of feature column names
            target (str): Target column name
            test_size (float): Proportion of data for testing
            val_size (float): Proportion of data for validation
            iters (int): Number of iterations for random search
            tolerance (int): Early stopping tolerance
            random_state (int): Random seed
        """

        self.df = df
        self.target = target
        self.features = df.columns.difference([target])
        self.test_size = test_size
        self.val_size = val_size
        self.iters = iters
        self.tolerance = tolerance
        self.random_state = random_state
        self.save = save

    def prepare_data(self):
        """Split data into train, validation, and test sets"""

        df  = self.df.sample(frac=1).reset_index(drop=True)

        total_size = len(df)
        test_size = int(total_size * self.test_size)

        validation_size = int(total_size * self.val_size)
        train_size = total_size - test_size - validation_size

        df_train = df.iloc[:train_size]
        df_validation = df.iloc[train_size:train_size + validation_size]
        df_test = df.iloc[train_size + validation_size:]

        categorical_cols = ["User", "Movie"]
        numerical_cols = self.features.difference(categorical_cols + [self.target])

        preprocessor = ColumnTransformer(
            transformers = [
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
                ("num", "passthrough", numerical_cols),
            ]
        )

        return df_train, df_validation, df_test, preprocessor

    def train(self):

        """Train the model and evaluate performance with SMOTE"""

        df_train, df_validation, df_test, preprocessor = self.prepare_data()

        df_train = df_train.copy()
        df_validation = df_validation.copy()
        df_test = df_test.copy()

        df_train[self.target] = df_train[self.target] - 1
        df_validation[self.target] = df_validation[self.target] - 1
        df_test[self.target] = df_test[self.target] - 1

        X_train = preprocessor.fit_transform(df_train[self.features])
        y_train = df_train[self.target]

        X_validation = preprocessor.transform(df_validation[self.features])
        y_validation = df_validation[self.target]

        smote = ADASYN(random_state=self.random_state)

        x_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

        eval_set = [(x_train_resampled, y_train_resampled), (X_validation, y_validation)]
        base_model = XGBClassifier(objective='multi:softmax', num_class=5)

        random_search = RandomizedSearchCV(
            estimator=base_model,
            param_distributions=self.param_grid,
            n_iter=self.iters,
            scoring='recall_weighted',
            verbose=1,
            n_jobs=-1,
            cv=10
        )

        model_logger.info("Performing random search for best parameters...")
        random_search.fit(x_train_resampled, y_train_resampled)

        best_params = random_search.best_params_
        model_logger.info(f"Best parameters found: {best_params}")

        best_model = XGBClassifier(
            **best_params,
            objective='multi:softmax',
            eval_metric="mlogloss"
        )

        best_model.fit(
            x_train_resampled,
            y_train_resampled,
            eval_set=eval_set,
            verbose=1
        )

        eval_results = best_model.evals_result()
        if "validation_0" in eval_results and "validation_1" in eval_results:
            epochs = range(len(eval_results["validation_0"]["mlogloss"]))
            plt.figure(figsize=(10, 6))
            plt.plot(epochs, eval_results["validation_0"]["mlogloss"], label="Train")
            plt.plot(epochs, eval_results["validation_1"]["mlogloss"], label="Validation")
            plt.xlabel("Epoch")
            plt.ylabel("Log Loss")
            plt.title("XGBoost Log Loss with SMOTE")
            plt.legend()
            plt.grid()
            plt.show()

        final_pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", best_model),
        ])

        def evaluate_predictions(y_true, y_pred, set_name):

            y_true = y_true + 1
            y_pred = y_pred + 1

            model_logger.info(f"\n{set_name} Performance:")
            model_logger.info(f"Accuracy: {accuracy_score(y_true, y_pred):.3f}")
            model_logger.info(f"Precision: {precision_score(y_true, y_pred, average='weighted'):.3f}")
            model_logger.info(f"Recall: {recall_score(y_true, y_pred, average='weighted'):.3f}")
            model_logger.info(f"F1 Score: {f1_score(y_true, y_pred, average='weighted'):.3f}")
            model_logger.info("\nClassification Report:")
            model_logger.info(classification_report(y_true, y_pred))

        for df_eval, name in [(df_train, "Training"),
                              (df_validation, "Validation"),
                              (df_test, "Test")]:
            y_pred = final_pipeline.predict(df_eval[self.features])
            evaluate_predictions(df_eval[self.target], y_pred, name)

        if self.save:
            joblib.dump(final_pipeline, os.path.join(BASE_DIR, 'movies/factorization_machine/best_pipeline.pkl'))


