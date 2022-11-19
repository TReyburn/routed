"""Solves vehicle routing problems given a distance matrix and associated constraints"""
from ortools.constraint_solver import pywrapcp, routing_enums_pb2  # type: ignore

from src.route.consts import __default_timeout__
from src.route.models import InputDataModel, OutputDataModel, RouteConstraints


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

    # TODO: we will likely need to support different kinds of callbacks;
    #  thus a Callback factory of sorts may be required
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
        constraints.slack,
        constraints.capacity,
        constraints.fixed_start,
        constraints.name,
    )
    distance_dimension = routing.GetDimensionOrDie(constraints.name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC  # pylint: disable=E1101
    )

    # Set time limit
    search_parameters.time_limit.FromSeconds(__default_timeout__)

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)
    # TODO: how can this be tested easier? Maybe create a callback and return the callback?
    if solution is not None:
        return parse_solution(manager, routing, solution, data.num_vehicles)
    raise Exception("err no solution")


# TODO: this function is currently not testable outside the scope of integration testing
def parse_solution(
    manager: pywrapcp.RoutingIndexManager,
    routing: pywrapcp.RoutingModel,
    solution: pywrapcp.RoutingModel,
    num_vehicles: int,
) -> list[OutputDataModel]:
    """Parses solution into object"""
    plan_output: list[OutputDataModel] = []

    # grab the solution route for each vehicle
    for vehicle in range(num_vehicles):
        sequence_output: list[int] = []
        index = routing.Start(vehicle)
        route_distance = 0

        # iterate through the route
        while not routing.IsEnd(index):
            sequence_output.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle
            )

        # append the final route stop (depot)
        sequence_output.append(manager.IndexToNode(index))

        # create the route output model and append to list of vehicle routes
        plan_output.append(OutputDataModel(sequence_output, route_distance))
    return plan_output
