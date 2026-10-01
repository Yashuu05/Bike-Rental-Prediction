class Models:
    """class to hold dictionary of model names and their corresponding objects"""
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from lightgbm import LGBMRegressor
    models = {
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(),
        "LGBMRegressor": LGBMRegressor(),
    }