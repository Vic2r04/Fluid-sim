from math import floor

# Get an interpolated data value from the grid, handling boundaries and weight normalization
def getInterpolatedValue(grid, x, y, component):
    # Find the indices of the lower-left corner of the grid cell
    i = floor(x)
    j = floor(y)

    # Calculate how far (x, y) is from the lower-left grid point
    x_weight = x - i
    y_weight = y - j

    # Initialize the result value and total weight
    rv = 0
    total_weight = 0

    # Define the 4 surrounding grid points and their corresponding weights
    corners = [
        (i, j, (1 - x_weight) * (1 - y_weight)),  # Lower-left corner
        (i+1, j, x_weight * (1 - y_weight)),      # Lower-right corner
        (i, j+1, (1 - x_weight) * y_weight),      # Upper-left corner
        (i+1, j+1, x_weight * y_weight)           # Upper-right corner
    ]

    # Loop through the corners, check bounds, and accumulate the valid contributions
    for i_c, j_c, weight in corners:
        if 0 <= i_c < len(grid[0]) and 0 <= j_c < len(grid):
            rv += weight * grid[j_c][i_c].vel[component]
            total_weight += weight

    # Normalize the result by dividing by the total weight
    if total_weight > 0:
        rv /= total_weight

    return rv


     
