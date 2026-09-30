import Toybox.ActivityMonitor;
import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.WatchUi;

module Clr {
    const BONE = 0xE8DCC4;
    const ASH = 0x9A8E84;
    const BLOOD = 0xE0182C;
    const EMBER = 0xFF5A32;
    const GOLD = 0xD6AA3C;
    const STEEL = 0x78A0C8;
    const TRACK = 0x2A1C1C;
    const AOD = 0x5A5250;
    const BLACK = 0x000000;
}

// Layout is authored for a 454x454 screen (fenix 8 Pro / 51mm) and scaled
// to whatever round display the face runs on.
class BerserkView extends WatchUi.WatchFace {

    private var _w as Number = 454;
    private var _h as Number = 454;
    private var _cx as Number = 227;
    private var _cy as Number = 227;
    private var _s as Float = 1.0;

    private var _bg as WatchUi.BitmapResource? = null;
    private var _bleeding as Boolean = false;
    private var _aodBrand as WatchUi.BitmapResource? = null;
    private var _icons as Dictionary<Symbol, WatchUi.BitmapResource> = {} as Dictionary<Symbol, WatchUi.BitmapResource>;

    private var _timeFont = Graphics.FONT_NUMBER_THAI_HOT;

    private var _sleeping as Boolean = false;
    private var _brandMode as Number = 0;
    private var _showSeconds as Boolean = true;

    // Slow-changing data is refreshed once a minute, not every second.
    private var _cacheMinute as Number = -1;
    private var _isNight as Boolean = false;
    private var _sunText as String = "--:--";
    private var _sunIcon as Symbol = :sunrise;
    private var _tempText as String = "--";
    private var _hiLoText as String = "";

    function initialize() {
        WatchFace.initialize();
        loadSettings();
    }

    function loadSettings() as Void {
        _brandMode = readProperty("BrandMode", 0) as Number;
        _showSeconds = readProperty("ShowSeconds", true) as Boolean;
        _cacheMinute = -1;
    }

    private function readProperty(key as String, fallback) {
        try {
            var v = Application.Properties.getValue(key);
            return v != null ? v : fallback;
        } catch (e) {
            return fallback;
        }
    }

    function onLayout(dc as Graphics.Dc) as Void {
        _w = dc.getWidth();
        _h = dc.getHeight();
        _cx = _w / 2;
        _cy = _h / 2;
        _s = _w / 454.0;

        // Fall back to a smaller numeric font if the hottest one can't fit
        // between the date block and the data rows.
        if (dc.getFontHeight(Graphics.FONT_NUMBER_THAI_HOT) > 175 * _s) {
            _timeFont = Graphics.FONT_NUMBER_HOT;
        }

        _aodBrand = WatchUi.loadResource(Rez.Drawables.AodBrand) as WatchUi.BitmapResource;
        _icons = {
            :heart => WatchUi.loadResource(Rez.Drawables.IconHeart),
            :steps => WatchUi.loadResource(Rez.Drawables.IconSteps),
            :flame => WatchUi.loadResource(Rez.Drawables.IconFlame),
            :stairs => WatchUi.loadResource(Rez.Drawables.IconStairs),
            :bolt => WatchUi.loadResource(Rez.Drawables.IconBolt),
            :stress => WatchUi.loadResource(Rez.Drawables.IconStress),
            :sword => WatchUi.loadResource(Rez.Drawables.IconSword),
            :drop => WatchUi.loadResource(Rez.Drawables.IconDrop),
            :mountain => WatchUi.loadResource(Rez.Drawables.IconMountain),
            :hourglass => WatchUi.loadResource(Rez.Drawables.IconHourglass),
            :sunrise => WatchUi.loadResource(Rez.Drawables.IconSunrise),
            :sunset => WatchUi.loadResource(Rez.Drawables.IconSunset),
            :bell => WatchUi.loadResource(Rez.Drawables.IconBell),
            :bt => WatchUi.loadResource(Rez.Drawables.IconBt),
            :alarm => WatchUi.loadResource(Rez.Drawables.IconAlarm),
            :dnd => WatchUi.loadResource(Rez.Drawables.IconDnd),
            :battery => WatchUi.loadResource(Rez.Drawables.IconBattery),
            :distance => WatchUi.loadResource(Rez.Drawables.IconDistance),
            :temp => WatchUi.loadResource(Rez.Drawables.IconTemp)
        } as Dictionary<Symbol, WatchUi.BitmapResource>;
    }

    function onEnterSleep() as Void {
        _sleeping = true;
        WatchUi.requestUpdate();
    }

    function onExitSleep() as Void {
        _sleeping = false;
        WatchUi.requestUpdate();
    }

    function onUpdate(dc as Graphics.Dc) as Void {
        if (dc has :setAntiAlias) {
            dc.setAntiAlias(true);
        }
        var settings = System.getDeviceSettings();
        var clock = System.getClockTime();

        if (_sleeping && (settings has :requiresBurnInProtection) && settings.requiresBurnInProtection) {
            drawAlwaysOn(dc, clock, settings);
            return;
        }

        if (clock.min != _cacheMinute) {
            refreshSlowData(settings);
            _cacheMinute = clock.min;
        }
        updateBackground();

        dc.setColor(Clr.BLACK, Clr.BLACK);
        dc.clear();
        var bg = _bg;
        if (bg != null) {
            dc.drawBitmap(_cx - bg.getWidth() / 2, _cy - bg.getHeight() / 2, bg);
        }

        var act = ActivityMonitor.getInfo();
        var bb = Data.bodyBattery();

        drawGauges(dc, act, bb);
        drawStatusRow(dc, settings);
        drawDate(dc);
        drawTopRow(dc, act, settings);
        drawTime(dc, clock, settings);
        drawDataRows(dc, act, bb, settings);
    }

    // ------------------------------------------------------------------
    // Background: the Brand of Sacrifice bleeds at night (or as configured)
    // ------------------------------------------------------------------

    private function updateBackground() as Void {
        var bleed = (_brandMode == 2) || (_brandMode == 0 && _isNight);
        if (_bg == null || bleed != _bleeding) {
            _bg = null; // release the old bitmap before loading the next
            _bg = WatchUi.loadResource(bleed ? Rez.Drawables.BgBleed : Rez.Drawables.BgCalm) as WatchUi.BitmapResource;
            _bleeding = bleed;
        }
    }

    private function refreshSlowData(settings as System.DeviceSettings) as Void {
        var cc = Data.weather();
        var statute = settings.temperatureUnits == System.UNIT_STATUTE;

        if (cc != null) {
            _tempText = Fmt.temperature(cc.temperature, statute);
            if (cc.highTemperature != null && cc.lowTemperature != null) {
                _hiLoText = Fmt.temperature(cc.highTemperature, statute) + "/" + Fmt.temperature(cc.lowTemperature, statute);
            } else {
                _hiLoText = "";
            }
        } else {
            _tempText = "--";
            _hiLoText = "";
        }

        var sun = Data.sunState(Data.location(cc));
        if (sun != null) {
            _isNight = sun[0] as Boolean;
            _sunText = Fmt.moment(sun[1] as Time.Moment?, settings.is24Hour);
            _sunIcon = (sun[2] as Boolean) ? :sunrise : :sunset;
        } else {
            var hour = System.getClockTime().hour;
            _isNight = hour >= 19 || hour < 7;
            _sunText = "--:--";
            _sunIcon = _isNight ? :sunrise : :sunset;
        }
    }

    // ------------------------------------------------------------------
    // Outer gauges: body battery (left), step goal (right)
    // ------------------------------------------------------------------

    private function drawGauges(dc as Graphics.Dc, act as ActivityMonitor.Info, bb as Number?) as Void {
        var r = (204 * _s).toNumber();
        var pen = (8 * _s).toNumber();
        if (pen < 3) {
            pen = 3;
        }
        dc.setPenWidth(pen);

        // Left: fills upward from 215° to 145° (clockwise on screen).
        var bbFrac = bb != null ? bb / 100.0 : 0.0;
        drawArcGauge(dc, r, 215, 70, Graphics.ARC_CLOCKWISE, bbFrac, Clr.GOLD);

        // Right: fills upward from 325° to 35° (counter-clockwise on screen).
        var stepFrac = 0.0;
        if (act.steps != null && act.stepGoal != null && act.stepGoal > 0) {
            stepFrac = act.steps.toFloat() / act.stepGoal;
        }
        drawArcGauge(dc, r, 325, 70, Graphics.ARC_COUNTER_CLOCKWISE, stepFrac,
            stepFrac >= 1.0 ? Clr.GOLD : Clr.BLOOD);

        dc.setPenWidth(1);

        drawIconAtAngle(dc, :bolt, r, 223);
        drawIconAtAngle(dc, :steps, r, 317);
    }

    private function drawArcGauge(dc as Graphics.Dc, r as Number, start as Number, span as Number,
            dir, frac as Float, color as Number) as Void {
        var cw = dir == Graphics.ARC_CLOCKWISE;
        dc.setColor(Clr.TRACK, Graphics.COLOR_TRANSPARENT);
        dc.drawArc(_cx, _cy, r, dir, start, normAngle(cw ? start - span : start + span));
        if (frac <= 0.01) {
            return;
        }
        if (frac > 1.0) {
            frac = 1.0;
        }
        var sweep = span * frac;
        dc.setColor(color, Graphics.COLOR_TRANSPARENT);
        dc.drawArc(_cx, _cy, r, dir, start, normAngle(cw ? start - sweep : start + sweep));
    }

    private function normAngle(a) {
        while (a >= 360) {
            a -= 360;
        }
        while (a < 0) {
            a += 360;
        }
        return a;
    }

    private function drawIconAtAngle(dc as Graphics.Dc, key as Symbol, r as Number, deg as Number) as Void {
        var rad = Math.toRadians(deg);
        var x = _cx + r * Math.cos(rad);
        var y = _cy - r * Math.sin(rad);
        var bmp = _icons[key];
        if (bmp != null) {
            dc.drawBitmap(x.toNumber() - bmp.getWidth() / 2, y.toNumber() - bmp.getHeight() / 2, bmp);
        }
    }

    // ------------------------------------------------------------------
    // Top: status icons, date, altitude / SpO2 / recovery
    // ------------------------------------------------------------------

    private function drawStatusRow(dc as Graphics.Dc, settings as System.DeviceSettings) as Void {
        var y = sy(46);
        var font = Graphics.FONT_XTINY;
        var gap = sx(10);
        var items = [] as Array<Array>;

        if (settings.phoneConnected) {
            items.add([:bt, "", Clr.STEEL]);
        }
        if (settings.notificationCount > 0) {
            items.add([:bell, settings.notificationCount.toString(), Clr.BONE]);
        }
        if (settings.alarmCount > 0) {
            items.add([:alarm, "", Clr.BONE]);
        }
        if ((settings has :doNotDisturb) && settings.doNotDisturb) {
            items.add([:dnd, "", Clr.ASH]);
        }
        var stats = System.getSystemStats();
        var batt = stats.battery.toNumber();
        var battText = batt.toString() + "%";
        if ((stats has :batteryInDays) && stats.batteryInDays != null && !stats.charging) {
            battText += " " + stats.batteryInDays.toNumber().toString() + "d";
        }
        items.add([:battery, battText, batt <= 20 ? Clr.BLOOD : Clr.BONE]);

        // measure, then lay out centered
        var total = 0;
        for (var i = 0; i < items.size(); i++) {
            total += cellWidth(dc, items[i][0] as Symbol, items[i][1] as String, font);
        }
        total += gap * (items.size() - 1);
        var x = _cx - total / 2;
        for (var i = 0; i < items.size(); i++) {
            var w = cellWidth(dc, items[i][0] as Symbol, items[i][1] as String, font);
            drawCell(dc, x + w / 2, y, items[i][0] as Symbol, items[i][1] as String, items[i][2] as Number, font);
            x += w + gap;
        }
    }

    private function drawDate(dc as Graphics.Dc) as Void {
        var info = Gregorian.info(Time.now(), Time.FORMAT_MEDIUM);
        var text = (info.day_of_week as String).toUpper() + " " + info.day.format("%02d") + " "
            + (info.month as String).toUpper();
        shadowText(dc, _cx, sy(80), Graphics.FONT_SMALL, text, Clr.BONE, Graphics.TEXT_JUSTIFY_CENTER, 2);
    }

    private function drawTopRow(dc as Graphics.Dc, act as ActivityMonitor.Info, settings as System.DeviceSettings) as Void {
        var y = sy(114);
        var font = Graphics.FONT_XTINY;

        var alt = Data.altitude();
        var altText = "--";
        if (alt != null) {
            altText = settings.elevationUnits == System.UNIT_STATUTE
                ? Fmt.thousands((alt * 3.28084).toNumber()) + "ft"
                : Fmt.thousands(alt.toNumber()) + "m";
        }
        drawCell(dc, _cx - sx(104), y, :mountain, altText, Clr.ASH, font);

        var ox = Data.spo2();
        drawCell(dc, _cx, y, :drop, ox != null ? ox.toString() + "%" : "--", Clr.STEEL, font);

        var rec = "--";
        if ((act has :timeToRecovery) && act.timeToRecovery != null) {
            rec = act.timeToRecovery.toString() + "h";
        }
        drawCell(dc, _cx + sx(104), y, :hourglass, rec, Clr.ASH, font);
    }

    // ------------------------------------------------------------------
    // Time
    // ------------------------------------------------------------------

    private function drawTime(dc as Graphics.Dc, clock as System.ClockTime, settings as System.DeviceSettings) as Void {
        var y = sy(194);
        var text = Fmt.hourMinute(clock.hour, clock.min, settings.is24Hour);
        shadowText(dc, _cx, y, _timeFont, text, Clr.BONE,
            Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER, sx(3));

        if (_showSeconds && !_sleeping) {
            var tw = dc.getTextWidthInPixels(text, _timeFont);
            var secY = y + dc.getFontHeight(_timeFont) / 4 - dc.getFontHeight(Graphics.FONT_TINY) / 2;
            shadowText(dc, _cx + tw / 2 + sx(4), secY, Graphics.FONT_TINY, clock.sec.format("%02d"),
                Clr.BLOOD, Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER, 2);
        }
    }

    // ------------------------------------------------------------------
    // Lower data block
    // ------------------------------------------------------------------

    private function drawDataRows(dc as Graphics.Dc, act as ActivityMonitor.Info, bb as Number?,
            settings as System.DeviceSettings) as Void {
        var big = Graphics.FONT_TINY;
        var small = Graphics.FONT_XTINY;
        var col = sx(116);

        // Row 1: heart rate | body battery | stress
        var y = sy(280);
        drawCell(dc, _cx - col, y, :heart, Fmt.orDash(Data.heartRate()), Clr.BONE, big);
        drawCell(dc, _cx, y, :bolt, Fmt.orDash(bb), Clr.GOLD, big);
        var st = Data.stress();
        drawCell(dc, _cx + col, y, :stress, Fmt.orDash(st), st != null && st > 75 ? Clr.EMBER : Clr.BONE, big);

        // Row 2: steps | calories | floors
        y = sy(318);
        drawCell(dc, _cx - col, y, :steps, act.steps != null ? Fmt.thousands(act.steps) : "--", Clr.BONE, big);
        drawCell(dc, _cx, y, :flame, Fmt.orDash(act.calories), Clr.BONE, big);
        var floors = (act has :floorsClimbed) ? act.floorsClimbed : null;
        drawCell(dc, _cx + col, y, :stairs, Fmt.orDash(floors), Clr.BONE, big);

        // Row 3: weather | next sunrise/sunset
        y = sy(356);
        var weather = _hiLoText.length() > 0 ? _tempText + " " + _hiLoText : _tempText;
        drawCell(dc, _cx - sx(72), y, :temp, weather, Clr.BONE, small);
        drawCell(dc, _cx + sx(78), y, _sunIcon, _sunText, _sunIcon == :sunrise ? Clr.GOLD : Clr.EMBER, small);

        // Row 4: weekly intensity minutes | distance
        y = sy(392);
        var mins = "--";
        if ((act has :activeMinutesWeek) && act.activeMinutesWeek != null) {
            mins = act.activeMinutesWeek.total.toString();
        }
        drawCell(dc, _cx - sx(64), y, :sword, mins, Clr.BONE, small);

        var dist = "--";
        if (act.distance != null) {
            dist = settings.distanceUnits == System.UNIT_STATUTE
                ? (act.distance / 160934.4).format("%.1f") + "mi"
                : (act.distance / 100000.0).format("%.1f") + "km";
        }
        drawCell(dc, _cx + sx(64), y, :distance, dist, Clr.BONE, small);
    }

    // ------------------------------------------------------------------
    // Always-on (AMOLED low power): <10% lit pixels, shifted each minute
    // ------------------------------------------------------------------

    private function drawAlwaysOn(dc as Graphics.Dc, clock as System.ClockTime, settings as System.DeviceSettings) as Void {
        dc.setColor(Clr.BLACK, Clr.BLACK);
        dc.clear();

        var shifts = [[0, 0], [-6, -4], [6, 4], [-4, 6], [4, -6]];
        var shift = shifts[clock.min % shifts.size()];
        var ox = sx(shift[0] as Number);
        var oy = sy(shift[1] as Number);

        var brand = _aodBrand;
        if (brand != null) {
            dc.drawBitmap(_cx - brand.getWidth() / 2 + ox, sy(52) + oy, brand);
        }
        dc.setColor(Clr.AOD, Graphics.COLOR_TRANSPARENT);
        dc.drawText(_cx + ox, _cy + sy(20) + oy, Graphics.FONT_NUMBER_MEDIUM,
            Fmt.hourMinute(clock.hour, clock.min, settings.is24Hour),
            Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);

        var info = Gregorian.info(Time.now(), Time.FORMAT_MEDIUM);
        dc.drawText(_cx + ox, _cy + sy(84) + oy, Graphics.FONT_XTINY,
            (info.day_of_week as String).toUpper() + " " + info.day.toString(),
            Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    private function sx(v as Number) as Number {
        return (v * _s).toNumber();
    }

    private function sy(v as Number) as Number {
        return (v * _s).toNumber();
    }

    private function cellWidth(dc as Graphics.Dc, key as Symbol, text as String, font) as Number {
        var bmp = _icons[key];
        var iw = bmp != null ? bmp.getWidth() : 0;
        if (text.length() == 0) {
            return iw;
        }
        return iw + sx(5) + dc.getTextWidthInPixels(text, font);
    }

    // Icon + value, centered on (x, y).
    private function drawCell(dc as Graphics.Dc, x as Number, y as Number, key as Symbol, text as String,
            color as Number, font) as Void {
        var bmp = _icons[key];
        var w = cellWidth(dc, key, text, font);
        var left = x - w / 2;
        if (bmp != null) {
            dc.drawBitmap(left, y - bmp.getHeight() / 2, bmp);
            left += bmp.getWidth() + sx(5);
        }
        if (text.length() > 0) {
            shadowText(dc, left, y, font, text, color, Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER, 1);
        }
    }

    // Black halo keeps text legible over the red brand.
    private function shadowText(dc as Graphics.Dc, x as Number, y as Number, font, text as String,
            color as Number, just as Number, d as Number) as Void {
        if (d < 1) {
            d = 1;
        }
        dc.setColor(Clr.BLACK, Graphics.COLOR_TRANSPARENT);
        dc.drawText(x - d, y - d, font, text, just);
        dc.drawText(x + d, y - d, font, text, just);
        dc.drawText(x - d, y + d, font, text, just);
        dc.drawText(x + d, y + d, font, text, just);
        dc.setColor(color, Graphics.COLOR_TRANSPARENT);
        dc.drawText(x, y, font, text, just);
    }
}
