
import tkinter as tk
from tkinter import ttk
import random

ROADS = ["NORTH", "EAST", "SOUTH", "WEST"]

COLORS = {
    "NORTH": "#3b82f6",
    "EAST": "#f59e0b",
    "SOUTH": "#22c55e",
    "WEST": "#a855f7"
}

WIDTH = 960
HEIGHT = 560
CX = WIDTH // 2
CY = HEIGHT // 2

ROAD_HALF_WIDTH = 125
MAX_QUEUE = 5
VEHICLE_GAP = 38
TICK_MS = 50
VEHICLE_SPEED = 2.5

GARDEN_RADIUS = 48


class TrafficApp:
    def __init__(self, root):
        self.root = root
        root.title("AI Traffic Flow Optimizer")
        root.geometry("1000x760")
        root.resizable(False, False)

        self.mode = tk.StringVar(value="Smart")
        self.running = False
        self.after_id = None

        self.vehicles = []
        self.next_id = 0
        self.cleared = 0
        self.elapsed = 0.0
        self.green_index = 0
        self.phase_time = 0.0

        self.queues = {road: 0 for road in ROADS}
        self.phase_duration = 10.0

        ttk.Label(
            root,
            text="AI TRAFFIC FLOW OPTIMIZER",
            font=("Arial", 20, "bold")
        ).pack(pady=8)

        controls = ttk.Frame(root, padding=8)
        controls.pack(fill="x")

        ttk.Radiobutton(
            controls, text="Fixed Timer",
            variable=self.mode, value="Fixed"
        ).pack(side="left")

        ttk.Radiobutton(
            controls, text="Smart Signal",
            variable=self.mode, value="Smart"
        ).pack(side="left", padx=8)

        ttk.Button(
            controls, text="Start",
            command=self.start
        ).pack(side="left", padx=4)

        ttk.Button(
            controls, text="Pause",
            command=self.pause
        ).pack(side="left", padx=4)

        ttk.Button(
            controls, text="Reset",
            command=self.reset
        ).pack(side="left", padx=4)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="#e4eddf",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=5)

        self.status = ttk.Label(root, padding=8)
        self.status.pack(anchor="w")

        ttk.Label(
            root,
            text="Vehicles maintain safe gaps and follow traffic signals.",
            padding=8
        ).pack(anchor="w")

        self.draw_roads()
        self.phase_duration = self.green_duration(
            ROADS[self.green_index]
        )
        self.update_display()

    # --------------------------------------------------
    # ROAD DESIGN
    # --------------------------------------------------

    def draw_roads(self):
        c = self.canvas
        c.delete("all")

        c.create_rectangle(
            0, 0, WIDTH, HEIGHT,
            fill="#e4eddf", outline=""
        )

        # Main roads
        c.create_rectangle(
            CX - ROAD_HALF_WIDTH, 0,
            CX + ROAD_HALF_WIDTH, HEIGHT,
            fill="#454b52", outline=""
        )

        c.create_rectangle(
            0, CY - 100,
            WIDTH, CY + 100,
            fill="#454b52", outline=""
        )

        # Dashed road markings
        for y in (CY - 50, CY + 50):
            c.create_line(
                0, y, CX - ROAD_HALF_WIDTH, y,
                fill="white", dash=(12, 9), width=2
            )
            c.create_line(
                CX + ROAD_HALF_WIDTH, y, WIDTH, y,
                fill="white", dash=(12, 9), width=2
            )

        for x in (CX - 62, CX + 62):
            c.create_line(
                x, 0, x, CY - 100,
                fill="white", dash=(12, 9), width=2
            )
            c.create_line(
                x, CY + 100, x, HEIGHT,
                fill="white", dash=(12, 9), width=2
            )

        # Road dividers
        c.create_rectangle(
            CX - 7, 0, CX + 7, CY - 100,
            fill="#b7c9a8", outline="white"
        )
        c.create_rectangle(
            CX - 7, CY + 100, CX + 7, HEIGHT,
            fill="#b7c9a8", outline="white"
        )
        c.create_rectangle(
            0, CY - 7, CX - ROAD_HALF_WIDTH, CY + 7,
            fill="#b7c9a8", outline="white"
        )
        c.create_rectangle(
            CX + ROAD_HALF_WIDTH, CY - 7, WIDTH, CY + 7,
            fill="#b7c9a8", outline="white"
        )

        # Road labels on the roadside verges
        c.create_text(
            CX + 165, 22, text="NORTH ROAD",
            fill="#17212b", font=("Arial", 10, "bold")
        )
        c.create_text(
            CX - 165, HEIGHT - 20, text="SOUTH ROAD",
            fill="#17212b", font=("Arial", 10, "bold")
        )
        c.create_text(
            95, CY - 125, text="WEST ROAD",
            fill="#17212b", font=("Arial", 10, "bold")
        )
        c.create_text(
            WIDTH - 95, CY - 125, text="EAST ROAD",
            fill="#17212b", font=("Arial", 10, "bold")
        )

        # Stop lines
        c.create_line(
            CX - 115, CY - 105, CX - 15, CY - 105,
            fill="white", width=4
        )
        c.create_line(
            CX + 15, CY + 105, CX + 115, CY + 105,
            fill="white", width=4
        )
        c.create_line(
            CX - 130, CY - 88, CX - 130, CY - 15,
            fill="white", width=4
        )
        c.create_line(
            CX + 130, CY + 15, CX + 130, CY + 88,
            fill="white", width=4
        )

        # Central garden
        c.create_oval(
            CX - GARDEN_RADIUS, CY - GARDEN_RADIUS,
            CX + GARDEN_RADIUS, CY + GARDEN_RADIUS,
            fill="#315e3b", outline="#d8c878", width=3
        )
        c.create_oval(
            CX - 41, CY - 41, CX + 41, CY + 41,
            fill="#4f8b4b", outline="#a8cf78", width=2
        )

        # Bushes
        for dx, dy in [
            (-28, -18), (0, -32), (28, -18),
            (-30, 12), (30, 12), (-15, 29), (15, 29)
        ]:
            c.create_oval(
                CX + dx - 7, CY + dy - 5,
                CX + dx + 7, CY + dy + 5,
                fill="#1e6b36", outline="#83bd65"
            )

        # Trees
        for dx, dy in [(-18, -8), (18, -8), (0, 17)]:
            c.create_rectangle(
                CX + dx - 2, CY + dy + 2,
                CX + dx + 2, CY + dy + 10,
                fill="#80502b", outline=""
            )
            c.create_oval(
                CX + dx - 8, CY + dy - 8,
                CX + dx + 8, CY + dy + 5,
                fill="#176b35", outline="#8ac878"
            )

        # Traffic lights in roadside areas
        positions = {
            "NORTH": (CX + 150, CY - 125),
            "EAST": (CX + 165, CY + 120),
            "SOUTH": (CX - 150, CY + 125),
            "WEST": (CX - 165, CY - 120)
        }

        self.lights = {}

        for road, (x, y) in positions.items():
            c.create_rectangle(
                x - 23, y - 19, x + 23, y + 19,
                fill="#202020", outline="white", width=2
            )

            red = c.create_oval(
                x - 17, y - 11, x - 6, y,
                fill="#ff4545", outline=""
            )
            yellow = c.create_oval(
                x - 5, y - 11, x + 6, y,
                fill="#5a5020", outline=""
            )
            green = c.create_oval(
                x + 7, y - 11, x + 18, y,
                fill="#205a32", outline=""
            )

            self.lights[road] = (red, yellow, green)

        self.vehicle_drawings = []

    # --------------------------------------------------
    # VEHICLE ROUTE INFORMATION
    # progress is distance along each vehicle's road
    # --------------------------------------------------

    def route_info(self, road):
        if road == "NORTH":
            return HEIGHT + 50, CY - 115 + 25

        if road == "SOUTH":
            return HEIGHT + 50, HEIGHT + 25 - (CY + 115)

        if road == "EAST":
            return WIDTH + 50, WIDTH + 25 - (CX + 140)

        return WIDTH + 50, CX - 140 + 25

    def vehicle_distance(self, vehicle):
        total, _ = self.route_info(vehicle["road"])
        return vehicle["progress"] * total

    def stop_distance(self, road):
        return self.route_info(road)[1]

    # --------------------------------------------------
    # CONTROLS
    # --------------------------------------------------

    def start(self):
        if not self.running:
            self.running = True
            self.tick()

    def pause(self):
        self.running = False

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def reset(self):
        self.pause()

        self.vehicles.clear()
        self.queues = {road: 0 for road in ROADS}
        self.next_id = 0
        self.cleared = 0
        self.elapsed = 0.0
        self.green_index = 0
        self.phase_time = 0.0

        self.draw_roads()
        self.phase_duration = self.green_duration("NORTH")
        self.update_display()

    # --------------------------------------------------
    # SIGNAL TIMING
    # --------------------------------------------------

    def green_duration(self, road):
        if self.mode.get() == "Fixed":
            return 10.0

        return max(
            6.0,
            min(18.0, 6.0 + self.queues[road] * 2.0)
        )

    # --------------------------------------------------
    # CREATE VEHICLES
    # --------------------------------------------------

    def spawn_vehicle(self, road):
        if self.queues[road] >= MAX_QUEUE:
            return

        self.next_id += 1

        vehicle = {
            "id": self.next_id,
            "road": road,
            "kind": random.choices(
                ["car", "bike", "truck"],
                weights=[6, 3, 1],
                k=1
            )[0],
            "state": "waiting",
            "progress": 0.0
        }

        self.vehicles.append(vehicle)
        self.queues[road] += 1

    # --------------------------------------------------
    # WAITING VEHICLE POSITIONS
    # Keep queued vehicles behind moving vehicles.
    # --------------------------------------------------

    def vehicle_position(self, vehicle):
        road = vehicle["road"]
        total, stop = self.route_info(road)

        if vehicle["state"] == "waiting":
            earlier_waiting = [
                v for v in self.vehicles
                if v["road"] == road
                and v["state"] == "waiting"
                and v["id"] < vehicle["id"]
            ]

            # Leave room for vehicles recently released
            # from the queue.
            blocking = sum(
                1 for v in self.vehicles
                if v["road"] == road
                and v["state"] == "moving"
                and self.vehicle_distance(v) < stop + VEHICLE_GAP
            )

            distance = stop - (
                len(earlier_waiting) + blocking
            ) * VEHICLE_GAP

        else:
            distance = vehicle["progress"] * total

        if road == "NORTH":
            return CX - 82, -25 + distance, False

        if road == "SOUTH":
            return CX + 82, HEIGHT + 25 - distance, False

        if road == "EAST":
            return WIDTH + 25 - distance, CY + 72, True

        return -25 + distance, CY - 72, True

    # --------------------------------------------------
    # VEHICLE DRAWING
    # --------------------------------------------------

    def draw_vehicle(self, x, y, kind, horizontal, color):
        c = self.canvas
        items = []

        if kind == "truck":
            if horizontal:
                items.extend([
                    c.create_rectangle(
                        x - 14, y - 7, x + 14, y + 7,
                        fill="#e5e7eb", outline="#111827"
                    ),
                    c.create_rectangle(
                        x - 14, y - 7, x - 4, y + 7,
                        fill="#f97316", outline="#111827"
                    ),
                    c.create_rectangle(
                        x + 5, y - 5, x + 11, y + 5,
                        fill="#93c5fd", outline="#111827"
                    )
                ])
            else:
                items.extend([
                    c.create_rectangle(
                        x - 7, y - 14, x + 7, y + 14,
                        fill="#e5e7eb", outline="#111827"
                    ),
                    c.create_rectangle(
                        x - 7, y - 14, x + 7, y - 4,
                        fill="#f97316", outline="#111827"
                    ),
                    c.create_rectangle(
                        x - 5, y + 5, x + 5, y + 11,
                        fill="#93c5fd", outline="#111827"
                    )
                ])

        elif kind == "bike":
            if horizontal:
                items.extend([
                    c.create_oval(
                        x - 9, y - 5, x - 1, y + 5,
                        fill="#20252a", outline="white"
                    ),
                    c.create_oval(
                        x + 2, y - 5, x + 10, y + 5,
                        fill="#20252a", outline="white"
                    ),
                    c.create_line(
                        x - 5, y, x + 6, y,
                        fill="#facc15", width=3
                    )
                ])
            else:
                items.extend([
                    c.create_oval(
                        x - 5, y - 9, x + 5, y - 1,
                        fill="#20252a", outline="white"
                    ),
                    c.create_oval(
                        x - 5, y + 2, x + 5, y + 10,
                        fill="#20252a", outline="white"
                    ),
                    c.create_line(
                        x, y - 5, x, y + 6,
                        fill="#facc15", width=3
                    )
                ])

        else:
            if horizontal:
                items.extend([
                    c.create_rectangle(
                        x - 11, y - 6, x + 11, y + 6,
                        fill=color, outline="#111827"
                    ),
                    c.create_rectangle(
                        x - 4, y - 4, x + 5, y + 4,
                        fill="#dbeafe", outline=""
                    )
                ])
            else:
                items.extend([
                    c.create_rectangle(
                        x - 6, y - 11, x + 6, y + 11,
                        fill=color, outline="#111827"
                    ),
                    c.create_rectangle(
                        x - 4, y - 4, x + 4, y + 5,
                        fill="#dbeafe", outline=""
                    )
                ])

        return items

    # --------------------------------------------------
    # INTERSECTION SAFETY
    # Hold the next signal until all moving vehicles
    # from the previous phase have cleared the junction.
    # --------------------------------------------------

    def intersection_clear(self):
        for vehicle in self.vehicles:
            if vehicle["state"] != "moving":
                continue

            road = vehicle["road"]
            distance = self.vehicle_distance(vehicle)

            if road in ("NORTH", "SOUTH"):
                zone_start = CY - 100 + 25
                zone_end = CY + 100 + 25
            elif road == "EAST":
                zone_start = WIDTH + 25 - (CX + ROAD_HALF_WIDTH)
                zone_end = WIDTH + 25 - (CX - ROAD_HALF_WIDTH)
            else:
                zone_start = CX - ROAD_HALF_WIDTH + 25
                zone_end = CX + ROAD_HALF_WIDTH + 25

            if zone_start <= distance <= zone_end:
                return False

            # Also wait for approaching vehicles that have
            # already been released toward the intersection.
            stop = self.stop_distance(road)
            if stop <= distance < zone_start:
                return False

        return True

    # --------------------------------------------------
    # MAIN SIMULATION LOOP
    # --------------------------------------------------

    def tick(self):
        if not self.running:
            return

        dt = TICK_MS / 1000
        self.elapsed += dt
        self.phase_time += dt

        chances = {
            "NORTH": 0.10,
            "EAST": 0.12,
            "SOUTH": 0.09,
            "WEST": 0.11
        }

        for road in ROADS:
            if random.random() < chances[road]:
                self.spawn_vehicle(road)

        active_road = ROADS[self.green_index]

        # Stop releasing vehicles when the green time ends.
        if self.phase_time < self.phase_duration:
            waiting = sorted(
                [
                    v for v in self.vehicles
                    if v["road"] == active_road
                    and v["state"] == "waiting"
                ],
                key=lambda v: v["id"]
            )

            moving = [
                v for v in self.vehicles
                if v["road"] == active_road
                and v["state"] == "moving"
            ]

            can_release = not moving

            if moving:
                nearest_to_stop = min(
                    self.vehicle_distance(v) - self.stop_distance(active_road)
                    for v in moving
                )
                can_release = nearest_to_stop >= VEHICLE_GAP

            if waiting and can_release:
                vehicle = waiting[0]
                total, stop = self.route_info(active_road)
                vehicle["state"] = "moving"
                vehicle["progress"] = stop / total

                self.queues[active_road] = max(
                    0, self.queues[active_road] - 1
                )

        # Advance vehicles using a distance-based speed.
        for vehicle in self.vehicles[:]:
            if vehicle["state"] == "moving":
                total, _ = self.route_info(vehicle["road"])
                vehicle["progress"] += VEHICLE_SPEED / total

                if vehicle["progress"] >= 1.0:
                    self.vehicles.remove(vehicle)
                    self.cleared += 1

        # Switch only when the old traffic has cleared.
        if (
            self.phase_time >= self.phase_duration
            and self.intersection_clear()
        ):
            self.green_index = (
                self.green_index + 1
            ) % len(ROADS)

            self.phase_time = 0.0
            self.phase_duration = self.green_duration(
                ROADS[self.green_index]
            )

        self.update_display()
        self.after_id = self.root.after(TICK_MS, self.tick)

    # --------------------------------------------------
    # UPDATE DISPLAY
    # --------------------------------------------------

    def update_display(self):
        c = self.canvas
        active_road = ROADS[self.green_index]

        for road, parts in self.lights.items():
            red, yellow, green = parts
            is_green = road == active_road

            c.itemconfigure(
                red,
                fill="#5a2020" if is_green else "#ff4545"
            )
            c.itemconfigure(yellow, fill="#5a5020")
            c.itemconfigure(
                green,
                fill="#32e875" if is_green else "#205a32"
            )

        for item in self.vehicle_drawings:
            c.delete(item)

        self.vehicle_drawings = []

        for vehicle in self.vehicles:
            x, y, horizontal = self.vehicle_position(vehicle)

            self.vehicle_drawings.extend(
                self.draw_vehicle(
                    x, y, vehicle["kind"],
                    horizontal, COLORS[vehicle["road"]]
                )
            )

        self.status.config(
            text=(
                f"Mode: {self.mode.get()} | "
                f"Time: {self.elapsed:.1f}s | "
                f"Green: {active_road} | "
                f"Vehicles passed: {self.cleared} | "
                f"Vehicles waiting: {sum(self.queues.values())}"
            )
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficApp(root)
    root.mainloop()
