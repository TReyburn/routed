"""Simple Travelling Salesperson Problem (TSP) between cities"""
from dataclasses import dataclass

from ortools.constraint_solver import pywrapcp, routing_enums_pb2  # type: ignore


@dataclass
class InputDataModel:
    """InputDataModel"""

    distance_matrix: list[list[int]]
    num_vehicles: int
    depot_position: int


@dataclass
class OutputDataModel:
    """OutputDataModel"""

    path: list[int]
    distance: int


@dataclass
class RouteConstraints:
    """RouteConstraints"""

    name: str
    slack: int
    capacity: int
    fixed_start: bool = True


def create_data_model() -> InputDataModel:
    """Stores the data for the problem"""
    distance_matrix = [
        [0, 2451, 713, 1018, 1631, 1374, 2408, 213, 2571, 875, 1420, 2145, 1972],
        [2451, 0, 1745, 1524, 831, 1240, 959, 2596, 403, 1589, 1374, 357, 579],
        [713, 1745, 0, 355, 920, 803, 1737, 851, 1858, 262, 940, 1453, 1260],
        [1018, 1524, 355, 0, 700, 862, 1395, 1123, 1584, 466, 1056, 1280, 987],
        [1631, 831, 920, 700, 0, 663, 1021, 1769, 949, 796, 879, 586, 371],
        [1374, 1240, 803, 862, 663, 0, 1681, 1551, 1765, 547, 225, 887, 999],
        [2408, 959, 1737, 1395, 1021, 1681, 0, 2493, 678, 1724, 1891, 1114, 701],
        [213, 2596, 851, 1123, 1769, 1551, 2493, 0, 2699, 1038, 1605, 2300, 2099],
        [2571, 403, 1858, 1584, 949, 1765, 678, 2699, 0, 1744, 1645, 653, 600],
        [875, 1589, 262, 466, 796, 547, 1724, 1038, 1744, 0, 679, 1272, 1162],
        [1420, 1374, 940, 1056, 879, 225, 1891, 1605, 1645, 679, 0, 1017, 1200],
        [2145, 357, 1453, 1280, 586, 887, 1114, 2300, 653, 1272, 1017, 0, 504],
        [1972, 579, 1260, 987, 371, 999, 701, 2099, 600, 1162, 1200, 504, 0],
    ]
    num_vehicles = 4
    depot = 0
    return InputDataModel(distance_matrix, num_vehicles, depot)


def default_constraints() -> RouteConstraints:
    """creates default constraints"""
    return RouteConstraints("Distance", 0, 5500)


def create_route(
    data: InputDataModel,
    constraints: RouteConstraints,
) -> list[OutputDataModel]:
    """creates the route solution given the input"""
    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data.distance_matrix), data.num_vehicles, data.depot_position
    )

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        """Returns the distance between the two nodes"""
        # Convert from routing variable Index to distance matrix NodeIndex
        from_node: int = manager.IndexToNode(from_index)
        to_node: int = manager.IndexToNode(to_index)
        return data.distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint
    routing.AddDimension(
        transit_callback_index,
        constraints.slack,  # no slack
        constraints.capacity,  # vehicle maximum travel distance
        constraints.fixed_start,  # fixed start cumulative to zero
        constraints.name,
    )
    distance_dimension = routing.GetDimensionOrDie(constraints.name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC  # pylint: disable=E1101
    )

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)
    if solution is not None:
        return parse_solution(manager, routing, solution, data.num_vehicles)
    raise Exception("err no solution")


def parse_solution(
    manager: pywrapcp.RoutingIndexManager,
    routing: pywrapcp.RoutingModel,
    solution: pywrapcp.RoutingModel,
    num_vehicles: int,
) -> list[OutputDataModel]:
    """Parses solution into object"""
    plan_output: list[OutputDataModel] = []
    for vehicle in range(num_vehicles):
        sequence_output: list[int] = []
        index = routing.Start(vehicle)
        route_distance = 0
        while not routing.IsEnd(index):
            sequence_output.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle
            )
        sequence_output.append(manager.IndexToNode(index))
        plan_output.append(OutputDataModel(sequence_output, route_distance))
    return plan_output


def main() -> None:
    """Entry point of the program"""
    data = create_data_model()
    constraints = default_constraints()

    try:
        outcome = create_route(data, constraints)
        print(outcome)
    except Exception as err:  # pylint: disable=broad-except
        print(err)


if __name__ == "__main__":
    main()
