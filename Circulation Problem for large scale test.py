from collections import deque
from time import perf_counter
import time

class Edge:
    def __init__(self, to, reverse, capacity):
        self.to = to
        self.reverse = reverse
        self.capacity = capacity
        self.flow = 0
class Dinic:
    def __init__(self, n):
        self.graph = [[] for _ in range(n)]
    def add_edge(self, u, v, capacity):
        forward = Edge(v, len(self.graph[v]), capacity)
        reverse = Edge(u, len(self.graph[u]), 0)

        self.graph[u].append(forward)
        self.graph[v].append(reverse)
        return forward
    def bfs(self, source, sink):
        self.level = [-1] * len(self.graph)
        self.level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for edge in self.graph[u]:
                if (edge.capacity - edge.flow > 0 and
                        self.level[edge.to] < 0):
                    self.level[edge.to] = self.level[u] + 1
                    queue.append(edge.to)
        return self.level[sink] >= 0
    def send_flow(self, u, sink, flow):
        if u == sink:
            return flow
        while self.next_edge[u] < len(self.graph[u]):
            edge = self.graph[u][self.next_edge[u]]
            if (self.level[edge.to] ==
                    self.level[u] + 1):
                residual = edge.capacity - edge.flow
                if residual > 0:
                    sent = self.send_flow(
                        edge.to,
                        sink,
                        min(flow, residual)
                    )
                    if sent > 0:
                        edge.flow += sent

                        reverse = self.graph[
                            edge.to
                        ][edge.reverse]

                        reverse.flow -= sent
                        return sent
            self.next_edge[u] += 1
        return 0
    def max_flow(self, source, sink):
        total_flow = 0

        while self.bfs(source, sink):
            self.next_edge = [0] * len(self.graph)

            while True:
                sent = self.send_flow(
                    source,
                    sink,
                    float("inf")
                )
                if sent == 0:
                    break
                total_flow += sent
        return total_flow
def solve_circulation(vertices, edges, balance):

    # Validate global balance
    
    total_balance = sum(
        balance[v] for v in vertices
    )

    if total_balance != 0:
        return None
    index = {
        v: i for i, v in enumerate(vertices)
    }
    remaining = {
        v: balance[v] for v in vertices
    }
    super_source = len(vertices)
    super_sink = len(vertices) + 1
    dinic = Dinic(len(vertices) + 2)
    transformed_edges = []

    # Lower-bound transformation
    
    for u, v, lower, capacity in edges:
        if lower < 0 or lower > capacity:
            return None
        transformed_capacity = (
            capacity - lower
        )
        edge_reference = dinic.add_edge(
            index[u],
            index[v],
            transformed_capacity
        )
        transformed_edges.append(
            (u, v, lower, edge_reference)
        )
        remaining[u] -= lower
        remaining[v] += lower
    required_flow = 0

    # Add balance edges
    
    for v in vertices:
        if remaining[v] > 0:
            dinic.add_edge(
                super_source,
                index[v],
                remaining[v]
            )
            required_flow += remaining[v]

        elif remaining[v] < 0:
            dinic.add_edge(
                index[v],
                super_sink,
                -remaining[v]
            )
    max_flow = dinic.max_flow(
        super_source,
        super_sink
    )
    if max_flow != required_flow:
        return None

    # Recover original flows
    
    final_flow = {}
    for u, v, lower, edge in transformed_edges:
        final_flow[(u, v)] = (
            lower + edge.flow
        )
    return final_flow

# ------------------------------
# Q7 Base Test Case
# ------------------------------

V = ["A", "B", "C", "D"]
b = {
    "A": 6,
    "B": 0,
    "C": 0,
    "D": -6
}
E = [
    ("A", "B", 2, 5),
    ("A", "C", 1, 4),
    ("B", "C", 1, 3),
    ("B", "D", 2, 4),
    ("C", "D", 2, 5)
]

result = solve_circulation(V, E, b)

if result is None:
    print("INFEASIBLE")
else:
    print("FEASIBLE")

    for edge, flow in result.items():
        print(
            edge[0], "->", edge[1],
            ": Flow =", flow
        )

#---------------------------
#TEST DATA FOR LARGE SCALE
#---------------------------
# -------------------------------------------------
# Q7 Performance Test for Larger Networks
# -------------------------------------------------

def generate_test_network(n):
    vertices = list(range(n))
    edges = []

    # Source supplies 10 units
    # Last vertex consumes 10 units
    balance = {v: 0 for v in vertices}
    balance[0] = 10
    balance[n - 1] = -10

    # Main path guarantees that a feasible solution exists
    for i in range(n - 1):
        edges.append((i, i + 1, 0, 10))

    # Additional edges increase network size
    for i in range(n - 2):
        edges.append((i, i + 2, 0, 5))

    return vertices, edges, balance


sizes = [50, 100, 200, 400, 800]
repetitions = 30

print("\nPERFORMANCE TEST")
print("-" * 60)
print(
    f"{'Vertices':<12}"
    f"{'Edges':<12}"
    f"{'Avg Time (ms)':<18}"
    f"{'Result'}"
)
print("-" * 60)


for size in sizes:

    V_test, E_test, b_test = generate_test_network(size)

    total_time = 0
    result = None

    for _ in range(repetitions):

        start = time.perf_counter()

        result = solve_circulation(
            V_test,
            E_test,
            b_test
        )

        end = time.perf_counter()

        total_time += (end - start)

    average_time_ms = (
        total_time / repetitions
    ) * 1000

    status = (
        "Feasible"
        if result is not None
        else "Infeasible"
    )

    print(
        f"{len(V_test):<12}"
        f"{len(E_test):<12}"
        f"{average_time_ms:<18.4f}"
        f"{status}"
    )
