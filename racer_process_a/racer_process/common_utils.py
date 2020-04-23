def find_points_on_line(m, c):
    """
    Function to find points on given line
    :param m: slope of line
    :param c: constant intercept of line
    :return: list of two points on the given line
    """
    return [
        [1, (m * 1) + c],
        [2, (m * 2) + c]
    ]


def line_intersection(m1, c1, m2, c2):
    """
    Function to intersection point of two lines
    :param m1: slope of line 1
    :param c1: constant intercept of line 1
    :param m2: slope of line 2
    :param c2: constant intercept of line 2
    :return: intersection point of the two lines in the form of tuple
    """
    line1 = find_points_on_line(m1, c1)
    line2 = find_points_on_line(m2, c2)

    x_diff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    y_diff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(x_diff, y_diff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, x_diff) / div
    y = det(d, y_diff) / div
    return x, y


def add_one_unit_to_point(point, m, c):
    """
    Function to add one to x coordinate of a point
    and find the y coordinate accordingly
    :param point: current point
    :param m: slope of line
    :param c: constant intercept of line
    :return: new point coordinates in the form of tuple
    """
    new_x = point[0] + 1
    new_y = (m * new_x) + c
    return new_x, new_y
