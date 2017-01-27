assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    """Cross product of elements in a and elements in b."""
    return [s + t for s in a for t in b]


boxes = cross(rows, cols)
unitlist = []
units = dict()
peers = dict()


def init(diagonal=True):
    """
    Init internal variables to solve sudoku with specified parameters like if it should be diagonal or not
    :param diagonal: True if solving sudoku should have diagonal constraints
    :return: None
    """

    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

    global unitlist
    if diagonal:
        # To solve diagonal sudoku we add 2 units for two diagonals into units collection
        diag_units = [[a + b for (a, b) in zip(list(rows), list(cols))]] + [
            [a + b for (a, b) in zip(list(rows), list(cols[::-1]))]]
        unitlist = row_units + column_units + square_units + diag_units
    else:
        unitlist = row_units + column_units + square_units

    global units
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

    global peers
    peers = dict((s, set(sum(units[s], [])) - {s}) for s in boxes)


def eliminate_from_boxes_collection(values, boxes_collection, digit):
    """Removes digit from all boxes in boxes_collection"""
    for peer in boxes_collection:
        assign_value(values, peer, values[peer].replace(digit, ''))


def find_twins(values):
    """Find all twins is sudoku, don't take into account unit/peers structure

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        dict with a key is twins_value and value is set of boxes that have this twins_value"""
    # dict with boxes as a key and set of boxes as a value
    twins = {}
    for v, box in [(values[box], box) for box in values.keys() if len(values[box]) == 2]:
        if v in twins:
            twins[v].add(box)
        else:
            twins[v] = {box}
    # Remove boxes which has 2-length value, but no pairs
    return {v: boxs for (v, boxs) in twins.items() if len(boxs) > 1}


def eliminate_twins(values, twins, unit):
    """Eliminate twins from the unit

    :param values: whole sudoku state
    :param twins: dict with all twins, key is twins values, value is twins boxes set
    :param unit: unit to search and eliminate twin values from
    :return: new values state
    """
    for i in range(0, len(unit)):
        box1 = unit[i]
        box1_value = values[box1]
        if box1_value in twins:
            for j in range(i + 1, len(unit)):
                box2 = unit[j]
                if box2 in twins[box1_value]:
                    # even if a value of this box is been modified already by other loop iteration - it's still fine
                    # we could continue to safely consider them as twins
                    for digit in box1_value:
                        other_unit_boxes = [box for box in unit if box not in {box1, box2}]
                        eliminate_from_boxes_collection(values, other_unit_boxes, digit)
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    twins = find_twins(values)

    # Eliminate the naked twins as possibilities for their peers
    for unit in unitlist:
        values = eliminate_twins(values, twins, unit)

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    print()


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all
    its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        eliminate_from_boxes_collection(values, peers[box], digit)
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value
    to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate(), only_choice() and naked_twins() if required.
    If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    :param values: A sudoku in a dictionary form.
    :return: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        assert isinstance(values, dict)
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        assert isinstance(values, dict)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        # use an expensive naked twins only if stalled with basic methods
        if stalled:
            values = naked_twins(values)
            solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
            stalled = solved_values_before == solved_values_after

        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, try all possible values."""
    assert isinstance(values, dict)

    values = reduce_puzzle(values)
    if values is False:
        return False  # Failed earlier
    assert isinstance(values, dict)

    if all(len(values[s]) == 1 for s in boxes):
        return values  # Solved!
    # Chose one of the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid, diagonal=True):
    """
    Find the solution to a Sudoku grid.
    :param grid: string serialized representation of a sudoku grid
                Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    :param diagonal: if you want to solve diagonal soduku or general one
    :return: The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    init(diagonal)
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
