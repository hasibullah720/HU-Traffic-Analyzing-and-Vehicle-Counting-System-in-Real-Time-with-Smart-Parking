"""
Simple Tkinter GUI for HU Traffic Analyzing System
Clean frontend with essential controls and live statistics
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import cv2
from PIL import Image, ImageTk

from scripts import config


class ModernDashboard:
    """Simple and clean dashboard UI with backend-compatible hooks"""

    def __init__(self, root):
        self.root = root
        self.root.title("HU Traffic Analyzing System")
        self.root.geometry("1180x760")
        self.root.configure(bg="#f4f6f8")

        self.video_source = config.VIDEO_SOURCE if config.VIDEO_SOURCE is not None else "NOT_SELECTED"
        self.is_running = False

        self.stats = {
            "total_vehicles": 0,
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0,
            "parking_occupied": 0,
            "parking_available": config.TOTAL_PARKING_SLOTS,
            "parking_total": config.TOTAL_PARKING_SLOTS,
        }

        self.detector = None
        self.tracker = None
        self.counter = None
        self.parking_manager = None
        self.rental_manager = None
        self.database = None
        self.preprocessor = None
        self.report_generator = None

        self.video_photo = None

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        top.pack(fill=tk.X, padx=12, pady=(12, 6))

        tk.Label(
            top,
            text="HU Traffic Analyzing and Vehicle Counting System",
            font=("Segoe UI", 15, "bold"),
            bg="#ffffff",
            fg="#1f2937",
        ).pack(side=tk.LEFT, padx=12, pady=10)

        self.time_label = tk.Label(
            top,
            text="",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#6b7280",
        )
        self.time_label.pack(side=tk.RIGHT, padx=12)
        self._tick_clock()

        controls = tk.Frame(self.root, bg="#f4f6f8")
        controls.pack(fill=tk.X, padx=12, pady=(2, 8))

        self.start_btn = tk.Button(
            controls,
            text="Start",
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="white",
            activebackground="#15803d",
            relief="flat",
            padx=16,
            pady=8,
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = tk.Button(
            controls,
            text="Stop",
            font=("Segoe UI", 10, "bold"),
            bg="#dc2626",
            fg="white",
            activebackground="#b91c1c",
            relief="flat",
            padx=16,
            pady=8,
            command=self.stop_system,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            controls,
            text="Upload Video",
            font=("Segoe UI", 10),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            relief="flat",
            padx=14,
            pady=8,
            command=self.select_video_file,
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            controls,
            text="Use Webcam",
            font=("Segoe UI", 10),
            bg="#0ea5e9",
            fg="white",
            activebackground="#0284c7",
            relief="flat",
            padx=14,
            pady=8,
            command=self.use_webcam,
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            controls,
            text="Export Reports",
            font=("Segoe UI", 10),
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            relief="flat",
            padx=14,
            pady=8,
            command=self.export_reports,
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            controls,
            text="Reset Counts",
            font=("Segoe UI", 10),
            bg="#6b7280",
            fg="white",
            activebackground="#4b5563",
            relief="flat",
            padx=14,
            pady=8,
            command=self.reset_counts,
        ).pack(side=tk.LEFT)

        self.source_label = tk.Label(
            controls,
            text="Source: Click 'Upload Video' or 'Use Webcam'",
            font=("Segoe UI", 10),
            bg="#f4f6f8",
            fg="#dc2626",
        )
        self.source_label.pack(side=tk.RIGHT)

        main = tk.Frame(self.root, bg="#f4f6f8")
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        left = tk.Frame(main, bg="#ffffff", bd=1, relief="solid")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.video_label = tk.Label(
            left,
            text="Video preview will appear here",
            font=("Segoe UI", 12),
            bg="#111827",
            fg="#d1d5db",
            width=80,
            height=30,
        )
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        right = tk.Frame(main, bg="#ffffff", bd=1, relief="solid", width=320)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        self._build_stats_panel(right)

    def _build_stats_panel(self, parent):
        tk.Label(
            parent,
            text="Live Statistics",
            font=("Segoe UI", 13, "bold"),
            bg="#ffffff",
            fg="#111827",
        ).pack(anchor="w", padx=12, pady=(12, 8))

        self.total_vehicles_label = self._add_stat_row(parent, "Total Vehicles", "0")
        self.car_count_label = self._add_stat_row(parent, "Cars", "0")
        self.motorcycle_count_label = self._add_stat_row(parent, "Motorcycles", "0")
        self.bus_count_label = self._add_stat_row(parent, "Buses", "0")
        self.truck_count_label = self._add_stat_row(parent, "Trucks", "0")

        ttk.Separator(parent, orient="horizontal").pack(fill=tk.X, padx=12, pady=8)

        tk.Label(
            parent,
            text="Parking",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#111827",
        ).pack(anchor="w", padx=12, pady=(0, 6))

        self.occupied_label = self._add_stat_row(parent, "Occupied", "0")
        self.available_label = self._add_stat_row(parent, "Available", str(config.TOTAL_PARKING_SLOTS))

        ttk.Separator(parent, orient="horizontal").pack(fill=tk.X, padx=12, pady=8)

        tk.Label(
            parent,
            text="Rental Revenue",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#111827",
        ).pack(anchor="w", padx=12, pady=(0, 6))

        self.gross_label = self._add_stat_row(parent, "Gross", "Rs. 0")
        self.discount_label = self._add_stat_row(parent, "Discount", "-Rs. 0")
        self.net_label = self._add_stat_row(parent, "Net", "Rs. 0")

        ttk.Separator(parent, orient="horizontal").pack(fill=tk.X, padx=12, pady=8)

        self.fps_label = tk.Label(
            parent,
            text="FPS: 0.0",
            font=("Consolas", 11, "bold"),
            bg="#ffffff",
            fg="#1d4ed8",
        )
        self.fps_label.pack(anchor="w", padx=12, pady=(0, 10))

        self.log_text = tk.Text(parent, height=12, font=("Consolas", 9), bg="#f9fafb", fg="#111827")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.log_text.insert(tk.END, "System ready.\n")
        self.log_text.config(state=tk.DISABLED)

    def _add_stat_row(self, parent, label, value):
        row = tk.Frame(parent, bg="#ffffff")
        row.pack(fill=tk.X, padx=12, pady=3)

        tk.Label(
            row,
            text=label,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#374151",
        ).pack(side=tk.LEFT)

        value_label = tk.Label(
            row,
            text=value,
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#111827",
        )
        value_label.pack(side=tk.RIGHT)
        return value_label

    def _tick_clock(self):
        self.time_label.config(text=datetime.now().strftime("%d %b %Y  %I:%M:%S %p"))
        self.root.after(1000, self._tick_clock)

    def append_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def select_video_file(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Stop the system before changing source.")
            return

        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("All Files", "*.*")],
        )

        if file_path:
            self.video_source = file_path
            filename = file_path.split('/')[-1].split('\\')[-1]  # Get just filename
            self.source_label.config(text=f"Source: {filename}", fg="#16a34a")
            self.append_log(f"Video file selected: {filename}")

    def use_webcam(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Stop the system before changing source.")
            return

        self.video_source = 0
        self.source_label.config(text="Source: Webcam", fg="#16a34a")
        self.append_log("Switched to webcam")

    def get_video_source(self):
        return self.video_source

    def stop_system(self):
        self.is_running = False
        self.append_log("Stop signal sent")

    def reset_counts(self):
        if self.counter:
            self.counter.reset_counts()

        self.update_statistics(
            {
                "total_vehicles": 0,
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
            }
        )
        self.append_log("Counts reset")

    def export_reports(self):
        if not self.database:
            messagebox.showwarning("Warning", "Database not initialized.")
            return

        try:
            if not self.report_generator:
                from scripts.reports import ReportGenerator

                self.report_generator = ReportGenerator(self.database)

            reports = self.report_generator.generate_all_reports()
            report_list = "\n".join([f"- {key.replace('_', ' ').title()}" for key in reports.keys()])
            messagebox.showinfo("Reports Generated", f"Reports generated successfully:\n\n{report_list}")
            self.append_log("Reports exported")
        except Exception as error:
            messagebox.showerror("Error", f"Could not generate reports:\n{error}")
            self.append_log(f"Report error: {error}")

    def update_video_display(self, frame):
        try:
            # Optimize: resize only if needed, avoid extra conversions
            h, w = frame.shape[:2]
            target_w, target_h = 820, 600
            
            # Skip resize if frame is already close to target size
            if abs(w - target_w) < 50 and abs(h - target_h) < 50:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = cv2.resize(rgb, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            
            image = Image.fromarray(rgb)
            self.video_photo = ImageTk.PhotoImage(image=image)
            self.video_label.config(image=self.video_photo, text="")
        except Exception as error:
            self.append_log(f"Video display error: {error}")

    def update_statistics(self, stats_dict):
        self.stats.update(stats_dict)

        self.total_vehicles_label.config(text=str(self.stats["total_vehicles"]))
        self.car_count_label.config(text=str(self.stats["car"]))
        self.motorcycle_count_label.config(text=str(self.stats["motorcycle"]))
        self.bus_count_label.config(text=str(self.stats["bus"]))
        self.truck_count_label.config(text=str(self.stats["truck"]))

        self.occupied_label.config(text=str(self.stats.get("parking_occupied", 0)))
        self.available_label.config(text=str(self.stats.get("parking_available", config.TOTAL_PARKING_SLOTS)))

        prices = {
            "motorcycle": config.RENTAL_PRICES["motorcycle"],
            "car": config.RENTAL_PRICES["car"],
            "bus": config.RENTAL_PRICES["bus"],
            "truck": config.RENTAL_PRICES["truck"],
        }

        gross = (
            self.stats["motorcycle"] * prices["motorcycle"]
            + self.stats["car"] * prices["car"]
            + self.stats["bus"] * prices["bus"]
            + self.stats["truck"] * prices["truck"]
        )
        discount = gross * config.DAILY_CUSTOMER_DISCOUNT
        net = gross - discount

        self.gross_label.config(text=f"Rs. {gross:,}")
        self.discount_label.config(text=f"-Rs. {discount:,.0f}")
        self.net_label.config(text=f"Rs. {net:,.0f}")

    def update_fps(self, fps):
        self.fps_label.config(text=f"FPS: {fps:.1f}")
