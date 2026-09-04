class_name Grid
## The hotel is a vertical shaft of 1 m cells. Column 0 and column
## [constant WALL_RIGHT] are the walls; rows count downwards from the top of
## the first level and map to negative world Y.

const CELL := 1.0
const WIDTH := 16            ## interior columns 1..15, wall at 0 and 16
const WALL_RIGHT := 16
const DEPTH := 2.0           ## thickness of floor/wall cells along Z
const INTERIOR_MIN_X := 1.0
const INTERIOR_MAX_X := 16.0
const CENTER_X := 8.5


static func cell_center(cx: int, row: int) -> Vector3:
	return Vector3(cx + 0.5, -(row + 0.5), 0.0)


## World position of the top-left corner of a cell (the old 2D spawn origin).
static func cell_corner(cx: float, row: float) -> Vector3:
	return Vector3(cx, -row, 0.0)


static func row_of(y: float) -> int:
	return int(floor(-y))


static func col_of(x: float) -> int:
	return int(floor(x))


## Converts an old 2D pixel offset (64 px cells, Y down) into metres, Y up.
static func px(x: float, y: float) -> Vector3:
	return Vector3(x / 64.0, -y / 64.0, 0.0)
