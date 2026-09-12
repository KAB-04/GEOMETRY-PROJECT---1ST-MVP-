from .solver.operations import SUPPORTED_OPERATIONS


TOPIC_DEFINITIONS = [
    {
        "id": "circles",
        "name": "Circles",
        "category": "Euclidean Geometry",
        "dimension": "2d",
        "description": "Circle measurements and coordinate circle relationships.",
        "operation_map": {
            "Area": "circle_area",
            "Circumference": "circle_circumference",
            "Circle intersection": "circle_circle_intersection",
        },
        "examples": [
            "A circle has radius 4 cm. Find its area.",
            "Circle A has center (0,0) and radius 5. Circle B has center (8,0) and radius 5. Find the intersection points.",
        ],
    },
    {
        "id": "triangles",
        "name": "Triangles",
        "category": "Euclidean Geometry",
        "dimension": "2d",
        "description": "Triangle area, perimeter, missing angles, and right-triangle side lengths.",
        "operation_map": {
            "Area": "triangle_area",
            "Perimeter": "triangle_perimeter",
            "Missing angle": "triangle_third_angle",
            "Pythagorean theorem": "pythagoras",
        },
        "examples": [
            "Two angles of a triangle are 45° and 65°. Find the third angle.",
            "A ladder is 6 m from a wall and reaches 8 m high. Find the ladder's length.",
        ],
    },
    {
        "id": "coordinate-geometry",
        "name": "Coordinate Geometry",
        "category": "Coordinate / Analytical Geometry",
        "dimension": "2d",
        "description": "Point-based calculations on the coordinate plane.",
        "operation_map": {
            "Distance": "distance",
            "Midpoint": "midpoint",
            "Slope": "slope",
            "Transformations": "transform",
        },
        "examples": [
            "Find the distance between A(2,3) and B(8,11).",
            "Triangle ABC has vertices A(2,1), B(6,1), and C(4,5). Reflect the triangle across the y-axis.",
        ],
    },
    {
        "id": "three-d-points",
        "name": "3D Points and Planes",
        "category": "Solid Geometry / 3D Geometry",
        "dimension": "3d",
        "description": "Coordinate geometry with 3D points, vectors, lines, and planes.",
        "operation_map": {
            "3D distance": "distance3d",
            "3D midpoint": "midpoint3d",
            "3D vectors": "vector3d",
            "3D lines": "line3d",
            "3D planes": "plane3d",
        },
        "examples": [
            "Point A is at (1, 2, 3) and point B is at (5, 5, 6). Find the distance between A and B.",
        ],
    },
    {
        "id": "cuboids",
        "name": "Cuboids",
        "category": "Solid Geometry / 3D Geometry",
        "dimension": "3d",
        "description": "Volume calculations for rectangular solids.",
        "operation_map": {"Volume": "cuboid_volume"},
        "examples": ["A cuboid has width 5, height 3, and depth 4. Find its volume."],
    },
    {
        "id": "cylinders",
        "name": "Cylinders",
        "category": "Solid Geometry / 3D Geometry",
        "dimension": "3d",
        "description": "Right circular cylinder volume and surface area.",
        "operation_map": {
            "Volume": "cylinder_volume",
            "Lateral surface area": "cylinder_lateral_surface_area",
            "Total surface area": "cylinder_total_surface_area",
        },
        "examples": [
            "A cylindrical water tank has radius 4 m and height 9 m. Find its volume.",
            "A cylinder has radius 5 cm and height 8 cm. Find its total surface area.",
        ],
    },
    {
        "id": "cones",
        "name": "Cones",
        "category": "Solid Geometry / 3D Geometry",
        "dimension": "3d",
        "description": "Right circular cone height derivation and volume planning.",
        "operation_map": {
            "Height from radius and slant height": "cone_height_from_radius_slant_height",
            "Volume": "cone_volume",
        },
        "examples": [
            "A cone has radius 5 cm and slant height 13 cm. Find its height and volume.",
        ],
    },
    {
        "id": "advanced-experimental",
        "name": "Advanced Geometry",
        "category": "Advanced / Experimental",
        "dimension": "mixed",
        "description": "Computational, differential, non-Euclidean, and topology modules exist in the engine but are not fully exposed through the chatbot MVP.",
        "operation_map": {},
        "examples": [],
        "status": "experimental",
    },
]


def get_topics():
    topics = []
    for topic in TOPIC_DEFINITIONS:
        operation_map = topic["operation_map"]
        supported = [
            {"label": label, "operation": operation}
            for label, operation in operation_map.items()
            if operation in SUPPORTED_OPERATIONS
        ]
        if topic.get("status"):
            status = topic["status"]
        elif supported and len(supported) == len(operation_map):
            status = "available"
        elif supported:
            status = "partial"
        else:
            status = "coming_later"
        topics.append(
            {
                "id": topic["id"],
                "name": topic["name"],
                "category": topic["category"],
                "dimension": topic["dimension"],
                "status": status,
                "description": topic["description"],
                "supported_operations": supported,
                "examples": topic["examples"] if status in {"available", "partial"} else [],
            }
        )
    return topics
