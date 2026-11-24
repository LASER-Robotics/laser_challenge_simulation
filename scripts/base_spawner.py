#!/usr/bin/env python3

import os
import random
import yaml
import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity
from geometry_msgs.msg import Pose, Point, Quaternion

class BaseSpawner(Node):
    def __init__(self):
        super().__init__('base_spawner')
        self.client = self.create_client(SpawnEntity, '/spawn_entity')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        self.declare_parameter('challenge_stage', 'stage_one')
        self.declare_parameter('bases_spawn', '')

        self.pkg_share = get_package_share_directory('laser_challenge_simulation')

    def spawn(self, model_name, x, y, z, model_path):
        self.get_logger().info(f"Preparing to spawn model: {model_name} at ({x}, {y}, {z})")
        pose = Pose(position=Point(x=x, y=y, z=z), orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0))
        try:
            with open(model_path, "r") as model_file:
                model_xml = model_file.read()
        except FileNotFoundError:
            self.get_logger().error(f"Model file not found: {model_path}")
            return

        request = SpawnEntity.Request()
        request.name = model_name
        request.xml = model_xml
        request.initial_pose = pose
        request.robot_namespace = ""
        request.reference_frame = "world"

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info(f"Spawned {model_name} at position ({x}, {y}, {z})")
        else:
            self.get_logger().error(f"Failed to spawn model {model_name}: {future.exception()}")

    def generate_random_positions(self, num_bases, x_limits, y_limits, z_limits, min_distance):
        positions = []
        while len(positions) < num_bases:
            x = random.uniform(x_limits[0], x_limits[1])
            y = random.uniform(y_limits[0], y_limits[1])
            z = random.uniform(z_limits[0], z_limits[1])  # Gera um valor aleatório para Z
            collision = False
            for pos in positions:
                # Verifica a distância em 3D (X, Y, Z)
                distance = ((x - pos[0])**2 + (y - pos[1])**2 + (z - pos[2])**2)**0.5
                if distance < min_distance:
                    collision = True
                    break
            if not collision:
                positions.append((x, y, z))  # Adiciona a posição com Z aleatório
        return positions

    def spawn_bases(self, num_bases, x_limits, y_limits, z_limits, min_distance):
        positions = self.generate_random_positions(num_bases, x_limits, y_limits, z_limits, min_distance)
        for idx, (x, y, z) in enumerate(positions):
            model_name = f"base_{idx}"
            self.spawn(model_name, x, y, z, os.path.join(self.pkg_share, "models/landing_platform/model.sdf"))

def main(args=None):
    rclpy.init(args=args)
    base_spawner = BaseSpawner()
    
    pkg_share = base_spawner.pkg_share
    challenge_stage = base_spawner.get_parameter('challenge_stage').get_parameter_value().string_value

    # geral para todas as fases
    base_spawner.get_logger().info("Spawning cluttered environment...")
    base_spawner.spawn("cluttered_environment", -0.75, -1.0, 0.0, os.path.join(pkg_share, "models/cluttered_environment/model.sdf"))

    if challenge_stage == "stage_one":
        bases_spawn_file = base_spawner.get_parameter('bases_spawn').get_parameter_value().string_value
        if bases_spawn_file:
            base_spawner.get_logger().info(f"Loading fixed Stage 1 bases from YAML: {bases_spawn_file}")
            with open(bases_spawn_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            params = data.get('/**', data.get('/**/**:', data)).get('ros__parameters', {})
            flat = params.get('debug', {}).get('yaml_lps', []) or params.get('already_known_lps', [])
            for idx in range(len(flat) // 4):
                x, y, z = float(flat[4 * idx]), float(flat[4 * idx + 1]), float(flat[4 * idx + 2])
                # Use flat landing_platform when placed on top of cluttered_environment (x <= 1.35)
                if x <= 1.35:
                    model_sdf = "models/landing_platform/model.sdf"
                else:
                    model_sdf = "models/suspended_landing_platform/model.sdf"
                base_spawner.spawn(f"base_yaml_{idx}", x, y, z, os.path.join(pkg_share, model_sdf))
        else:
            # Limites para as 5 bases normais
            x_limits_normal = (1.75, 6.25)  # x entre 0.5 e 7.5
            y_limits_normal = (0, -6)  # y entre 0.5 e 6.0
            z_limits_normal = (0.0, 1.5)  # z aleatório entre 0.0 e 1.5

            # Limites para a base especial
            x_limits_special = (0.25, 0.75)  # x entre 0.5 e 6.0
            y_limits_special = (-1.5, -6)  # y entre 6.0 e 7.5
            z_fixed_special = 1.52          # z fixo em 1.5

            # Distância mínima entre as bases (1.0 metro para evitar colisões)
            min_distance = 2.0

            # Spawn das 5 bases normais
            base_spawner.get_logger().info("Spawning 5 bases normais...")
            positions_normal = base_spawner.generate_random_positions(
                5, x_limits_normal, y_limits_normal, z_limits_normal, min_distance
            )
            for idx, (x, y, z) in enumerate(positions_normal):
                model_name = f"base_normal_{idx}"
                base_spawner.spawn(model_name, x, y, z, os.path.join(pkg_share, "models/suspended_landing_platform/model.sdf"))

            # Spawn da base especial
            base_spawner.get_logger().info("Spawning 1 base especial...")
            x_special = random.uniform(x_limits_special[0], x_limits_special[1])
            y_special = random.uniform(y_limits_special[0], y_limits_special[1])
            z_special = z_fixed_special
            model_name = "base_especial"
            base_spawner.spawn(model_name, x_special, y_special, z_special, os.path.join(pkg_share, "models/landing_platform/model.sdf"))
    
    elif challenge_stage == "stage_two":
        # Limites para as 3 bases aleatórias
        x_limits_random = (1.75, 6.25)  # x entre 0.5 e 7.5
        y_limits_random = (0, -6)  # y entre -0.5 e -7.5
        z_limits_random = (0.0, 1.5)  # z aleatório entre 0.0 e 1.5

        # Posições fixas para as 3 bases especiais
        fixed_positions = [
            (0.25, -2.5, 1.52),  # Base fixa 1
            (0.25, -4.0, 1.52),  # Base fixa 2
            (0.25, -5.5, 1.52)   # Base fixa 3
        ]

        # Distância mínima entre as bases (1.0 metro para evitar colisões em X-Y)
        min_distance = 2.0

        # Spawn das 3 bases aleatórias
        base_spawner.get_logger().info("Spawning 3 bases aleatórias...")
        positions_random = base_spawner.generate_random_positions(
            3, x_limits_random, y_limits_random, z_limits_random, min_distance
        )
        for idx, (x, y, z) in enumerate(positions_random):
            model_name = f"base_random_{idx}"
            base_spawner.spawn(model_name, x, y, z, os.path.join(pkg_share, "models/suspended_landing_platform/model.sdf"))

        # Spawn das 3 bases fixas
        base_spawner.get_logger().info("Spawning 3 bases fixas...")
        for idx, (x, y, z) in enumerate(fixed_positions):
            model_name = f"base_fixa_{idx}"
            box_name = f"box_{idx}"
            base_spawner.spawn(model_name, x, y, z, os.path.join(pkg_share, "models/landing_platform/model.sdf"))
            base_spawner.spawn(box_name, x, y, z+0.3, os.path.join(pkg_share, "models/box/model.sdf"))

    elif challenge_stage == "stage_three": 
        # Limites para as 5 bases normais
        x_limits_normal = (1.75, 6.25)  # x entre 0.5 e 7.5
        y_limits_normal = (0, -6)  # y entre 0.5 e 6.0
        z_limits_normal = (0.1, 0.1)  # z aleatório entre 0.0 e 1.5

        # Limites para a base especial
        x_limits_special = (0.25, 0.75)  # x entre 0.5 e 6.0
        y_limits_special = (-1.5, -6)  # y entre 6.0 e 7.5
        z_fixed_special = 1.52          # z fixo em 1.5

        # Distância mínima entre as bases (1.0 metro para evitar colisões)
        min_distance = 2.0

        # Spawn das 5 bases normais
        base_spawner.get_logger().info("Spawning 5 bases normais...")
        positions_normal = base_spawner.generate_random_positions(
            5, x_limits_normal, y_limits_normal, z_limits_normal, min_distance
        )
        for idx, (x, y, z) in enumerate(positions_normal):
            model_name = f"base_normal_{idx}"
            base_spawner.spawn(model_name, x, y, z, os.path.join(pkg_share, "models/landing_platform/model.sdf"))

        # Spawn da base especial
        base_spawner.get_logger().info("Spawning 1 base especial...")
        x_special = random.uniform(x_limits_special[0], x_limits_special[1])
        y_special = random.uniform(y_limits_special[0], y_limits_special[1])
        z_special = z_fixed_special
        model_name = "base_especial"
        base_spawner.spawn(model_name, x_special, y_special, z_special, os.path.join(pkg_share, "models/landing_platform/model.sdf"))

    elif challenge_stage == "stage_four":
        # Posição fixa para a base da fase 4
        fixed_position = (3.0, -3.25, 0.1)  # Base fixa

        # Spawn da base fixa
        base_spawner.get_logger().info("Spawning 1 base fixa...")
        model_name = "base_fixa_fase4"
        base_spawner.spawn(model_name, fixed_position[0], fixed_position[1], fixed_position[2],
                           os.path.join(pkg_share, "models/landing_platform/model.sdf"))
        
        #spawn qr codes
        base_spawner.get_logger().info("Spawning QR Code A...")
        base_spawner.spawn("qr_code_a", -0.73, -2.0, 0.75, os.path.join(pkg_share, "models/qr_code_a/model.sdf"))
        base_spawner.get_logger().info("Spawning QR Code B...")
        base_spawner.spawn("qr_code_b", 1.23, -3.5, 0.75, os.path.join(pkg_share, "models/qr_code_b/model.sdf"))
        base_spawner.get_logger().info("Spawning QR Code C...")
        base_spawner.spawn("qr_code_c", 0.75, -4.01, 0.75, os.path.join(pkg_share, "models/qr_code_c/model.sdf"))
        base_spawner.get_logger().info("Spawning QR Code D...")
        base_spawner.spawn("qr_code_d", 0.75, -5.98, 0.75, os.path.join(pkg_share, "models/qr_code_d/model.sdf"))
        base_spawner.get_logger().info("Spawning QR Code E...")
        base_spawner.spawn("qr_code_e", 0.25, -6.98, 0.75, os.path.join(pkg_share, "models/qr_code_e/model.sdf"))

    rclpy.spin(base_spawner)
    base_spawner.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
