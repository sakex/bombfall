class_name Layers
## Physics layer bits (see project.godot [layer_names]).

const PLAYER := 1 << 0
const BOMB := 1 << 1
const EXPLOSION := 1 << 2
const COIN := 1 << 3
const WORLD := 1 << 4
const SPAWNABLE := 1 << 5
const EFFECT := 1 << 6
const PICKUP := 1 << 7
const CONNECTOR := 1 << 8
const POLE := 1 << 9
const BULLET := 1 << 10
const BOSS := 1 << 11

## Everything a solid prop bumps into.
const SOLID := PLAYER | BOMB | COIN | WORLD | SPAWNABLE | CONNECTOR | POLE | BOSS
## Everything an explosion can hurt.
const BLASTABLE := PLAYER | BOMB | COIN | WORLD | SPAWNABLE | CONNECTOR | POLE | BOSS | PICKUP
