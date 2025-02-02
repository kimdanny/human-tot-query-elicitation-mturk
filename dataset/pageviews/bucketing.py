"""
Post-processing after the final candidates files are created.
Create 19 buckets for even distribution drawing
"""
import pandas as pd
from collections import Counter


CLUSTER_USER = "YOUR_USER_NAME"
BASE_PATH = f"/YOUR/BASE/PATH/dataset"
del CLUSTER_USER
CATEGORY_NAME = "landmark"


pageviews_df = pd.read_csv(f"{BASE_PATH}/{CATEGORY_NAME}_candidates.csv")

# Quantile-based discretization (equal-sized buckets)
bucket_names = [f"{x:02}" for x in range(1, 20)][::-1]
pageviews_df["Bucket"] = pd.qcut(pageviews_df["PageViews"], q=19, labels=bucket_names)

# to local
pageviews_df.to_csv(
    f"{BASE_PATH}/{CATEGORY_NAME}_candidates.csv",
    index=False,
)

total_counter = Counter(pageviews_df["Bucket"].tolist())
print(sorted(total_counter.items()))

# movie (min=79)
# [('01', 80), ('02', 81), ('03', 79), ('04', 80), ('05', 80), ('06', 81), ('07', 79), ('08', 80), ('09', 80), ('10', 80),
# ('11', 80), ('12', 80), ('13', 80), ('14', 80), ('15', 80), ('16', 80), ('17', 80), ('18', 80), ('19', 81)]

# celebrity (min=98)
# [('01', 98), ('02', 98), ('03', 98), ('04', 98), ('05', 98), ('06', 98), ('07', 98), ('08', 98), ('09', 98), ('10', 98),
# ('11', 98), ('12', 98), ('13', 98), ('14', 98), ('15', 98), ('16', 98), ('17', 98), ('18', 98), ('19', 98)]

# landmark (min=16)
# [('01', 17), ('02', 17), ('03', 16), ('04', 17), ('05', 16), ('06', 17), ('07', 17), ('08', 16), ('09', 17), ('10', 16),
# ('11', 17), ('12', 16), ('13', 17), ('14', 17), ('15', 16), ('16', 17), ('17', 16), ('18', 17), ('19', 17)]
