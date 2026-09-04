class_name SpecialLevel
extends RefCounted
## A hand-designed storey inserted every ten levels.


func available() -> bool:
	return true


## Builds the storey starting at [param roof] and returns its Level.
func draw(_world: Node, _roof: int, _coin_budget: int) -> Level:
	return null


## How many rows the roof advances after this storey.
func advance_rows() -> int:
	return 16
