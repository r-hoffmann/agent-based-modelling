$(function() {
    // Fix overlap elements
    $('#elements canvas.chartjs-render-monitor').css({
        "position": "relative",
        "top": "700px",
        "margin-bottom": "20px"
    });

    // Copy world grid and set z-index such that we can draw on this element
    const world_grid = document.getElementsByClassName('world-grid')[1];
    let cln = world_grid.cloneNode(true);
    document.getElementById("elements").appendChild(cln);
    $(cln).css({
        "z-index": -1
    })

    // Shared variables
    window.ctx = cln.getContext("2d");
    window.size = 3 * 216;
    window.color_grass = "#567D46";
    window.color_road = "#808080";
    window.color_line = "#FFFFFF";

    // Color the edges of the roads
    const west = '#ff0303';
    const north = '#ffc105';
    const east = '#03ff03';
    const south = '#8205ff';
    $('canvas.world-grid').css({
        "border-left": "5px solid " + west,
        "border-top": "5px solid " + north,
        "border-right": "5px solid " + east,
        "border-bottom": "5px solid " + south,
    });

    // Load intersection
    intersection_specific();
});