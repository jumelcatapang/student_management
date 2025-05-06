import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load the CSV using an absolute path
csv_path = os.path.join(BASE_DIR, 'course_data.csv')
df = pd.read_csv(csv_path)

# Ensure column names are lowercase
df.columns = df.columns.str.lower()

# Encode categorical features
df['gender'] = df['gender'].map({'Male': 0, 'Female': 1})
df['interest'] = df['interest'].astype('category')
df['interest_code'] = df['interest'].cat.codes

# Save the interest encoding for later use
interest_mapping = dict(zip(df['interest'], df['interest_code']))
joblib.dump(interest_mapping, 'interest_mapping.joblib')

# Prepare training data
X = df[['age', 'gender', 'interest_code']]
y = df['course']

# Train model
model = DecisionTreeClassifier()
model.fit(X, y)

# Save the trained model
joblib.dump(model, 'course_predictor.joblib')

print("✅ Model trained and saved as 'course_predictor.joblib'")
