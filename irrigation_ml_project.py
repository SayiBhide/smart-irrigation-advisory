# ================================================================
# AI-BASED SMART IRRIGATION ADVISORY SYSTEM
# COMPLETE MACHINE LEARNING IMPLEMENTATION
#
# Models:
# 1. Random Forest
# 2. Decision Tree
# 3. XGBoost
# 4. SVM
#
# Evaluation:
# Accuracy, Precision, Recall, F1-Score, MSE, R2
#
# Additional:
# - Dataset inspection
# - Preprocessing
# - 80/20 train-test split
# - Model comparison
# - Confusion matrices
# - Cross-validation
# - Feature importance
# - Comparison graphs
# - Final model selection
# - Save final model
# - Sample irrigation prediction
# - Simple farmer-friendly advisory
# ================================================================


# ================================================================
# 1. IMPORT REQUIRED LIBRARIES
# ================================================================

import os
import warnings
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_squared_error,
    r2_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report
)

from xgboost import XGBClassifier


warnings.filterwarnings("ignore")


# ================================================================
# 2. FILE SETTINGS
# ================================================================

# IMPORTANT:
# Keep the Excel file in the SAME folder as this Python file.

DATA_FILE = "irrigation_prediction cepdt final(1).xlsx"

SHEET_NAME = "irrigation_prediction(1)"

TARGET_COLUMN = "Irrigation_Need"


# ================================================================
# 3. CREATE OUTPUT FOLDER
# ================================================================

OUTPUT_FOLDER = "ML_Results"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("\n")
print("=" * 70)
print("AI-BASED SMART IRRIGATION ADVISORY SYSTEM")
print("COMPLETE ML IMPLEMENTATION")
print("=" * 70)


# ================================================================
# 4. CHECK WHETHER DATASET EXISTS
# ================================================================

if not os.path.exists(DATA_FILE):

    print("\nERROR:")
    print("Excel dataset was not found.")
    print("\nMake sure this file is in the same folder as this Python file:")
    print(DATA_FILE)

    input("\nPress Enter to exit...")
    raise SystemExit


print("\n[1/12] Loading dataset...")


# ================================================================
# 5. LOAD DATASET
# ================================================================

df = pd.read_excel(
    DATA_FILE,
    sheet_name=SHEET_NAME
)

print("\nDataset successfully loaded.")

print("Number of rows    :", df.shape[0])
print("Number of columns :", df.shape[1])


# ================================================================
# 6. BASIC DATASET INSPECTION
# ================================================================

print("\n")
print("-" * 70)
print("DATASET INFORMATION")
print("-" * 70)

print("\nColumn names:")
print(df.columns.tolist())


print("\nMissing values:")
print(df.isnull().sum())


print("\nTarget variable distribution:")
print(df[TARGET_COLUMN].value_counts())


# Save dataset information
dataset_info = pd.DataFrame({
    "Column": df.columns,
    "Data_Type": df.dtypes.astype(str).values,
    "Missing_Values": df.isnull().sum().values
})

dataset_info.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "dataset_information.csv"
    ),
    index=False
)


# ================================================================
# 7. DEFINE FEATURES
# ================================================================

print("\n[2/12] Preparing features...")


# Numerical agricultural/environmental features

NUMERIC_COLUMNS = [

    "Soil_pH",

    "Soil_Moisture",

    "Organic_Carbon",

    "Electrical_Conductivity",

    "Temperature_C",

    "Humidity",

    "Rainfall_mm",

    "Sunlight_Hours",

    "Wind_Speed_kmh",

    "Field_Area_hectare",

    "Previous_Irrigation_mm"

]


# Categorical agricultural features

CATEGORICAL_COLUMNS = [

    "Soil_Type",

    "Crop_Type",

    "Crop_Growth_Stage",

    "Season",

    "Irrigation_Type",

    "Water_Source",

    "Mulching_Used",

    "Region"

]


# We intentionally exclude State because the uploaded dataset
# contains the same State value for all records.

FEATURE_COLUMNS = (
    NUMERIC_COLUMNS +
    CATEGORICAL_COLUMNS
)


# Check that all required columns exist

missing_columns = [
    col for col in FEATURE_COLUMNS + [TARGET_COLUMN]
    if col not in df.columns
]

if len(missing_columns) > 0:

    print("\nERROR: These columns are missing from the dataset:")

    for col in missing_columns:
        print("-", col)

    input("\nPress Enter to exit...")
    raise SystemExit


X = df[FEATURE_COLUMNS].copy()


# ================================================================
# 8. ENCODE TARGET VARIABLE
# ================================================================

print("\n[3/12] Encoding target variable...")


# IMPORTANT:
#
# Low    = 0
# Medium = 1
# High   = 2
#
# This ordering is important because MSE and R2 are also calculated.

TARGET_MAPPING = {

    "Low": 0,

    "Medium": 1,

    "High": 2

}


y = df[TARGET_COLUMN].map(TARGET_MAPPING)


# Check whether any target values failed to map

if y.isnull().any():

    print("\nERROR: Unknown target values found.")

    print(
        df.loc[
            y.isnull(),
            TARGET_COLUMN
        ].unique()
    )

    input("\nPress Enter to exit...")
    raise SystemExit


y = y.astype(int)


print("\nTarget encoding:")

print("Low    = 0")
print("Medium = 1")
print("High   = 2")


# ================================================================
# 9. TRAIN / TEST SPLIT
# ================================================================

print("\n[4/12] Splitting dataset...")


X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.20,

    random_state=42,

    stratify=y

)


print("\nTraining records :", len(X_train))
print("Testing records  :", len(X_test))


# ================================================================
# 10. PREPROCESSING PIPELINE
# ================================================================

print("\n[5/12] Creating preprocessing pipeline...")


# Numerical preprocessing:
# Missing values -> median
# Scaling -> StandardScaler

numeric_pipeline = Pipeline([

    (
        "imputer",
        SimpleImputer(
            strategy="median"
        )
    ),

    (
        "scaler",
        StandardScaler()
    )

])


# Categorical preprocessing:
# Missing values -> most frequent
# Categories -> One Hot Encoding

categorical_pipeline = Pipeline([

    (
        "imputer",
        SimpleImputer(
            strategy="most_frequent"
        )
    ),

    (
        "onehot",
        OneHotEncoder(
            handle_unknown="ignore"
        )
    )

])


# Combine both pipelines

preprocessor = ColumnTransformer([

    (
        "numeric",
        numeric_pipeline,
        NUMERIC_COLUMNS
    ),

    (
        "categorical",
        categorical_pipeline,
        CATEGORICAL_COLUMNS
    )

])


# ================================================================
# 11. DEFINE FOUR MACHINE LEARNING MODELS
# ================================================================

print("\n[6/12] Creating four ML models...")


models = {

    "Random Forest":

        RandomForestClassifier(

            n_estimators=200,

            random_state=42,

            n_jobs=-1

        ),


    "Decision Tree":

        DecisionTreeClassifier(

            max_depth=8,

            random_state=42

        ),


    "XGBoost":

        XGBClassifier(

            n_estimators=200,

            max_depth=5,

            learning_rate=0.1,

            subsample=0.9,

            colsample_bytree=0.9,

            eval_metric="mlogloss",

            random_state=42,

            n_jobs=-1

        ),


    "SVM":

        SVC(

            kernel="rbf",

            C=10,

            gamma="scale",

            probability=True,

            random_state=42

        )

}


# ================================================================
# 12. TRAIN AND EVALUATE ALL FOUR MODELS
# ================================================================

print("\n[7/12] Training four ML models...")

print("\nThis may take a little time, especially for SVM.")

print("\n")


results = {}

trained_models = {}

predictions = {}

classification_reports = {}


for model_name, model in models.items():

    print("=" * 70)

    print("TRAINING:", model_name)

    print("=" * 70)


    # Create complete pipeline

    pipeline = Pipeline([

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )

    ])


    # ------------------------------------------------------------
    # TRAIN
    # ------------------------------------------------------------

    pipeline.fit(
        X_train,
        y_train
    )


    # ------------------------------------------------------------
    # PREDICT
    # ------------------------------------------------------------

    y_pred = pipeline.predict(
        X_test
    )


    # Store trained model

    trained_models[model_name] = pipeline

    predictions[model_name] = y_pred


    # ------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )


    precision = precision_score(

        y_test,

        y_pred,

        average="weighted",

        zero_division=0

    )


    recall = recall_score(

        y_test,

        y_pred,

        average="weighted",

        zero_division=0

    )


    f1 = f1_score(

        y_test,

        y_pred,

        average="weighted",

        zero_division=0

    )


    mse = mean_squared_error(

        y_test,

        y_pred

    )


    r2 = r2_score(

        y_test,

        y_pred

    )


    # Store results

    results[model_name] = {

        "Accuracy": accuracy,

        "Precision": precision,

        "Recall": recall,

        "F1-Score": f1,

        "MSE": mse,

        "R2": r2

    }


    # Classification report

    report = classification_report(

        y_test,

        y_pred,

        target_names=[
            "Low",
            "Medium",
            "High"
        ],

        output_dict=True,

        zero_division=0

    )


    classification_reports[model_name] = report


    # ------------------------------------------------------------
    # PRINT RESULTS
    # ------------------------------------------------------------

    print("\nAccuracy  :", round(accuracy, 4))

    print("Precision :", round(precision, 4))

    print("Recall    :", round(recall, 4))

    print("F1-Score  :", round(f1, 4))

    print("MSE       :", round(mse, 4))

    print("R2        :", round(r2, 4))


    print("\nClassification Report:")

    print(

        classification_report(

            y_test,

            y_pred,

            target_names=[
                "Low",
                "Medium",
                "High"
            ],

            zero_division=0

        )

    )


# ================================================================
# 13. CREATE FINAL MODEL COMPARISON TABLE
# ================================================================

print("\n[8/12] Creating model comparison table...")


results_df = pd.DataFrame(
    results
).T


# Add percentage versions for easier presentation

results_df["Accuracy_%"] = (
    results_df["Accuracy"] * 100
)

results_df["Precision_%"] = (
    results_df["Precision"] * 100
)

results_df["Recall_%"] = (
    results_df["Recall"] * 100
)

results_df["F1-Score_%"] = (
    results_df["F1-Score"] * 100
)


# Round values

results_df = results_df.round(4)


print("\n")
print("=" * 70)

print("FINAL MODEL COMPARISON")

print("=" * 70)

print(results_df)


# Save comparison table

results_df.to_csv(

    os.path.join(

        OUTPUT_FOLDER,

        "model_comparison_results.csv"

    )

)


# ================================================================
# 14. SELECT BEST MODEL
# ================================================================

print("\n[9/12] Selecting optimum model...")


# PRIMARY SELECTION CRITERION:
#
# Weighted F1-score
#
# Accuracy, Precision and other metrics are considered
# supplementary evaluation measures.

best_model_name = (

    results_df["F1-Score"]

    .idxmax()

)


best_model = trained_models[
    best_model_name
]

best_predictions = predictions[
    best_model_name
]


print("\n")
print("=" * 70)

print("OPTIMUM MODEL")

print("=" * 70)

print(
    "\nSelected model:",
    best_model_name
)

print(
    "\nReason:"
)

print(
    "It achieved the highest weighted F1-score "
    "among the four evaluated models."
)


# ================================================================
# 15. SAVE FINAL MODEL
# ================================================================

joblib.dump(

    best_model,

    os.path.join(

        OUTPUT_FOLDER,

        "final_irrigation_model.pkl"

    )

)


print(
    "\nFinal trained model saved as:"
)

print(
    os.path.join(
        OUTPUT_FOLDER,
        "final_irrigation_model.pkl"
    )
)


# ================================================================
# 16. SAVE TARGET MAPPING
# ================================================================

joblib.dump(

    TARGET_MAPPING,

    os.path.join(

        OUTPUT_FOLDER,

        "target_mapping.pkl"

    )

)


# ================================================================
# 17. CONFUSION MATRIX FOR BEST MODEL
# ================================================================

print("\n[10/12] Creating confusion matrix...")


cm = confusion_matrix(

    y_test,

    best_predictions

)


print("\nConfusion Matrix:")

print(cm)


plt.figure(
    figsize=(7, 6)
)


disp = ConfusionMatrixDisplay(

    confusion_matrix=cm,

    display_labels=[
        "Low",
        "Medium",
        "High"
    ]

)


disp.plot()

plt.title(
    "Confusion Matrix - " +
    best_model_name
)

plt.tight_layout()


plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "confusion_matrix_best_model.png"

    ),

    dpi=300

)


plt.close()


# ================================================================
# 18. CREATE MODEL COMPARISON GRAPHS
# ================================================================

print("\nCreating comparison graphs...")


metrics_for_graph = [

    "Accuracy",

    "Precision",

    "Recall",

    "F1-Score"

]


for metric in metrics_for_graph:

    plt.figure(
        figsize=(8, 5)
    )

    values = (
        results_df[metric] * 100
    )

    plt.bar(
        results_df.index,
        values
    )

    plt.ylabel(
        metric + " (%)"
    )

    plt.xlabel(
        "Machine Learning Model"
    )

    plt.title(
        metric +
        " Comparison of ML Models"
    )

    plt.xticks(
        rotation=15
    )

    plt.ylim(
        0,
        100
    )

    plt.tight_layout()


    filename = (

        metric.lower()
        .replace("-", "_")
        +
        "_comparison.png"

    )


    plt.savefig(

        os.path.join(

            OUTPUT_FOLDER,

            filename

        ),

        dpi=300

    )


    plt.close()


# ================================================================
# 19. MSE COMPARISON GRAPH
# ================================================================

plt.figure(
    figsize=(8, 5)
)


plt.bar(

    results_df.index,

    results_df["MSE"]

)


plt.ylabel(
    "Mean Squared Error"
)

plt.xlabel(
    "Machine Learning Model"
)

plt.title(
    "MSE Comparison of ML Models"
)

plt.xticks(
    rotation=15
)

plt.tight_layout()


plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "mse_comparison.png"

    ),

    dpi=300

)


plt.close()


# ================================================================
# 20. R2 COMPARISON GRAPH
# ================================================================

plt.figure(
    figsize=(8, 5)
)


plt.bar(

    results_df.index,

    results_df["R2"]

)


plt.ylabel(
    "R² Score"
)

plt.xlabel(
    "Machine Learning Model"
)

plt.title(
    "R² Comparison of ML Models"
)

plt.xticks(
    rotation=15
)

plt.tight_layout()


plt.savefig(

    os.path.join(

        OUTPUT_FOLDER,

        "r2_comparison.png"

    ),

    dpi=300

)


plt.close()


# ================================================================
# 21. CROSS-VALIDATION OF ALL FOUR MODELS
# ================================================================

print("\n[11/12] Performing 5-fold cross-validation...")


cv = StratifiedKFold(

    n_splits=5,

    shuffle=True,

    random_state=42

)


cv_results = {}


for model_name, model in models.items():

    print(
        "\nCross-validating:",
        model_name
    )


    pipeline = Pipeline([

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )

    ])


    scores = cross_val_score(

        pipeline,

        X,

        y,

        cv=cv,

        scoring="f1_weighted",

        n_jobs=1

    )


    cv_results[model_name] = {

        "Mean_F1": scores.mean(),

        "Std_F1": scores.std()

    }


    print(
        "Fold F1 scores:",
        np.round(scores, 4)
    )

    print(
        "Mean F1:",
        round(scores.mean(), 4)
    )

    print(
        "Std F1:",
        round(scores.std(), 4)
    )


cv_df = pd.DataFrame(
    cv_results
).T.round(4)


print("\n")
print("=" * 70)

print("5-FOLD CROSS-VALIDATION RESULTS")

print("=" * 70)

print(cv_df)


cv_df.to_csv(

    os.path.join(

        OUTPUT_FOLDER,

        "cross_validation_results.csv"

    )

)


# ================================================================
# 22. FEATURE IMPORTANCE
# ================================================================

print("\nGenerating feature importance...")


# Feature importance is available for Random Forest,
# Decision Tree and XGBoost.
#
# If XGBoost or Random Forest is selected,
# feature importance will be generated.

if best_model_name in [
    "Random Forest",
    "Decision Tree",
    "XGBoost"
]:

    model_inside_pipeline = (
        best_model.named_steps["model"]
    )


    preprocessor_inside_pipeline = (
        best_model.named_steps["preprocessor"]
    )


    feature_names = (
        preprocessor_inside_pipeline
        .get_feature_names_out()
    )


    importances = (
        model_inside_pipeline
        .feature_importances_
    )


    feature_importance_df = pd.DataFrame({

        "Feature": feature_names,

        "Importance": importances

    })


    feature_importance_df = (
        feature_importance_df
        .sort_values(
            "Importance",
            ascending=False
        )
    )


    # Save complete feature importance table

    feature_importance_df.to_csv(

        os.path.join(

            OUTPUT_FOLDER,

            "feature_importance.csv"

        ),

        index=False

    )


    # Print top 15

    print("\nTop 15 Important Features:")

    print(
        feature_importance_df
        .head(15)
        .to_string(index=False)
    )


    # Plot top 15

    top_features = (
        feature_importance_df
        .head(15)
        .sort_values(
            "Importance"
        )
    )


    plt.figure(
        figsize=(10, 7)
    )


    plt.barh(

        top_features["Feature"],

        top_features["Importance"]

    )


    plt.xlabel(
        "Feature Importance"
    )

    plt.ylabel(
        "Feature"
    )

    plt.title(

        "Top 15 Feature Importances - "
        + best_model_name

    )


    plt.tight_layout()


    plt.savefig(

        os.path.join(

            OUTPUT_FOLDER,

            "feature_importance_top15.png"

        ),

        dpi=300

    )


    plt.close()


# ================================================================
# 23. SAMPLE IRRIGATION PREDICTION
# ================================================================

print("\n[12/12] Testing final irrigation prediction...")


# Take one real unseen test record
# This demonstrates that the trained model can make
# a prediction for a field record.

sample_input = X_test.iloc[
    [0]
].copy()


sample_prediction = best_model.predict(
    sample_input
)[0]


# Convert numeric output back to class name

reverse_mapping = {

    0: "Low",

    1: "Medium",

    2: "High"

}


predicted_need = reverse_mapping[
    int(sample_prediction)
]


print("\n")
print("=" * 70)

print("SAMPLE IRRIGATION PREDICTION")

print("=" * 70)


print("\nInput agricultural conditions:")

print(
    sample_input.to_string(
        index=False
    )
)


print(
    "\nPredicted Irrigation Requirement:",
    predicted_need
)


# ================================================================
# 24. SIMPLE FARMER-FRIENDLY ADVISORY
# ================================================================

def generate_advisory(irrigation_need):

    if irrigation_need == "Low":

        return (
            "Low irrigation requirement. "
            "Immediate irrigation may not be necessary. "
            "Continue monitoring soil moisture and weather conditions."
        )

    elif irrigation_need == "Medium":

        return (
            "Medium irrigation requirement. "
            "Plan irrigation according to soil moisture, "
            "crop stage and upcoming weather conditions."
        )

    elif irrigation_need == "High":

        return (
            "High irrigation requirement. "
            "Irrigation should be considered soon, "
            "while checking rainfall forecast and field conditions."
        )

    else:

        return (
            "Unable to generate advisory."
        )


advisory = generate_advisory(
    predicted_need
)


print(
    "\nAdvisory:"
)

print(
    advisory
)


# ================================================================
# 25. SAVE SAMPLE PREDICTION
# ================================================================

prediction_output = sample_input.copy()

prediction_output[
    "Predicted_Irrigation_Need"
] = predicted_need

prediction_output[
    "Advisory"
] = advisory


prediction_output.to_csv(

    os.path.join(

        OUTPUT_FOLDER,

        "sample_irrigation_prediction.csv"

    ),

    index=False

)


# ================================================================
# 26. SAVE FINAL CLASSIFICATION REPORT
# ================================================================

final_report = classification_report(

    y_test,

    best_predictions,

    target_names=[
        "Low",
        "Medium",
        "High"
    ],

    zero_division=0

)


with open(

    os.path.join(

        OUTPUT_FOLDER,

        "final_classification_report.txt"

    ),

    "w"

) as file:

    file.write(
        "FINAL MODEL: " +
        best_model_name +
        "\n\n"
    )

    file.write(
        final_report
    )


# ================================================================
# 27. FINAL SUMMARY
# ================================================================

print("\n")
print("=" * 70)

print("PROJECT IMPLEMENTATION COMPLETED")

print("=" * 70)


print("\nFour models trained:")

print("1. Random Forest")

print("2. Decision Tree")

print("3. XGBoost")

print("4. SVM")


print(
    "\nSelected model:",
    best_model_name
)


print(
    "\nAll results and graphs have been saved in:"
)

print(
    os.path.abspath(
        OUTPUT_FOLDER
    )
)


print("\nGenerated files include:")

print(" - model_comparison_results.csv")

print(" - cross_validation_results.csv")

print(" - dataset_information.csv")

print(" - confusion_matrix_best_model.png")

print(" - accuracy_comparison.png")

print(" - precision_comparison.png")

print(" - recall_comparison.png")

print(" - f1_score_comparison.png")

print(" - mse_comparison.png")

print(" - r2_comparison.png")

print(" - feature_importance.csv")

print(" - feature_importance_top15.png")

print(" - final_classification_report.txt")

print(" - sample_irrigation_prediction.csv")

print(" - final_irrigation_model.pkl")

print(" - target_mapping.pkl")


print("\n")
print("=" * 70)

print("ML TRAINING AND EVALUATION FINISHED SUCCESSFULLY!")

print("=" * 70)


input(
    "\nPress Enter to close..."
)