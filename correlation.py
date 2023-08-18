import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd

# Read the CSV file into a DataFrame
data = pd.read_csv('tracks.csv')

# Compute the correlation matrix
correlation_matrix = data.corr()

# Print the correlation matrix
print(correlation_matrix)

sns.heatmap(correlation_matrix, cmap='coolwarm')
plt.show()


absolute_corr_values = correlation_matrix.abs().values.flatten()

sorted_corr_values = sorted(absolute_corr_values, reverse=True)


# Print the ranked variable pairs
print(sorted_corr_values)