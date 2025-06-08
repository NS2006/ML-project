def getRecommendations(feature_pairs, prediction):
    rec_db = pd.read_csv('sleep_recommendations.csv') 
    
    recommendations = []
    
    # Get base recommendations (where feature and condition are empty)
    base_recs = rec_db[
        (rec_db['prediction_level'] == prediction) &
        (rec_db['feature'].isna()) &
        (rec_db['condition'].isna())
    ]
    recommendations.extend(base_recs['recommendation'].tolist())
    
    # Get feature-specific recommendations
    for col, val in feature_pairs:
        # Get rows for this feature that have conditions
        feature_rows = rec_db[
            (rec_db['feature'] == col) & 
            (rec_db['condition'].notna())
        ]
        
        # Evaluate each condition
        for _, row in feature_rows.iterrows():
            try:
                if eval(row['condition'], {'val': val}):
                    recommendations.append(row['recommendation'])
            except:
                continue
    
    # max 10
    return list(set(recommendations))[:10]