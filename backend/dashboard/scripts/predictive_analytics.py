from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import pandas as pd

# Load the data
data = pd.read_csv('financial_data.csv')

# Prepare features and target
X = data[['Traditional_ROI', 'ESG_Score', 'Volatility']]
y = data['ESG_ROI']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f'Mean Squared Error: {mse}')

# Save the model
joblib.dump(model, '../../data_model/esg_model.pkl')

print("Model trained and saved.")
