
from sklearn.compose._column_transformer import ColumnTransformer
from sklearn.metrics._ranking import ndcg_score
from sklearn.pipeline import Pipeline

from sklearn.preprocessing._encoders import OneHotEncoder
from xgboost import callback, XGBRanker

import joblib
import pickle
import os
from pathlib import Path

from config.logger_config import model_logger
import matplotlib.pyplot as plt

from scipy.stats import uniform, randint
import numpy as np

import pickle

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


class MovieRankingXGB:
    """
    XGBoost ranker for movie rating prediction
    """

    param_grid = {
        'n_estimators': [50,60,70,80,90,100],  # Increased from 80
        'max_depth': [2,3,4],  # Slightly increased complexity
        'learning_rate': uniform(0.01, 0.1),  # Narrowed range
        'subsample': uniform(0.8, 0.2),  # Added randomness
        'colsample_bytree': uniform(0.8, 0.2),
        'min_child_weight': randint(1, 10),  # Reduced to allow more splits
        'gamma': [0, 0.1, 0.2],  # More granular values
        'reg_alpha': uniform(0, 10),  # Reduced range
        'reg_lambda': uniform(0, 10),
    }

    def __init__(self, df, target='Rating', test_size=0.2, val_size=0.1,
                 iters=20, random_state=42, save=False):
        self.df = df
        self.target = target
        self.features = df.columns.difference([target, 'User'])
        self.test_size = test_size
        self.val_size = val_size
        self.iters = iters
        self.random_state = random_state
        self.save = save

    def prepare_data(self):
        """Split data into train, validation, and test sets, preserving user groups"""
        df = self.df.sample(frac=1, random_state=self.random_state).reset_index(drop=True)

        # Sort by user to ensure proper grouping
        df = df.sort_values('User')
        unique_users = df['User'].unique()
        np.random.seed(self.random_state)
        np.random.shuffle(unique_users)

        n_users = len(unique_users)
        n_test = int(n_users * self.test_size)
        n_val = int(n_users * self.val_size)

        test_users = unique_users[:n_test]
        val_users = unique_users[n_test:n_test + n_val]
        train_users = unique_users[n_test + n_val:]

        df_train = df[df['User'].isin(train_users)]
        df_validation = df[df['User'].isin(val_users)]
        df_test = df[df['User'].isin(test_users)]

        categorical_cols = ["Movie"]
        numerical_cols = self.features.difference(categorical_cols + [self.target])

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
                ("num", "passthrough", numerical_cols),
            ]
        )

        return df_train, df_validation, df_test, preprocessor

    def train(self):
        """Train the ranking model and evaluate performance"""
        df_train, df_validation, df_test, preprocessor = self.prepare_data()

        X_train = preprocessor.fit_transform(df_train[self.features])
        y_train = df_train[self.target]
        groups_train = df_train['User']

        X_validation = preprocessor.transform(df_validation[self.features])
        y_validation = df_validation[self.target]
        groups_validation = df_validation['User']

        # Get group counts
        group_counts_train = groups_train.value_counts().sort_index().values
        group_counts_val = groups_validation.value_counts().sort_index().values

        best_score = float('-inf')
        best_params = None

        model_logger.info("Starting parameter search...")

        # Generate parameter combinations
        param_combinations = []
        for _ in range(self.iters):
            params = {
                'n_estimators': np.random.choice(self.param_grid['n_estimators']),
                'max_depth': np.random.choice(self.param_grid['max_depth']),
                'learning_rate': np.random.uniform(0.01, 0.1),
                'subsample': np.random.uniform(0.8, 1.0),
                'colsample_bytree': np.random.uniform(0.8, 1.0),
                'min_child_weight': np.random.randint(1, 10),
                'gamma': np.random.choice(self.param_grid['gamma']),
                'reg_alpha': np.random.uniform(0, 10),
                'reg_lambda': np.random.uniform(0, 10),
            }
            param_combinations.append(params)

        for params in param_combinations:

            model = XGBRanker(
                objective='rank:pairwise',
                random_state=self.random_state,
                eval_metric=['ndcg@5'],
                lambdarank_pair_method = "topk",
                **params
            )

            model.fit(
                X_train,
                y_train,
                group=group_counts_train,
                eval_set=[(X_validation, y_validation)],
                eval_group=[group_counts_val],
                verbose=False
            )

            val_pred = model.predict(X_validation)
            ndcg_scores = []
            start_idx = 0

            for group_size in group_counts_val:
                end_idx = start_idx + group_size
                group_true = y_validation[start_idx:end_idx]
                group_pred = val_pred[start_idx:end_idx]
                ndcg_scores.append(ndcg_score([group_true], [group_pred], k=5))
                start_idx = end_idx

            mean_ndcg = np.mean(ndcg_scores)

            if mean_ndcg > best_score:
                best_score = mean_ndcg
                best_params = params
                model_logger.info(f"New best score: {best_score:.3f} with params: {best_params}")

        model_logger.info(f"Training final model with best parameters: {best_params}")
        eval_history = EvalHistory()

        best_model = XGBRanker(
            objective='rank:pairwise',
            random_state=self.random_state,
            eval_metric=['ndcg@5'],
            callbacks=[eval_history],
            lambdarank_pair_method="topk",
            **best_params
        )

        best_model.fit(
            X_train,
            y_train,
            group=group_counts_train,
            eval_set=[(X_train, y_train), (X_validation, y_validation)],
            eval_group=[group_counts_train, group_counts_val],
            verbose=True
        )

        plt.figure(figsize=(10, 6))
        for key in eval_history.history:
            for metric, values in eval_history.history[key].items():
                plt.plot(values, label=f'{key}-{metric}')
        plt.xlabel("Iteration")
        plt.ylabel("NDCG@5")
        plt.title("XGBoost Ranking Model Training Progress")
        plt.legend()
        plt.grid()
        plt.show()

        # X_combined = np.vstack([X_train, X_validation])
        # y_combined = np.hstack([y_train, y_validation])
        # group_counts_combined = np.concatenate([group_counts_train, group_counts_val])


        best_model = XGBRanker(
            objective='rank:pairwise',
            random_state=self.random_state,
            eval_metric=['ndcg@5'],
            lambdarank_pair_method="topk",
            **best_params
        )

        best_model.fit(
            X_train,
            y_train,
            group=group_counts_train,
            verbose=True
        )

        final_pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("ranker", best_model),
        ])

        def evaluate_predictions(df_eval, pipeline, set_name):

            predictions = pipeline.predict(df_eval[self.features])
            ndcg_scores = []

            for user in df_eval['User'].unique():
                user_mask = df_eval['User'] == user
                user_true = df_eval.loc[user_mask, self.target]
                user_pred = predictions[user_mask]
                ndcg_scores.append(ndcg_score([user_true], [user_pred], k=5))

            mean_ndcg = np.mean(ndcg_scores)
            model_logger.info(f"\n{set_name} Performance:")
            model_logger.info(f"Mean NDCG@5: {mean_ndcg:.3f}")
            model_logger.info(f"Min NDCG@5: {min(ndcg_scores):.3f}")
            model_logger.info(f"Max NDCG@5: {max(ndcg_scores):.3f}")

        # Evaluate on all sets
        for df_eval, name in [(df_train, "Training"),
                              (df_validation, "Validation"),
                              (df_test, "Test")]:
            evaluate_predictions(df_eval, final_pipeline, name)


        if self.save:
            with open(os.path.join(BASE_DIR, 'movies/factorization_machine/best_pipeline.pkl'), 'wb') as f:
                pickle.dump(final_pipeline, f)



