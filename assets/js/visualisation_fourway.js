function intersection_specific() {
    // Shared variables
    const ctx = window.ctx;
    const size = window.size;
    const color_grass = window.color_grass;
    const color_road = window.color_road;
    const color_line = window.color_line;

    const road_size = 3 * 2 * 8;
    const grass_starting_coordinates = [
        [0, 0],
        [0, size + road_size / 2 - 1.5 * 216],
        [size + road_size / 2 - 1.5 * 216, 0],
        [size + road_size / 2 - 1.5 * 216, size + road_size / 2 - 1.5 * 216]
    ];
    const road_properties = [
        [0, size - road_size / 2 - 1.5 * 216, size, road_size],
        [size - road_size / 2 - 1.5 * 216, 0, road_size, size],
    ];
    const stopping_line_properties = [
        [size - road_size / 2 - 1.5 * 216, size - road_size / 2 - 1.5 * 216 - 2, road_size / 2, 2],
        [size - road_size / 2 - 1.5 * 216, size - 1.5 * 216, 2, road_size / 2],
        [size + road_size / 2 - 1.5 * 216, size - road_size / 2 - 1.5 * 216, 2, road_size / 2],
        [size - 1.5 * 216, size + road_size / 2 - 1.5 * 216 - 2, road_size / 2, 2],
    ];

    for(let i in road_properties) {
        let road_property = road_properties[i];
        ctx.beginPath();
        ctx.rect(road_property[0], road_property[1], road_property[2], road_property[3]);
        ctx.fillStyle = color_road;
        ctx.fill();
    }
    
    for(let i in stopping_line_properties) {
        let stopping_line_property = stopping_line_properties[i];
        ctx.beginPath();
        ctx.rect(stopping_line_property[0], stopping_line_property[1], stopping_line_property[2], stopping_line_property[3]);
        ctx.fillStyle = color_line;
        ctx.fill();
    }
    
    for(let i in grass_starting_coordinates) {
        let starting_coordinate = grass_starting_coordinates[i];
        ctx.beginPath();
        ctx.rect(starting_coordinate[0], starting_coordinate[1], (size - road_size) / 2, (size - road_size) / 2);
        ctx.fillStyle = color_grass;
        ctx.fill();
    }
}