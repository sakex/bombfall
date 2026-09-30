import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Lang;
import Toybox.Math;
import Toybox.SensorHistory;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Weather;

// Every sensor read is guarded: a missing API or an empty history just
// yields null, and the view renders "--" for it.
module Data {

    function heartRate() as Number? {
        var act = Activity.getActivityInfo();
        if (act != null && act.currentHeartRate != null) {
            return act.currentHeartRate;
        }
        if (ActivityMonitor has :getHeartRateHistory) {
            var it = ActivityMonitor.getHeartRateHistory(1, true);
            var sample = it.next();
            if (sample != null && sample.heartRate != null
                    && sample.heartRate != ActivityMonitor.INVALID_HR_SAMPLE) {
                return sample.heartRate;
            }
        }
        return null;
    }

    function latest(iter) as Numeric? {
        if (iter == null) {
            return null;
        }
        var sample = iter.next();
        var n = 0;
        while (sample != null && n < 10) {
            if (sample.data != null) {
                return sample.data;
            }
            sample = iter.next();
            n++;
        }
        return null;
    }

    function historyOptions() as Dictionary {
        return {:period => 10, :order => SensorHistory.ORDER_NEWEST_FIRST};
    }

    function bodyBattery() as Number? {
        if ((Toybox has :SensorHistory) && (SensorHistory has :getBodyBatteryHistory)) {
            var v = latest(SensorHistory.getBodyBatteryHistory(historyOptions()));
            return v != null ? v.toNumber() : null;
        }
        return null;
    }

    function stress() as Number? {
        if ((Toybox has :SensorHistory) && (SensorHistory has :getStressHistory)) {
            var v = latest(SensorHistory.getStressHistory(historyOptions()));
            return v != null ? v.toNumber() : null;
        }
        return null;
    }

    function spo2() as Number? {
        if ((Toybox has :SensorHistory) && (SensorHistory has :getOxygenSaturationHistory)) {
            var v = latest(SensorHistory.getOxygenSaturationHistory(historyOptions()));
            return v != null ? v.toNumber() : null;
        }
        return null;
    }

    // Meters, from the barometric altimeter (falls back to sensor history).
    function altitude() as Float? {
        var act = Activity.getActivityInfo();
        if (act != null && act.altitude != null) {
            return act.altitude.toFloat();
        }
        if ((Toybox has :SensorHistory) && (SensorHistory has :getElevationHistory)) {
            var v = latest(SensorHistory.getElevationHistory(historyOptions()));
            return v != null ? v.toFloat() : null;
        }
        return null;
    }

    function weather() as Weather.CurrentConditions? {
        if (Toybox has :Weather) {
            return Weather.getCurrentConditions();
        }
        return null;
    }

    function location(cc as Weather.CurrentConditions?) {
        if (cc != null && cc.observationLocationPosition != null) {
            return cc.observationLocationPosition;
        }
        var act = Activity.getActivityInfo();
        if (act != null && act.currentLocation != null) {
            return act.currentLocation;
        }
        return null;
    }

    // Returns [isNight, nextEventMoment, nextIsSunrise] or null when the
    // sun times can't be computed (no location yet, or no API).
    function sunState(loc) as Array? {
        if (loc == null || !(Toybox has :Weather) || !(Weather has :getSunrise)) {
            return null;
        }
        var now = Time.now();
        var rise = Weather.getSunrise(loc, now);
        var set = Weather.getSunset(loc, now);
        if (rise == null || set == null) {
            return null;
        }
        if (now.compare(rise) < 0) {
            return [true, rise, true];
        }
        if (now.compare(set) < 0) {
            return [false, set, false];
        }
        var tomorrow = Weather.getSunrise(loc, now.add(new Time.Duration(Gregorian.SECONDS_PER_DAY)));
        return [true, tomorrow, true];
    }
}

module Fmt {

    function thousands(n as Number) as String {
        var s = n.abs().toString();
        var len = s.length();
        var out = "";
        for (var i = 0; i < len; i++) {
            if (i > 0 && (len - i) % 3 == 0) {
                out += ",";
            }
            out += s.substring(i, i + 1);
        }
        return n < 0 ? "-" + out : out;
    }

    function orDash(v) as String {
        return v == null ? "--" : v.toString();
    }

    function hourMinute(hour as Number, min as Number, is24 as Boolean) as String {
        if (is24) {
            return hour.format("%02d") + ":" + min.format("%02d");
        }
        var h = hour % 12;
        if (h == 0) {
            h = 12;
        }
        return h.toString() + ":" + min.format("%02d");
    }

    function moment(m as Time.Moment?, is24 as Boolean) as String {
        if (m == null) {
            return "--:--";
        }
        var info = Gregorian.info(m, Time.FORMAT_SHORT);
        return hourMinute(info.hour, info.min, is24);
    }

    function temperature(celsius, statute as Boolean) as String {
        if (celsius == null) {
            return "--";
        }
        var t = celsius.toFloat();
        if (statute) {
            t = t * 9.0 / 5.0 + 32.0;
        }
        return Math.round(t).toNumber().toString() + "°";
    }
}
