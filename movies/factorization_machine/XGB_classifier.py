
from sklearn.compose._column_transformer import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing._encoders import OneHotEncoder
from xgboost import XGBClassifier

from scipy.stats import uniform, randint

from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, classification_report)

from sklearn.model_selection import RandomizedSearchCV

import joblib
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


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
        'n_estimators': [100],
        'max_depth': randint(3, 8),
        'learning_rate': uniform(0.01, 0.2),
        'subsample': uniform(0.7, 0.3),
        'colsample_bytree': uniform(0.7, 0.3),
        'min_child_weight': randint(1, 7),
        'gamma': uniform(0, 0.5),
        'reg_alpha': uniform(0, 1),
        'reg_lambda': uniform(0, 1),
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

        total_size = len(self.df)
        test_size = int(total_size * self.test_size)
        validation_size = int(total_size * self.val_size)
        train_size = total_size - test_size - validation_size

        df_train = self.df.iloc[:train_size]
        df_validation = self.df.iloc[train_size:train_size + validation_size]
        df_test = self.df.iloc[train_size + validation_size:]

        categorical_cols = ["User", "Movie"]
        numerical_cols = self.features.difference(categorical_cols + [self.target])

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
                ("num", "passthrough", numerical_cols),
            ]
        )

        return df_train, df_validation, df_test, preprocessor

    def train(self):
        """Train the model and evaluate performance"""
        df_train, df_validation, df_test, preprocessor = self.prepare_data()

        # Adjust target values to 0-based indexing for XGBoost
        df_train = df_train.copy()
        df_validation = df_validation.copy()
        df_test = df_test.copy()

        df_train[self.target] = df_train[self.target] - 1
        df_validation[self.target] = df_validation[self.target] - 1
        df_test[self.target] = df_test[self.target] - 1

        base_model = XGBClassifier(objective='multi:softmax', num_class=5)
        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", base_model)])

        param_grid = {f"classifier__{key}": value for key, value in self.param_grid.items()}

        random_search = RandomizedSearchCV(
            estimator=pipeline,
            param_distributions=param_grid,
            n_iter=self.iters,
            scoring='accuracy',
            verbose=1,
            n_jobs=-1,
            random_state=self.random_state,
            cv=3
        )

        print("Performing random search for best parameters...")
        random_search.fit(df_train[self.features], df_train[self.target])

        best_params = {k.replace('classifier__', ''): v
                       for k, v in random_search.best_params_.items()}
        print(f"Best parameters found: {best_params}")

        best_model = XGBClassifier(
            **best_params,
            objective='multi:softmax',
            num_class=5
        )

        final_pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", best_model)])

        print("Training final model...")
        final_pipeline.fit(df_train[self.features], df_train[self.target])

        def evaluate_predictions(y_true, y_pred, set_name):
            # Convert back to 1-5 scale
            y_true = y_true + 1
            y_pred = y_pred + 1

            print(f"\n{set_name} Performance:")
            print(f"Accuracy: {accuracy_score(y_true, y_pred):.3f}")
            print(f"Precision: {precision_score(y_true, y_pred, average='weighted'):.3f}")
            print(f"Recall: {recall_score(y_true, y_pred, average='weighted'):.3f}")
            print(f"F1 Score: {f1_score(y_true, y_pred, average='weighted'):.3f}")
            print("\nClassification Report:")
            print(classification_report(y_true, y_pred))

        for df_eval, name in [(df_train, "Training"),
                              (df_validation, "Validation"),
                              (df_test, "Test")]:
            y_pred = final_pipeline.predict(df_eval[self.features])
            evaluate_predictions(df_eval[self.target], y_pred, name)

        if self.save:
            joblib.dump(final_pipeline, os.path.join(BASE_DIR, 'movies/best_pipeline.pkl'))

        return final_pipeline


    def predict(self,X,y):
        pass


