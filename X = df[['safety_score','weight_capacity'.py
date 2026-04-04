X = df[['safety_score','weight_capacity','biodegradability']]
y_cost = df['Cost']
y_co2 = df['co2_emission']
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# split data
X_train, X_test, y_train, y_test = train_test_split(X, y_cost, test_size=0.3)

# train
model = LinearRegression()
model.fit(X_train, y_train)

# predict
pred = model.predict(X_test)

print(pred)