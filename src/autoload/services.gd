extends Node
## Online services the original game wired to AdMob and Firebase.
##
## Neither SDK can be bundled by the headless build (both need Google's
## Maven repository at build time), so the game talks to these two small
## interfaces instead. The default implementations are offline no-ops that
## keep every feature working locally; drop in real ones here when the
## native plugins are available again.

var ads: Ads = Ads.new()
var backend: Backend = Backend.new()


class Ads extends RefCounted:
	## Emitted after a rewarded ad finished (or immediately when ads are off).
	signal rewarded_finished(success: bool)

	func available() -> bool:
		return false

	func show_interstitial() -> void:
		pass

	func show_rewarded() -> void:
		rewarded_finished.emit(false)


class Backend extends RefCounted:
	## Emitted with an Array of {username, score} entries.
	signal leaderboard_loaded(entries: Array)
	## Emitted with {"username": String} or {"error": String}.
	signal username_changed(result: Dictionary)

	func available() -> bool:
		return false

	func sync_profile(_data: Dictionary) -> void:
		pass

	func fetch_leaderboard() -> void:
		leaderboard_loaded.emit([])

	func change_username(name: String) -> void:
		username_changed.emit({"error": "Online accounts are not available in this build."} if name.is_empty() else {"username": name})
