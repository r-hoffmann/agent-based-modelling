// This should be a css file, but that does not seem to be possible with mesa.

$(function() {
    $('#elements canvas.chartjs-render-monitor').css({
        "position": "relative",
        "top": "500px",
        "margin-bottom": "20px"
    });

    const world_grid = document.getElementsByClassName('world-grid')[2];
 
    var cln = world_grid.cloneNode(true);

    document.getElementById("elements-topbar").appendChild(cln);

    const ctx = world_grid.getContext("2d");
    const size = 3 * 216;
    const road_size = 3 * 2 * 8;
    const grass = "#567D46";
    const grass_starting_coordinates = [
        [0, 0],
        [0, size + road_size / 2 - 1.5 * 216],
        [size + road_size / 2 - 1.5 * 216, 0],
        [size + road_size / 2 - 1.5 * 216, size + road_size / 2 - 1.5 * 216]
    ];
    const road = "#808080";
    const road_properties = [
        [0, size - road_size / 2 - 1.5 * 216, size, road_size],
        [size - road_size / 2 - 1.5 * 216, 0, road_size, size],
    ];

    for(let i in road_properties) {
        let road_property = road_properties[i];
        ctx.beginPath();
        ctx.rect(road_property[0], road_property[1], road_property[2], road_property[3]);
        ctx.fillStyle = road;
        ctx.fill();
    }
    
    for(let i in grass_starting_coordinates) {
        let starting_coordinate = grass_starting_coordinates[i];
        ctx.beginPath();
        ctx.rect(starting_coordinate[0], starting_coordinate[1], (size - road_size) / 2, (size - road_size) / 2);
        ctx.fillStyle = grass;
        ctx.fill();
    }
});