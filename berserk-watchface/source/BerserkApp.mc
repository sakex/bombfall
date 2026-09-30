import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;

class BerserkApp extends Application.AppBase {

    private var _view as BerserkView?;

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
    }

    function onStop(state as Dictionary?) as Void {
    }

    function getInitialView() {
        _view = new BerserkView();
        return [_view];
    }

    function onSettingsChanged() as Void {
        var view = _view;
        if (view != null) {
            view.loadSettings();
        }
        WatchUi.requestUpdate();
    }
}
