from keras.layers import Dense, Dropout
from keras.models import Sequential

def ConstructDenseNetwork(rows_count, cols_count):
    network = Sequential()
    network.add(Dense(rows_count * cols_count * 8, activation = "relu",
                        input_dim = rows_count * cols_count))
    network.add(Dense(rows_count * cols_count * 4, activation = "relu"))
    network.add(Dropout(0.2))
    network.add(Dense(rows_count * cols_count * 2, activation = "relu"))
    network.add(Dropout(0.1))
    network.add(Dense(rows_count * cols_count, activation = "relu"))
    network.add(Dense(1, activation="tanh"))
    network.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return network
