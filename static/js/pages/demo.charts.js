var colors = ["#727cf5", "#0acf97", "#fa5c7c", "#ffbc00"];
var data_colors = $("#rain-level-chart").data("colors");
data_colors && (colors = data_colors.split(","));

var rain_level_chart = {
    chart: { type: "bar", height: 60, sparkline: { enabled: !0 } },
    plotOptions: { bar: { columnWidth: "60%" } },
    colors: colors,
    series: [{ data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 54, 30, 60] }],
    labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    xaxis: { crosshairs: { width: 1 } },
    tooltip: {
        fixed: { enabled: !1 },
        x: { show: !1 },
        y: {
            title: {
                formatter: function (o) {
                    return "";
                },
            },
        },
        marker: { show: !1 },
    },
};

new ApexCharts(document.querySelector("#rain-level-chart"), rain_level_chart).render();

(data_colors = $("#temperature-chart").data("colors")) && (colors = data_colors.split(","));

var temperature_chart = {
    chart: { type: "line", height: 60, sparkline: { enabled: !0 } },
    series: [{ data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54] }],
    stroke: { width: 2, curve: "smooth" },
    markers: { size: 0 },
    colors: colors,
    tooltip: {
        fixed: { enabled: !1 },
        x: { show: !1 },
        y: {
            title: {
                formatter: function (o) {
                    return "";
                },
            },
        },
        marker: { show: !1 },
    },
};

new ApexCharts(document.querySelector("#temperature-chart"), temperature_chart).render();

(data_colors = $("#dew-point-chart").data("colors")) && (colors = data_colors.split(","));

var dew_point_chart = {
    chart: { type: "bar", height: 60, sparkline: { enabled: !0 } },
    plotOptions: { bar: { columnWidth: "60%" } },
    colors: colors,
    series: [{ data: [12, 14, 2, 47, 42, 15, 47, 75, 65, 19, 14] }],
    labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    xaxis: { crosshairs: { width: 1 } },
    tooltip: {
        fixed: { enabled: !1 },
        x: { show: !1 },
        y: {
            title: {
                formatter: function (o) {
                    return "";
                },
            },
        },
        marker: { show: !1 },
    },
};

new ApexCharts(document.querySelector("#dew-point-chart"), dew_point_chart).render();

(data_colors = $("#air-quality-chart").data("colors")) && (colors = data_colors.split(","));

var air_quality_chart = {
    chart: { type: "line", height: 60, sparkline: { enabled: !0 } },
    series: [{ data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54] }],
    stroke: { width: 2, curve: "smooth" },
    markers: { size: 0 },
    colors: colors,
    tooltip: {
        fixed: { enabled: !1 },
        x: { show: !1 },
        y: {
            title: {
                formatter: function (o) {
                    return "";
                },
            },
        },
        marker: { show: !1 },
    },
};

new ApexCharts(document.querySelector("#air-quality-chart"), air_quality_chart).render();

!(function (o) {
    "use strict";

    function e() {
        (this.$body = o("body")), (this.charts = []);
    }

    (e.prototype.initCharts = function () {
        window.Apex = { chart: { parentHeightOffset: 0, toolbar: { show: !1 } }, grid: { padding: { left: 0, right: 0 } }, colors: ["#727cf5", "#0acf97", "#fa5c7c", "#ffbc00"] };
        var e = ["#727cf5", "#0acf97", "#fa5c7c", "#ffbc00"],
            t = o("#humidity-chart").data("colors");
        t && (e = t.split(","));
        var humidity_chart = {
            chart: { height: 320, type: "line", dropShadow: { enabled: !0, opacity: 0.2, blur: 7, left: -7, top: 7 } },
            dataLabels: { enabled: !1 },
            stroke: { curve: "smooth", width: 4 },
            series: [
                { name: "Umidade do ar", data: [10, 20, 15, 25, 20, 30] },
                { name: "Umidade do solo", data: [0, 15, 10, 30, 15, 35] },
            ],
            colors: e,
            zoom: { enabled: !1 },
            legend: { show: !1 },
            xaxis: { type: "string", categories: ["60s", "50s", "40s", "30s", "20s", "10s"], tooltip: { enabled: !1 }, axisBorder: { show: !1 } },
            yaxis: {
                labels: {
                    formatter: function (e) {
                        return e + "%";
                    },
                    offsetX: -15,
                },
            },
        };
        new ApexCharts(document.querySelector("#humidity-chart"), humidity_chart).render();
    }),
        (e.prototype.init = function () {
            this.initCharts();
        }),
        (o.Dashboard = new e()),
        (o.Dashboard.Constructor = e);
})(window.jQuery),
    (function (t) {
        "use strict";
        t(document).ready(function (e) {
            t.Dashboard.init();
        });
    })(window.jQuery);

(data_colors = $("#water-reservoir-chart").data("colors")) && (colors = data_colors.split(","));

water_reservoir_chart = {
    chart: { height: 340, type: "radialBar" },
    plotOptions: {
        radialBar: {
            hollow: { size: "60%" },
            startAngle: -135,
            endAngle: 135,
            dataLabels: {
                name: { fontSize: "16px", color: void 0, offsetY: 92 },
                value: {
                    offsetY: 0,
                    fontSize: "22px",
                    color: void 0,
                    formatter: function (o) {
                        return o + "%";
                    },
                },
            },
        },
    },
    fill: { gradient: { enabled: !0, shade: "dark", shadeIntensity: 0.15, inverseColors: !1, opacityFrom: 1, opacityTo: 1, stops: [0, 50, 65, 91] } },
    stroke: { dashArray: 0 },
    colors: colors,
    series: [67],
    labels: ["980 L"],
    responsive: [{ breakpoint: 340, options: { chart: { height: 280 } } }],
};

new ApexCharts(document.querySelector("#water-reservoir-chart"), water_reservoir_chart).render();

(data_colors = $("#water-consumption-chart").data("colors")) && (colors = data_colors.split(","));

water_consumption_chart = {
    chart: {
        height: 340,
        type: "bar",
        toolbar: { show: !1 },
        events: {
            click: function (o, a, t) {
                console.log(o, a, t);
            },
        },
    },
    colors: colors,
    plotOptions: { bar: { columnWidth: "50%", distributed: !1 } },
    dataLabels: { enabled: !1 },
    series: [{ name: "Consumo", data: [20, 42, 68, 55, 80, 25, 40, 94, 30, 36, 60, 72] }],
    xaxis: { categories: ["Jan.", "Fev.", "Mar.", "Abr.", "Maio", "Jun.", "Jul.", "Ago.", "Set.", "Out.", "Nov.", "Dez."], labels: { style: { colors: colors, fontSize: "14px" } } },
    yaxis: {
        labels: {
            formatter: function (o) {
                return o + " L";
            },
        },
    },
    legend: { offsetY: 7 },
    grid: { row: { colors: ["transparent", "transparent"], opacity: 0.2 }, borderColor: "#f1f3fa" },
};

new ApexCharts(document.querySelector("#water-consumption-chart"), water_consumption_chart).render();
