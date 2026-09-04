class_name BinaryGrid
## Occupancy bitmap used while laying out a level: one int per row, one bit
## per column. Mirrors the Rust BinaryGrid of the original generator.

var cols: int
var rows: int
var _data: PackedInt64Array


func _init(p_cols: int, p_rows: int) -> void:
	cols = p_cols
	rows = p_rows
	_data.resize(rows)
	reset()


func reset() -> void:
	_data.fill(0)


func is_cell_free(x: int, y: int) -> bool:
	if x < 0 or y < 0 or x >= cols or y >= rows:
		return false
	return (_data[y] & (1 << x)) == 0


func set_square(x: int, y: int, width: int, height: int) -> void:
	assert(x + width <= cols and y + height <= rows, "BinaryGrid.set_square out of bounds")
	for row in range(y, y + height):
		for col in range(x, x + width):
			_data[row] |= 1 << col


func can_make_full_rect(x: int, y: int, width: int, height: int) -> bool:
	if x < 0 or y < 0 or x + width > cols or y + height > rows:
		return false
	for row in range(y, y + height):
		for col in range(x, x + width):
			if _data[row] & (1 << col):
				return false
	return true


## Top-left cells (as Vector2i) where a width x height rectangle fits,
## scanning rows y0..y1-1 and columns x0..x1-1.
func free_squares(x0: int, x1: int, y0: int, y1: int, width: int, height: int) -> Array[Vector2i]:
	var free: Array[Vector2i] = []
	for row in range(y0, y1):
		for col in range(x0, x1):
			if can_make_full_rect(col, row, width, height):
				free.append(Vector2i(col, row))
	return free
