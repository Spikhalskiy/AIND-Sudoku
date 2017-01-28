import solution
import unittest


def get_from_file(filename):
    """
    Returns a list with each line in the file.
    """
    with open(filename, 'r') as f:
        return f.read().splitlines()


class ExtraTests(unittest.TestCase):
    def test_non_diagonal_extras(self):
        hard_probs = get_from_file('non_diagonal_extra_problems.txt')
        hard_sols = [solution.grid_values(sol) for sol in get_from_file('non_diagonal_extra_solutions.txt')]

        assert len(hard_probs) == len(hard_sols)

        # False here means we are solving sudokus without diagonal constraints
        my_sols = [solution.solve(prob, False) for prob in hard_probs]

        for index in range(0, len(hard_probs)):
            self.assertEqual(hard_sols[index], my_sols[index],
                             msg='A sudoku number {0} with grid {1} with a solution {2} solved incorrectly with a '
                                 'result {3} '
                             .format(index, hard_probs[index], hard_sols[index], my_sols[index]))


if __name__ == '__main__':
    unittest.main()
