// This should be a css file, but that does not seem to be possible with mesa.

$(function() {
    $('#elements canvas.chartjs-render-monitor').css({
        "position": "relative",
        "top": "500px",
        "margin-bottom": "20px"
    });

    const world_grid = document.getElementsByClassName('world-grid')[1];
    const ctx = world_grid.getContext("2d");
    const size = 3 * 216;
    const road_size = 3 * 2 * 8;
    const grass = "#567D46";
    const grass_starting_coordinates = [
        [0, 0],
        [0, size + road_size / 2 - 216],
        [size + road_size / 2 - 216, 0],
        [size + road_size / 2 - 216, size + road_size / 2 - 216]
    ];
    const road = "#808080";
    const road_starting_coordinates = [
        [0, size + road_size / 2 - 216],
        [0, size + road_size / 2 - 216],
        [size + road_size / 2 - 216, 0],
        [size + road_size / 2 - 216, size + road_size / 2 - 216]
    ];


    for(let i in grass_starting_coordinates) {
        let starting_coordinate = starting_coordinates[i];
        ctx.beginPath();
        ctx.rect(starting_coordinate[0], starting_coordinate[1], (size - road_size) / 2, (size - road_size) / 2);
        ctx.fillStyle = grass;
        ctx.fill();
    }
});