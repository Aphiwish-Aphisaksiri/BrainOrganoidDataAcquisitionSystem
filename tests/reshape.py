import numpy as np

# Create a 1D array with 8 elements
array_1d = np.tile(np.arange(1, 5), 2)
print("Original 1D array:")
print(array_1d)

# This is the fix
array_temp = array_1d.reshape(2,4)
print(array_temp)

array_2d = array_temp.T
print("\nTransposed 2D array:")
print(array_2d)

# This is how it was before the fix
# Reshape the 1D array to a 2D array with 4 rows and 2 columns
array_2d = array_1d.reshape(4, 2)
print("\nReshaped to 2D array (4x2):")
print(array_2d)
